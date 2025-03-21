from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base

load_dotenv()
database_url = os.getenv("DATABASE_URL")

engine = create_engine(database_url)

Sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
