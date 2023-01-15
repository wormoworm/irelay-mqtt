class HttpConfig:
    """Contains config data used when publishing data via HTTP."""

    def __init__(self, endpoint: str, ispindel_paths: dict, nautilis_path: str, min_publication_interval_s: int) -> None:
        self.endpoint = endpoint
        self.ispindel_paths = ispindel_paths
        self.nautilis_path = nautilis_path
        self.min_publication_interval_s = min_publication_interval_s

    
    def get_endpoint_url_with_protocol(self, https: bool):
        return ("https://" if https else "http://") + self.endpoint

    def get_ispindel_path(self, channel: int) -> str:
        return self.ispindel_paths.get(str(channel))


    def get_ispindel_url(self, channel: int, https: bool = False) -> str:
        path = self.get_ispindel_path(channel)
        if path:
            return self.get_endpoint_url_with_protocol(https) + path
        else:
            return None


    def get_nautilis_url(self, https: bool = True) -> str:
        return self.get_endpoint_url_with_protocol(https) + self.nautilis_path