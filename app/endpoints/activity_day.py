from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.activity_day import Activity_day
from app.models.activity import Activity
from app.models.day import Day

from app.schemas.activity_day import ActivityDay, ActivityDayCreate, ActivityDayUpdate

router = APIRouter(
    prefix="/activities/{activity_id}/activity-days", tags=["Activity Days"]
)

def validate_activity(activity_id: int, db: Session):
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="La actividad no existe")
    return activity


# GET
@router.get("/", response_model=list[ActivityDay])
def get_timetable(activity_id: int, db: Session = Depends(get_db)):

    activity = validate_activity(activity_id, db)

    timetable = (
        db.query(Activity_day)
        .options(joinedload(Activity_day.day))
        .filter(Activity_day.activity_id == activity_id)
        .order_by(Activity_day.day_id, Activity_day.start_time)
        .all()
    )
    return timetable


# POST


@router.post("/", response_model=ActivityDay)
def post_timetable(
    activity_id: int,
    timetable_response: ActivityDayCreate,
    db: Session = Depends(get_db),
):
    # validacion: que la actividad solicitada exista
    activity = validate_activity(activity_id, db)

    # validacion: que el dia exista
    day_obj = db.query(Day).filter(Day.name == timetable_response.day_name).first()
    if not day_obj:
        raise HTTPException(
            status_code=400,
            detail=f"El día '{timetable_response.day_name}' no existe",
        )
    # validacion: que el horario y dia ya exista
    existing = (
        db.query(Activity_day)
        .filter(
            Activity_day.activity_id == activity_id,
            Activity_day.day_id == day_obj.id,
            Activity_day.start_time == timetable_response.start_time,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Ese horario ya existe para esta actividad",
        )

    new_timetable = Activity_day(
        day_id=day_obj.id,
        activity_id=activity_id,
        start_time=timetable_response.start_time,
    )

    db.add(new_timetable)
    db.commit()
    db.refresh(new_timetable)
    return new_timetable


# PUT
@router.put("/{timetable_id}", response_model=ActivityDay)
def put_timetable(
    activity_id: int,
    new_timetable_response: ActivityDayUpdate,
    timetable_id: int,
    db: Session = Depends(get_db),
):
    activity = validate_activity(activity_id, db)

    timetable = (
        db.query(Activity_day)
        .filter(
            Activity_day.id == timetable_id, Activity_day.activity_id == activity_id
        )
        .first()
    )
    if not timetable:
        raise HTTPException(status_code=404, detail="Horario no encontrado")

    update_data = new_timetable_response.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="Debe enviar al menos un campo para actualizar",
        )
    if "day_name" in update_data:
        day_obj = db.query(Day).filter(Day.name == update_data["day_name"]).first()
        if not day_obj:
            raise HTTPException(status_code=400, detail="Día no válido")

        timetable.day_id = day_obj.id
        update_data.pop("day_name")

    # Actualizar otros campos
    for field, value in update_data.items():
        setattr(timetable, field, value)

    #  Validar duplicado nuevamente
    duplicate = (
        db.query(Activity_day)
        .filter(
            Activity_day.activity_id == activity_id,
            Activity_day.day_id == timetable.day_id,
            Activity_day.start_time == timetable.start_time,
            Activity_day.id != timetable_id,
        )
        .first()
    )

    if duplicate:
        raise HTTPException(
            status_code=409,
            detail="Ese horario ya existe para esta actividad",
        )

    db.commit()
    db.refresh(timetable)

    return timetable


# DELETE
@router.delete("/{timetable_id}", response_model=ActivityDay)
def delete_timetable(
    activity_id: int, timetable_id: int, db: Session = Depends(get_db)
):
    activity = validate_activity(activity_id, db)

    timetable = db.query(Activity_day).filter(
        Activity_day.activity_id == activity_id, Activity_day.id == timetable_id
    ).first()
    if not timetable:
        raise HTTPException(status_code=404, detail="Horario no encontrado")

    db.delete(timetable)
    db.commit()

    return timetable
