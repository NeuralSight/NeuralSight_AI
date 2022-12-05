from pydantic import BaseModel
from typing import Optional

class PatientBase(BaseModel):
    id: str
    patient_id: str
    report: Optional[str]  = None


class PatientCreate(PatientBase):
    pass


class PatientUpdate(PatientBase):
    report: Optional[str] = None
