from db.db_base import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
import json
from sqlalchemy import Column, DateTime, func, JSON, String
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import func

class Report(Base):
    __tablename__ = 'report'
    id = Column(String, primary_key=True, index=True)
    report = Column(String, nullable=True)
    inference_path = Column(String, nullable=True)
    annotation_path = Column(String, nullable=True)
    is_deleted = Column(Boolean(), default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=datetime.now)
    patient_id = Column(String, ForeignKey("patient.id"))
    patient = relationship("Patient", back_populates="report")


class Patient(Base):
    __tablename__ = 'patient'
    id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=datetime.now)
    is_deleted = Column(Boolean(), default=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="patient_records")
    report = relationship("Report", back_populates="patient")




class OrthancModel(Base):
    __tablename__ = 'orthanc'
    ID = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=datetime.now)
    ParentPatient = Column(String, nullable=True)
    ParentSeries = Column(String, nullable=True)
    ParentStudy = Column(String, nullable=True)
    Path = Column(String, nullable=True)
    results = Column(JSON, nullable=True)



class DeletePatientObject(Base):
    __tablename__ = 'deleted_patient_objects'
    id = Column(String, primary_key=True, index=True)
    deleted_at = Column(DateTime, server_default=func.now())
    deleted_patient_id = Column(String, ForeignKey("patient.id"), unique=True)


class DeleteReportObject(Base):
    __tablename__ = 'deleted_reports_objects'
    id = Column(String, primary_key=True, index=True)
    deleted_at = Column(DateTime, server_default=func.now())
    deleted_report_id = Column(String, ForeignKey("report.id"), unique=True)






    # id---2 (db_id and docker_id. report-->string)
    # get id later and updated report..


### Diagonistic Report...
# - after inference..
#     - string, doctor,
#
# ### Save patient Details.
#     - Patient object.-> upload image.
#     - create patient()
