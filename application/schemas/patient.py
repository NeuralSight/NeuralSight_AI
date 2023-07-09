from pydantic import BaseModel
from typing import Optional
from typing import Optional, Dict, Any, List, Union


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




# Orthanck saved.....
class OrthancBase(BaseModel):
    ID: str
    ParentPatient: Optional[str] = None
    ParentSeries: Optional[str] = None
    ParentStudy: Optional[str] = None
    Path: Optional[str] = None
    results: Optional[Dict[str, Any]] = None


class OrthancBaseOptional(BaseModel):
    ID: str
    ParentPatient: Optional[str] = None
    ParentSeries: Optional[str] = None
    ParentStudy: Optional[str] = None
    Path: Optional[str] = None
    results: Optional[Any] = None

class OrthancCreate(OrthancBase):
    pass
