class MqttConfig:
    """Contains config data used to connect to MQTT."""

    def __init__(self, endpoint: str, port: int, client_id: str, username: str, password: str) -> None:
        self.endpoint = endpoint
        self.port = port
        self.client_id = client_id
        self.username = username
        self.password = password