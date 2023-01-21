# iRelay-MQTT Publisher

# What is it?
A service that listens subscribes to the MQTT topics that the API publishes to, and re-publishes any received messages to an HTTP destination of your choice.

# How does it work?
It runs as a Docker container, but does not need any network jiggery-pokery to get it to work. When a 

# Does it support multiple iSpindels?
Yes, as with the iRelay, up to two iSpindels are supported. In addition, data from multiple iSpindels may be sent to services like Grainfather, where the iRelay currently only supports one iSpindel.

# Can I publish to multiple services?
Yes, for example you could use two instances (i.e. two containers running in parallel) to publish the same data to Grainfather and Brewfather simultaneously. You would accomplish this by doing the following:
1. Define two services in your Docker compose file, giving them unique names (e.g. `irelay-publisher-grainfather` and `irelay-publisher-brewfather`)
1. Give each publisher container a unique client ID, using the `MQTT_CLIENT_ID` environment variable.
1. Set the destination for each publisher using the `HTTP_DESTINATION_SERVICE` environment variable.
1. Run the compose file as normal.

 By using the MQTT topic environment variables and multiple publishers, you could also create more exotic combinations, such as sending data from iSpindel 1 to one service, and the data from iSpindel 2 to another.