from enum import Enum

class Destination(Enum):
    GRAINFATHER = "grainfather"
    BREWFATHER = "brewfather"

    def from_string(value: str):
        if value:
            for destination in Destination:
                if destination.value.lower() == value.lower():
                    return destination
        return None