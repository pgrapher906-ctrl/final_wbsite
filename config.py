import os

class Config:
    # We are pasting the link directly here to stop the 502 crash
    uri = "postgresql://neondb_owner:npg_qna54HgPVOvb@ep-flat-wind-aiezn0bh-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"
    
    # Render requires 'postgresql://' but Neon sometimes gives 'postgres://'
    # This code fixes that automatically
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "smart_water_2026_secure_key"

    # FIX: Prevents Vercel 500 errors by pinging the database to keep the connection alive
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
