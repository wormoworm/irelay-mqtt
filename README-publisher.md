# iRelay-MQTT Publisher

# What is it?
A service that listens subscribes to the MQTT topics that the iRelay-MQTT API publishes to, and re-publishes any received messages to an HTTP destination of your choice.

# How does it work?
It runs as a Docker container, but does not need any network jiggery-pokery to get it to work.

# Does it support multiple iSpindels?
Yes, as with the iRelay, up to two iSpindels are supported. In addition, data from multiple iSpindels may be sent to services like Grainfather, where the iRelay currently only supports one iSpindel.

# What services does it support?
The following services are supported:
- Brewfather.
- Grainfather.
If you need support for another service, let me know by filing a GitHub issue and I'll take a look.

# Can I publish to multiple services?
Yes, for example you could use two instances (i.e. two containers running in parallel) to publish the same data to Grainfather and Brewfather simultaneously. You would accomplish this by doing the following:
1. Define two services in your Docker compose file, giving them unique names (e.g. `irelay-publisher-grainfather` and `irelay-publisher-brewfather`)
1. Give each publisher container a unique client ID, using the `MQTT_CLIENT_ID` environment variable.
1. Set the destination for each publisher using the `HTTP_DESTINATION_SERVICE` environment variable.
1. Run the compose file as normal.

 By using the MQTT topic environment variables and multiple publishers, you could also create more exotic combinations, such as sending data from iSpindel 1 to one service, and the data from iSpindel 2 to another.

 # How do I set this up?
 All you need to do is run the container and configure it to match your setup. I prefer to use `docker-compose` to run containers:
```yaml
version: "2.2"
services:
  irelay-mqtt-publisher:
    image: tomhomewood/irelay-mqtt-publisher:latest
    container_name: irelay-mqtt-publisher
    restart: unless-stopped
    environment:
      - MQTT_ENDPOINT=<broker_address_or_hostname>
      - MQTT_PORT=<broker_port>
      - MQTT_CLIENT_ID=irelay_mqtt_publisher
      - MQTT_USERNAME=<username>
      - MQTT_PASSWORD=<password>
      - TOPIC_FORMAT_ISPINDEL_REPORT=devices/ispindel/channel/{}/data
      - TOPIC_IRELAY_REPORT=devices/irelay/data
      - HTTP_DESTINATION_SERVICE=grainfather
      - HTTP_ENDPOINT=community.grainfather.com
      - HTTP_PATH_ISPINDEL_CHANNEL_1=<ispindel_data_path>
      - HTTP_PATH_IRELAY=<custom_data_path>
    network_mode: "host"
```
A full compose file for both tools can be found [here](/docker/docker-compose-example.yml).
    

 # Configuration options
Below is a full a list of the configuration options that can be set via environment variables:
- `MQTT_ENDPOINT`: Address or hostname of your MQTT broker.
- `MQTT_PORT`: MQTT port the broker is running on.
- `MQTT_CLIENT_ID`: A (unique name) that identifies this service to the MQTT broker.
- `MQTT_USERNAME`: Username for connecting to MQTT.
- `MQTT_PASSWORD`: Password for connecting to MQTT.
- `TOPIC_FORMAT_ISPINDEL_REPORT`: MQTT topic format for receiving iSpindel data. This should be a pre-formatted Python string that contains one (and only one) variable placeholder. This placeholder will be substituted with the channel number when subscribing to data updates. For example, providing the topic format `devices/ispindel/{}/data` will result in data from iSpindel channel 1 being received on `devices/ispindel/1/data`.
- `MQTT_TOPIC_IRELAY`REPORT`: Topic for receiving iRelay data.
- `HTTP_ENDPOINT`: Base endpoint to publish data to (e.g. `community.grainfather.com` for Grainfather).
- `HTTP_PATH_ISPINDEL_CHANNEL_1`: API path to send data to for iSpindel channel 1. This will be different for each service, - see the instructions provided by your service for setting up an iSpindel.
- `HTTP_PATH_ISPINDEL_CHANNEL_1`: API path to send data to for iSpindel channel 2.
- `HTTP_PATH_IRELAY`: API path to send data to for iRelay data. This is often referred to by services like Brewfather as a "Custom Stream". See the instructions provided by your service for setting this up.
- `HTTP_MIN_PUBLICATION_INTERVAL`: Most web services enforce limits on how often you can publish data. This option allows you to define the minimum time between updates in seconds. Defaults to 900 (15 minutes). If you like, you can take advantage of this setting by having your iRelay publish every 5 minutes, intercepting this data using the iRelay-MQTT API, then setting this option to 900. This would give you the best of both worlds - 5-minute data delivered to any clients subscribed via MQTT, and 15-minute data reported to your web service.
- `HTTP_DESTINATION_SERVICE`: The type of service you wish to publish data to. Primarily used to determine what format custom data for the iRelay should be published in. Must be one of the following:
  - `brewfather`
  - `grainfather`