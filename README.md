# iRelay-MQTT

## What is it?
A set of services for capturing data from a Nautilis iRelay brew tracking device.

## Why is it?
Whilst an iSpindel supports publishing data to an arbitrary location using either HTTP or MQTT, the Nautilis iRelay currently does not. Whilst the developer is aware of the need for this and plans to add this functionality in the future, I needed a quick fix to meet my needs, so I made this.

# What does it do?
Two services are provided:
1. [An HTTP server](/README-api.md) that listens for HTTP requests sent by the iRelay, and re-publishes them on a set of MQTT topics. This runs as a Docker container, and an [example configuration](/docker/docker-compose-example.yml) is provided. Note that to use this server, you will need to add a manual DNS entry or hostname mapping in your network's router or DNS server. You will also need to either run this container on a host that has port 80 available, or use a reverse proxy such as Nginx or Traefik to deliver the requests to the container.
1. [A publisher](/README-publisher.md) that subscribes to the topics mentioned above, and re-publishes any received messages to an HTTP destination of your choice. This is also run using a Docker, but does not need any network jiggery-pokery to get it to work.

# Why is this useful?
There are two ways in which you can use these tools:
1. By using only the HTTP server, you can capture all data sent from the iRelay and publish it to an MQTT broker. It is then up to you what you do with the data. For example, you might choose to consume it in Home Assistant.
2. In addition, by also using the publisher, you can forward any captured data to another party service that accepts data via HTTP. In this way, you can have your cake and eat it - the iRelay data gets published to the service of your choice (Brewfather, Grainfather, or any other non-paternal brewing management service), and you get access to it via MQTT.

# How do I set this up?
Refer to the [HTTP server](/README-api.md) and [publisher](/README-publisher.md) READMEs for instructions on how to set up each tool.
The basic pre-requisites you'll need are:
- Docker running on the server that will be running the services.
- The ability to forward HTTP data from the iRelay to the server. I personally use a local DNS record in my Pi-Hole config to achieve this, but you might be able to do this on a decent consumer router instead.