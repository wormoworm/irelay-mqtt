from pydantic import BaseModel


class NautilisReport(BaseModel):
    temperature: float
    unit: str
    token: str


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
            name = "iRelay",    # TODO: Make this configurable?
            aux_temp = nautilis_report.temperature,
            temp_unit = "C" if nautilis_report.unit == "celsius" else "F" ) # TODO: Use an enum to make this smarter?