from pydantic import BaseModel

class TemperatureResponse(BaseModel):
    latitude: float
    longitude: float
    temperature: float
    unit: str
