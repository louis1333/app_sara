import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'dev-secret-key'

    SQLALCHEMY_DATABASE_URI = (
        "postgresql://postgres:Louis.alejo133@"
        "db.qcxnouurjgspgqkrfvoh.supabase.co:5432/postgres"
        "?sslmode=require"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
