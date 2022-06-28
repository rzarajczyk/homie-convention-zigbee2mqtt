import json
import logging

import paho.mqtt.client as mqtt
from bootstrap.bootstrap import start_service
from homie_helpers import FloatProperty, Homie, Node, MqttSettings, create_homie_id

config, logger, timezone = start_service()

MQTT_HOST = config['mqtt']['broker']
MQTT_PORT = config['mqtt']['port']
MQTT_USER = config['mqtt']['username']
MQTT_PASS = config['mqtt']['password']

HOMIE_MQTT_SETTINGS = MqttSettings.from_dict(config['mqtt'])

LOGGER = logging.getLogger("main")
LOGGER.info("Starting application!")

DEVICES = {}


def on_connect(client, userdata, flags, rc):
    LOGGER.info("Connected with result code %s" % str(rc))
    client.subscribe("zigbee2mqtt/#")


def read_devices(devices_definition):
    parsed_payload = json.loads(devices_definition)
    for device_definition in parsed_payload:
        if device_definition['definition'] is not None:
            device_id = create_homie_id(device_definition['friendly_name'])
            device_name = device_definition['definition']['description']
            properties = []
            for property_definition in device_definition['definition']['exposes']:
                property_id = create_homie_id(property_definition['name'])
                property_name = property_definition['description']
                property_unit = property_definition['unit']
                property_type = property_definition['type']
                if property_type == 'numeric':
                    property = FloatProperty(property_id, name=property_name, unit=property_unit)
                    properties.append(property)
                else:
                    logger.error(f'Unsupported property type: {property_type} of device {device_id}')
            device = Homie(HOMIE_MQTT_SETTINGS, device_id, device_name, nodes=[
                Node("status", properties=properties)
            ])
            DEVICES[device_id] = device
            logger.info(f'Registering device {device_id}: {device}')


def read_values(payload):
    parsed_payload = json.loads(payload)
    device_id = create_homie_id(parsed_payload['device']['friendlyName'])
    device = DEVICES[device_id]
    print(device)
    for property_id in parsed_payload.keys():
        if property_id != 'device':
            value = parsed_payload[property_id]
            homie_property_id = create_homie_id(property_id)
            device[homie_property_id] = value


def on_message(client, userdata, msg):
    topic: str = msg.topic
    payload = msg.payload.decode(encoding='UTF-8')
    if topic == 'zigbee2mqtt/bridge/devices' and len(DEVICES) == 0:
        read_devices(payload)
    elif not topic.startswith('zigbee2mqtt/bridge'):
        logger.info(f'on {topic} => {payload}')
        read_values(payload)


client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_HOST, MQTT_PORT)

client.loop_forever()
