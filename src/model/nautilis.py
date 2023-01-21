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


class NautilisReport(BaseModel):
    temperature: float
    unit: TemperatureUnit
    token: str

    class Config:
        use_enum_values = True


class NautilisReportGrainfather(BaseModel):
    specific_gravity: float = 0.0
    temperature: float
    unit: str

    def __init__(self, nautilis_report: NautilisReport):
        super().__init__(
            specific_gravity = 0,
            temperature = nautilis_report.temperature,
            unit = nautilis_report.unit)


class NautilisReportBrewfather(BaseModel):
    name: str
    aux_temp: float
    temp_unit: str

    def __init__(self, nautilis_report: NautilisReport):
        super().__init__(
            name = os.getenv("IRELAY_NAME", default = "iRelay"),
            aux_temp = nautilis_report.temperature,
            temp_unit = TemperatureUnit(nautilis_report.unit).short_value())