from db.db_base import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Patient(Base):
    __tablename__ = 'patient'
    id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, nullable=False)
    report = Column(String, nullable=True)




    # id---2 (db_id and docker_id. report-->string)
    # get id later and updated report..


### Diagonistic Report...
# - after inference..
#     - string, doctor,
#
# ### Save patient Details.
#     - Patient object.-> upload image.
#     - create patient()
