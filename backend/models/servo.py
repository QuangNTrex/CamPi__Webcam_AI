from pydantic import BaseModel

class ServoRequest(BaseModel):
    angle: int