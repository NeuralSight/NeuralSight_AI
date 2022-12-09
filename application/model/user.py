from db.db_base import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)

# class Patient(Base):
#     __tablename__ = 'patient'
    # id---2 (db_id and docker_id. report-->string)


    # get id later and updated report..


### Diagonistic Report...
# - after inference..
#     - string, doctor,
#
# ### Save patient Details.
#     - Patient object.-> upload image.
#     - create patient()
