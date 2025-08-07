#!/bin/sh

MQTT_SERVER="mqtt.domain.tld"
MQTT_PORT="1883"
MQTT_USER="user"
MQTT_PASSWORD="password"

MYSQL_SERVER="mysql.domain.tld"
MYSQL_SCHEMA="owntracks"
MYSQL_USER="user"
MYSQL_PASSWORD="password"

docker build -t owntracks-mqtt-mysql .

docker run \
  --name owntracks-mqtt-container \
  --restart=always \
  -e MQTT_BROKER=$MQTT_SERVER \
  -e MQTT_PORT=$MQTT_PORT \
  -e MQTT_USERNAME=$MQTT_USER \
  -e MQTT_PASSWORD=$MQTT_PASSWORD \
  -e MYSQL_HOST=$MYSQL_SERVER \
  -e MYSQL_USER=$MYSQL_USER \
  -e MYSQL_PASSWORD=$MYSQL_PASSWORD \
  -e MYSQL_DATABASE=$MYSQL_SCHEMA \
  owntracks-mqtt-mysql
