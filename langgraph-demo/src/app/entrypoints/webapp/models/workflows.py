from pydantic import BaseModel


class LGQuery(BaseModel):
    result: str
