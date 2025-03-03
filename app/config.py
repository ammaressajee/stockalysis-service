import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Config:
    # SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://ammar:Zoo=2582924@localhost:5432/ecib") <- local database
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False