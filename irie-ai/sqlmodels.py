import sys
import random
import pymysql
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String,JSON, TEXT, DateTime, Boolean
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
Base = declarative_base()
#csvdat=pd.read_csv('/Users/arun/machinelearning/data/wine.dat')
#print(csvdat)


class Model(Base):
    __tablename__ = 'model'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    model_id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    content = Column(LONGTEXT, nullable=True)
    description = Column(String(250), nullable=False)
    algorithm = Column(String(250), nullable=True)
    status = Column(String(50), nullable=True)
    precision_value = Column(Integer, nullable=True)
    recall_value = Column(Integer, nullable=True)
    fscore_value = Column(Integer, nullable=True)
    accuracy = Column(Integer, nullable=True)
    lda_model = Column(LONGTEXT, nullable=True)

class CSVData(Base):
    __tablename__ = 'csv_dataset'
    id = Column(Integer, primary_key=True)
    filename = Column(String(1000), nullable=False)
    title = Column(TEXT, nullable=True)
    content = Column(TEXT, nullable=True)
    model_id = Column(Integer, ForeignKey('model.model_id'))

engine = create_engine(
      "mysql+pymysql://irie:irie1234@iriedb.cwj1ihf4ectz.us-east-1.rds.amazonaws.com/irie?host=iriedb.cwj1ihf4ectz.us-east-1.rds.amazonaws.com?port=3306")

# Local
# engine = create_engine(
#    "mysql+pymysql://irie:irie1234@localhost/irie?host=localhost?port=3306"
# )
# engine = create_engine(
#     "mysql+pymysql://root:root@localhost/irie?host=localhost?port=3306"
#     )
Base.metadata.create_all(engine)

