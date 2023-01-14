from pydantic import BaseModel


class IspindelReport(BaseModel):
    ID: int
    name: str
    RSSI: int
    battery: float
    interval: int
    angle: float
    gravity: float
    temperature: float
    temp_units: str

    def get_channel_number(self) -> int:
        if self.name[0] == '1':
            return 1
        elif self.name[0] == '2':
            return 2
        else:
            return None