from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Usamos SQLite para desarrollo
DATABASE_URL = "sqlite:///./database.db"

# Engine: conexión a la base de datos
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Session: cada request usará una sesión
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base: de acá van a heredar todos los modelos
Base = declarative_base()

# Dependencia para obtener la sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
