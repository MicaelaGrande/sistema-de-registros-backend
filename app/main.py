from fastapi import FastAPI
from app.database import Base, engine, SessionLocal
from app.models import *  # importa todos los modelos
from app.endpoints.activity import router as activity_router
from app.enums import Day_Name


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas o ya existentes.")

    db = SessionLocal()
    try:
        # Verificar si ya hay días en la tabla
        if db.query(Day).count() == 0:
            # Insertar los 7 días
            for day_name in Day_Name:
                new_day = Day(name=day_name)
                db.add(new_day)
            db.commit()
            print("Días de la semana insertados.")
        else:
            print("Los días ya existen en la base de datos.")
    finally:
        db.close()


create_tables()  # se ejecuta al iniciar

app = FastAPI(title="Sistema de registros")
app.include_router(activity_router)


@app.get("/")
def root():
    return {"status": "ok"}
