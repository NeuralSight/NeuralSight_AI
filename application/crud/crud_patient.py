

from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from crud.base import CRUDBase
from model.inference import Patient
from schemas.patient import PatientCreate, PatientUpdate




class CRUDPatient(CRUDBase[Patient, PatientCreate, PatientUpdate]):
    def create(self, db: Session, *, obj_in: PatientCreate) -> Patient:
        print("Object in is  ", obj_in)
        db_obj = Patient(
            id=obj_in.get('id'),
            patient_id=obj_in.get('patient_id'),
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: Patient, obj_in: Union[PatientUpdate, Dict[str, Any]]
    ) -> Patient:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data["report"]:
            update_data["report"] = update_data["report"]
        return super().update(db, db_obj=db_obj, obj_in=update_data)



patient = CRUDPatient(Patient)
