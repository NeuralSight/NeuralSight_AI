from pydantic import BaseModel
from typing import Optional

class PatientBase(BaseModel):
    id: str


class PatientCreate(PatientBase):
    pass


class PatientUpdate(PatientBase):
    id: Optional[str] = None


# report

class ReportBase(BaseModel):
    id: str
    patient_id: str
    report: Optional[str]  = None


class ReportCreate(PatientBase):
    pass


class ReportUpdate(PatientBase):
    report: Optional[str] = None
