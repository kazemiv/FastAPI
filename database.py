from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMI_DATABASE_URL = 'sqlite:///./user.db'

engine=create_engine(SQLALCHEMI_DATABASE_URL, connect_args={'check_same_thread':False})
SessionLocal=sessionmaker(autocommit=False , autoflush=False , bind=engine)
Base=declarative_base()

