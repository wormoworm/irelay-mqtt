# iRelay-MQTT API

# What is it?
A service that listens for HTTP requests sent by the iRelay, and re-publishes them on a set of MQTT topics.

# How does it work?
It runs as a Docker container, inside which there is a Uvicorn server that invokes a Python FastAPI instance. All HTTP requests from the iRelay hit this server, and any supported ones are handled. Unsupported requests are simply ignored.

# Does it support multiple iSpindels?
Yes. As with the iRelay, up to two iSpindels are supported.

# Aha, so could I use this to publish data from multiple iSpindels to services where the iRelay currently only supports one iSpindel?
Yes, for example you could use this tool (in combination with the [publisher](README-publisher.md) to publish data from two iSpindels to Grainfather. See the <TODO> section below for details.

# Can I choose what topics data are published to?
Yes, you have full control over topics that the service publishes data to. Currently there are three topics:
1. iSpindel channel 1.
1. iSpindel channel 2.
1. iRelay internal data (for the temperature readings from the iRelay's built-in thermometer).

# Anything else I should know?
- irelay-mqtt will also calculate the battery percentage from the raw reading in volts. This is to make things easier when you come to consume the data in whatever service you choose. This calculation uses 3.0V and 4.1V as the the minimum and maximum voltages respectively.

# OK this sounds great. How do I set this up?
## 1. Run the container
I prefer to use `docker-compose` to run containers.
```yaml
version: "2.2"
services:
  irelay-mqtt:
    image: tomhomewood/irelay-mqtt:latest
    container_name: irelay-mqtt
    restart: unless-stopped
    environment:
      - MQTT_ENDPOINT=<broker_address_or_hostname>
      - MQTT_PORT=<broker_port>
      - MQTT_CLIENT_ID=irelay_mqtt
      - MQTT_USERNAME=<username>
      - MQTT_PASSWORD=<password>
      - GRAVITY_OFFSET_ISPINDEL_CHANNEL_1=-.006
      - ROUND_VALUES=true
    cpu_count: 2
    mem_limit: 256m
    network_mode: "host"
```
_Note: You will also need to either run this container in "host mode" (i.e. not behind a docker network) on a host that has port 80 available, or use a reverse proxy such as Nginx or Traefik to deliver the requests to the container._
## 2. Intercept HTTP data
The iRelay must be configured to send data to the iRelay. Since there is no dedicated "custom HTTP" service option in the configuration options, we must do a little trickery. We will pretend to be `brey-spy.com` to do this.
1. Login to the iRelay via its Wi-Fi network. In the configuration page, set the service to Brew-Spy, click save and then set the custom sensor URL to `api/nautilis`. The iRelay will now publish iSpindel data to `brey-spy.com/api/ispindel` and iRelay data to `brew-spy.com/api/nautilis`.
1. Configure the DNS server in your network to return the address of the machine irelay-mqtt is running on when the iRelay asks for `brew-spy.com`. How this is configured will vary according to your DNS server:
    - Some consumer routers offer some sort of "custom DNS" option that allows you to add custom DNS entries.
    - Pi-Hole allows the addition of "Local DNS Records". This is the option I went with, as I already run a Pi-Hole.


# Example Docker compose file
 See the `irelay-mqtt` service in the [provided compose file](/docker/docker-compose-example.yml) for an example.


Note that to use this server, you will need to add a manual DNS entry or hostname mapping in your network's router or DNS server. 

# Configuration options
Below is a full a list of the configuration options that can be set via environment variables:
- `MQTT_ENDPOINT`: Address or hostname of your MQTT broker.
- `MQTT_PORT`: MQTT port the broker is running on.
- `MQTT_CLIENT_ID`: A (unique name) that identifies this service to the MQTT broker.
- `MQTT_USERNAME`: Username for connecting to MQTT.
- `MQTT_PASSWORD`: Password for connecting to MQTT.
- `MQTT_TOPIC_ISPINDEL_CHANNEL_1`: TODO (and in code)
- `MQTT_TOPIC_ISPINDEL_CHANNEL_2`: TODO
- `MQTT_TOPIC_ISPINDEL_NAUTILIS`: TODO
- `GRAVITY_OFFSET_ISPINDEL_CHANNEL_1`: Gravity offset to apply to readings for the iSpindel reporting on channel 1. This is provided because if you set an offset on the iRelay, it is only applied to the number shown on the screen, not the values transmitted to the destination web srvice. This option allows you to adjust the transmitted values by the same amount, so the data will match what's shown on the iRelay's screen.
- `GRAVITY_OFFSET_ISPINDEL_CHANNEL_2`: Gravity offset to apply to readings for the iSpindel reporting on channel 2.
- `ROUND_VALUES`: Whether or not the values published to MQTT should be rounded. Rounding is as follows:
    - Battery percentage, angle and temperature: 1DP.
    - Battery voltage: 3DP.
    - Gravity: 4DP. Initially I made this 3DP, but looking at the raw data it's clear that the iSpindel is good for another digit of precision.