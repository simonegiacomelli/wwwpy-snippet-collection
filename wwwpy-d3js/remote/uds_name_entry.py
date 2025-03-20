from pydantic import BaseModel


class Validated(BaseModel):
    class Config:
        validate_assignment = True


class UdsNameEntry(Validated):
    name: str
    enabled: bool
