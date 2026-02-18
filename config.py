import os

class Config:
    SECRET_KEY = 'your_secret_key_here'
    # Replace with your actual Neon DB connection string
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://neondb_owner:npg_qna54HgPVOvb@ep-flat-wind-aiezn0bh-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
