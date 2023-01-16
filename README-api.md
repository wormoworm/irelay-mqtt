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

# OK this sounds great. How do I set this up?


 and an [example configuration](/docker/docker-compose-example.yml) is provided. Note that to use this server, you will need to add a manual DNS entry or hostname mapping in your network's router or DNS server. You will also need to either run this container on a host that has port 80 available, or use a reverse proxy such as Nginx or Traefik to deliver the requests to the container.