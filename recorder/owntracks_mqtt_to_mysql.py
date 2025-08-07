import paho.mqtt.client as mqtt
import json
import mysql.connector
from mysql.connector import Error
import os

# MQTT Configuration
MQTT_BROKER = os.environ.get('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.environ.get('MQTT_PORT', 1883))
MQTT_USERNAME = os.environ.get('MQTT_USERNAME', '')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD', '')
MQTT_TOPIC = "owntracks/+/+"

# MySQL Configuration
MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_USER = os.environ.get('MYSQL_USER', 'youruser')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'yourpassword')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'owntracksdb')

def on_connect(client, userdata, flags, rc):
    """Callback for when the client receives a CONNACK response from the server."""
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    """Callback for when a PUBLISH message is received from the server."""
    try:
        payload = json.loads(msg.payload)
        if 'lat' in payload and 'lon' in payload and payload.get('_type', '') == 'location':
            user, device = msg.topic.split('/')[1:]
            insert_location(user, device, payload)
    except json.JSONDecodeError:
        print("Received message was not JSON")

def insert_location(user, device, payload):
    """Insert all location data into MySQL."""
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create table if not exists
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS `locations` (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                `user` VARCHAR(255),
                `device` VARCHAR(255),
                `timestamp` BIGINT,
                `lat` FLOAT,
                `lon` FLOAT,
                `t` TEXT,
                `acc` INT,
                `batt` INT,
                `conn` VARCHAR(255),
                `vel` FLOAT,
                `alt` INT,
                `trigger` VARCHAR(255),
                `tid` VARCHAR(255),
                `cog` FLOAT,
                `m` TEXT,
                `vac` INT,
                `p` DATETIME,
                `ssid` VARCHAR(255),
                `bs` INT,
                `event` VARCHAR(255),
                `inregions` TEXT
            )
            ''')
            
            # Prepare data for insertion
            data = {
                '`user`': user,
                '`device`': device,
                '`timestamp`': payload.get('tst', None),
                '`lat`': payload.get('lat', None),
                '`lon`': payload.get('lon', None),
                '`t`': json.dumps(payload.get('t', {})),
                '`acc`': payload.get('acc', None),
                '`batt`': payload.get('batt', None),
                '`conn`': payload.get('conn', None),
                '`vel`': payload.get('vel', None),
                '`alt`': payload.get('alt', None),
                '`trigger`': payload.get('t', {}) if isinstance(payload.get('t'), dict) else None,
                '`tid`': payload.get('tid', None),
                '`cog`': payload.get('cog', None),
                '`m`': json.dumps(payload.get('m', {})),
                '`vac`': payload.get('vac', None),
                '`p`': payload.get('p', None),
                '`ssid`': payload.get('SSID', None),
                '`bs`': payload.get('bs', None),
                '`event`': payload.get('event', None),
                '`inregions`': json.dumps(payload.get('inregions', []))
            }
            
            # Insert all available data
            fields = ', '.join(data.keys())
            # fields = '`user`, `device`, `timestamp`, `lat`, `lon`, `t`, `acc`, `batt`, `conn`, `vel`, `alt`, `trigger`, `tid`, `cog`, `m`, `vac`, `p`, `ssid`, `bs`, `event`'
            placeholders = ', '.join(['%s'] * len(data))
            query = f"INSERT INTO locations ({fields}) VALUES ({placeholders})"
            cursor.execute(query, list(data.values()))
            
            connection.commit()
            print(f"Location data inserted for user: {user}, device: {device} - {placeholders}")
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Initialize MQTT Client
client = mqtt.Client()
client.username_pw_set(username=MQTT_USERNAME, password=MQTT_PASSWORD)
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT Broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Start the loop
client.loop_forever()
