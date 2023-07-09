from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from sqlalchemy.orm import Session
from datetime import datetime
from crud.base import CRUDBase
from model.inference import Patient, Report, DeleteReportObject, DeletePatientObject, OrthancModel
from schemas.patient import PatientCreate, PatientUpdate, ReportCreate, ReportUpdate, OrthancBase, OrthancCreate
import json

from db.db_base import Base

ModelType = TypeVar("ModelType", bound=Base)



class CRUDDeletePatient(CRUDBase[DeletePatientObject, PatientCreate, PatientUpdate]):
    def create(self, db: Session, *, obj_in: PatientCreate) -> DeletePatientObject:
        db_obj = DeletePatientObject(
            id=obj_in.get('id'),
            deleted_patient_id = obj_in.get('patient_id'),
            deleted_at= obj_in.get('deleted_at')
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_patient(self, db: Session, id: Any) -> Optional[ModelType]:
        try:
            return db.query(self.model).filter(self.model.deleted_patient_id == id).first()
        except Exception as e:
            return db.query(self.model).filter(self.model.deleted_patient_id == id).first()



class CRUDDeleteReport(CRUDBase[DeleteReportObject, ReportCreate, ReportUpdate]):
    def create(self, db: Session, *, obj_in: ReportCreate) -> DeleteReportObject:
        db_obj = DeleteReportObject(
            id=obj_in.get('id'),
            deleted_report_id = obj_in.get('report_id'),
            deleted_at= obj_in.get('deleted_at')
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_report(self, db: Session, id: Any) -> Optional[ModelType]:
        try:
            return db.query(self.model).filter(self.model.deleted_report_id == id).first()
        except Exception as e:
            return db.query(self.model).filter(self.model.deleted_report_id == id).first()


class CRUDPatient(CRUDBase[Patient, PatientCreate, PatientUpdate]):
    def create(self, db: Session, *, obj_in: PatientCreate) -> Patient:
        db_obj = Patient(
            id=obj_in.get('id'),
            user_id = obj_in.get('user_id'),
            created_at= obj_in.get('created_at'),
            updated_at= obj_in.get('updated_at')
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_user_id(self, db: Session, *, user_id: Any) -> Optional[Patient]:
        return db.query(Patient).filter(Patient.user_id == user_id, Patient.is_deleted==False).all()

    def update(
        self, db: Session, *, db_obj: Report, obj_in: Union[PatientUpdate, Dict[str, Any]]
    ) -> Patient:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        if update_data.get('is_deleted', None):
            update_data['is_deleted'] = update_data["is_deleted"]
        return super().update(db, db_obj=db_obj, obj_in=update_data)



class CRUDReport(CRUDBase[Report, ReportCreate, ReportUpdate]):
    def create(self, db: Session, *, obj_in: ReportCreate) -> Report:
        db_obj = Report(
            id=obj_in.get('id'),
            patient_id=obj_in.get('patient_id'),
            created_at= obj_in.get('created_at'),
            updated_at= obj_in.get('updated_at'),
            annotation_path = obj_in.get("annotation_path"),
            inference_path = obj_in.get("inference_path"),
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


    def update(
        self, db: Session, *, db_obj: Report, obj_in: Union[ReportUpdate, Dict[str, Any]]
    ) -> Report:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("report", None):
            update_data["report"] = update_data["report"]
            update_data['updated_at'] = datetime.now()
        if update_data.get('is_deleted'):
            update_data['is_deleted'] = update_data["is_deleted"]
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    # def delete_update(
    #     self, db: Session, *, db_obj: Report, obj_in: Union[ReportUpdate, Dict[str, Any]]
    # ) -> Report:
    #     if isinstance(obj_in, dict):
    #         update_data = obj_in
    #     else:
    #         update_data = obj_in.dict(exclude_unset=True)
    #     if update_data["is_deleted"]:
    #         update_data['is_deleted'] = update_data["is_deleted"]
    #     return super().update(db, db_obj=db_obj, obj_in=update_data)


class CRUDOrthanc(CRUDBase[OrthancModel, OrthancCreate, OrthancBase]):
    def create(self, db: Session, *, obj_in: OrthancCreate) -> OrthancBase:

        db_obj = OrthancModel(
            ID=obj_in.get('ID'),
            ParentPatient= obj_in.get('ParentPatient'),
            ParentSeries= obj_in.get('ParentSeries'),
            ParentStudy= obj_in.get('ParentStudy'),
            Path= obj_in.get('Path'),
            results= json.dumps(obj_in.get('results')),
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_data_id(self, db: Session, *, ID: Any) -> Optional[OrthancBase]:
        return db.query(OrthancModel).filter(OrthancModel.ID == ID).all()

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        try:
            return db.query(OrthancModel).filter(OrthancModel.ID == id).first()
        except Exception as e:
            return db.query(OrthancModel).filter(OrthancModel.ID == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        try:
            return db.query(OrthancModel).filter(OrthancModel).offset(skip).limit(limit).all()
        except Exception as e:
            return db.query(OrthancModel).offset(skip).limit(limit).all()


patient = CRUDPatient(Patient)
orthankSaver = CRUDOrthanc(CRUDOrthanc)
report = CRUDReport(Report)
patient_delete = CRUDDeletePatient(DeletePatientObject)
report_delete = CRUDDeleteReport(DeleteReportObject)
