import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'dev-secret-key'

    SQLALCHEMY_DATABASE_URI = (
        "postgresql://postgres.qcxnouurjgspgqkrfvoh:[Louis.alejo133]@aws-1-us-east-1.pooler.supabase.com:6543/postgres"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
