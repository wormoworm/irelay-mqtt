from pydantic import BaseModel
from enum import Enum
import os

class TemperatureUnit(str, Enum):
    Celsius = "celsius"
    Fahrenheit = "fahrenheit"

    def short_value(self) -> str:
        if self == TemperatureUnit.Celsius:
            return "C"
        elif self == TemperatureUnit.Fahrenheit:
            return "F"


class IrelayReport(BaseModel):
    temperature: float
    unit: TemperatureUnit
    token: str

    class Config:
        use_enum_values = True


class IrelayReportGrainfather(BaseModel):
    specific_gravity: float = 0.0
    temperature: float
    unit: str

    def __init__(self, irelay_report: IrelayReport):
        super().__init__(
            specific_gravity = 0,
            temperature = irelay_report.temperature,
            unit = irelay_report.unit)


class IrelayReportBrewfather(BaseModel):
    name: str
    aux_temp: float
    temp_unit: str

    def __init__(self, irelay_report: IrelayReport):
        super().__init__(
            name = os.getenv("IRELAY_NAME", default = "iRelay"),
            aux_temp = irelay_report.temperature,
            temp_unit = TemperatureUnit(irelay_report.unit).short_value())