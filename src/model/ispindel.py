from pydantic import BaseModel

ISPINDEL_BATTERY_MIN = 3.0
ISPINDEL_BATTERY_MAX = 4.1


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


class ExtendedIspindelReport(IspindelReport):

    battery_percentage: float


    def __init__(self, original_report: IspindelReport):
        # This is rather verbose, but I can't think of a better way to copy the values in from the other Pydantic object.
        super().__init__(
            ID = original_report.ID,
            name = original_report.name,
            RSSI = original_report.RSSI,
            battery = original_report.battery,
            interval = original_report.interval,
            angle = original_report.angle,
            gravity = original_report.gravity,
            temperature = original_report.temperature,
            temp_units = original_report.temp_units,
            battery_percentage = self._calculate_battery_percentage(original_report.battery)
        )
    

    def _calculate_battery_percentage(self, battery_voltage) -> float:
        percentage_raw = ((battery_voltage - ISPINDEL_BATTERY_MIN) / (ISPINDEL_BATTERY_MAX - ISPINDEL_BATTERY_MIN)) * 100
        return min(max(0, percentage_raw), 100)