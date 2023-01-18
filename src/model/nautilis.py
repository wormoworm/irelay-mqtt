from pydantic import BaseModel


class NautilisReport(BaseModel):
    temperature: float
    unit: str
    token: str