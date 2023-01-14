from pydantic import BaseModel


class NautilisReport(BaseModel):
    temperature: float
    unit: str
    specific_gravity: float