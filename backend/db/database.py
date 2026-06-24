import os
from urllib.parse import quote_plus, urlparse

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Optional
load_dotenv()


def extract_supabase_project_ref(url: str) -> Optional[str]:
    host = urlparse(url.strip()).netloc
    if host.endswith(".supabase.co"):
        return host.split(".")[0]
    return None


def get_database_url() -> str:
    db_url = os.getenv("DATABASE_URL", "").strip()
    if db_url.startswith("postgresql://") or db_url.startswith("postgres://"):
        return db_url

    password = os.getenv("PASSWORD") or os.getenv("SUPABASE_DB_PASSWORD")
    if not password:
        raise RuntimeError(
            "Set DATABASE_URL to a postgresql:// connection string, or set "
            "PASSWORD/SUPABASE_DB_PASSWORD along with DATABASE_URL or SUPABASE_URL."
        )

    project_url = db_url or os.getenv("SUPABASE_URL", "").strip()
    project_ref = extract_supabase_project_ref(project_url)
    if not project_ref:
        raise RuntimeError(
            "Could not determine Supabase project ref. Use a postgresql:// "
            "DATABASE_URL or a Supabase project/REST URL in DATABASE_URL/SUPABASE_URL."
        )

    encoded_password = quote_plus(password)
    return (
        f"postgresql://postgres:{encoded_password}"
        f"@db.{project_ref}.supabase.co:5432/postgres"
    )


DATABASE_URL = get_database_url()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
