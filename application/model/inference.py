from db.db_base import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import func

class Report(Base):
    __tablename__ = 'report'
    id = Column(String, primary_key=True, index=True)
    report = Column(String, nullable=True)
    inference_path = Column(String, nullable=True)
    annotation_path = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=datetime.now)
    patient_id = Column(String, ForeignKey("patient.id"))
    patient = relationship("Patient", back_populates="report")


class Patient(Base):
    __tablename__ = 'patient'
    id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=datetime.now)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="patient_records")
    report = relationship("Report", back_populates="patient")





    # id---2 (db_id and docker_id. report-->string)
    # get id later and updated report..


### Diagonistic Report...
# - after inference..
#     - string, doctor,
#
# ### Save patient Details.
#     - Patient object.-> upload image.
#     - create patient()
