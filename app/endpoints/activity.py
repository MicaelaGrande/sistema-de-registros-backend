from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.activity import Activity
from app.schemas.activity import (
    CreateActivity,
    Activity as ActivitySchema,
    UpdateActivity,
)
from app.models.activity_day import Activity_day
from app.models.enrollment import Enrollment
from app.models.day import Day
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/activities",
    tags=["activities"],
    dependencies=[Depends(get_current_user)]
)


# GET
@router.get("/", response_model=list[ActivitySchema])
def get_activities(
    name: str | None = Query(None),
    professor: str | None = Query(None),
    day: str | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Activity).options(
        joinedload(Activity.activity_days).joinedload(Activity_day.day),
        joinedload(Activity.enrollments).joinedload(Enrollment.student),
    )

    if name:
        query = query.filter(Activity.name.ilike(f"%{name.strip().title()}%"))

    if professor:
        query = query.filter(
            Activity.professor_name.ilike(f"%{professor.strip().lower()}%")
        )

    if day:
        query = (
            query.join(Activity.activity_days)
            .join(Activity_day.day)
            .filter(Day.name == day)
            .distinct()
        )

    return query.all()


# GET con id
@router.get("/{activity_id}", response_model=ActivitySchema)
def get_activity_id(activity_id: int, db: Session = Depends(get_db)):
    activity = (
        db.query(Activity)
        .options(
            joinedload(Activity.activity_days).joinedload(Activity_day.day),
            joinedload(Activity.enrollments).joinedload(Enrollment.student),
        )
        .filter(Activity.id == activity_id)
        .first()
    )
    if not activity:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    return activity


# POST
@router.post("/", response_model=ActivitySchema)
def create_activity(activity_response: CreateActivity, db: Session = Depends(get_db)):

    # Validación 1: Debe tener al menos un día
    if not activity_response.activity_days:
        raise HTTPException(
            status_code=400,
            detail="La actividad debe tener al menos un día y un horario",
        )

    # Validación 2: No repetir día + hora en la misma petición
    seen = set()
    for d in activity_response.activity_days:
        key = (d.day_name, d.start_time)
        if key in seen:
            raise HTTPException(
                status_code=400,
                detail="No se pueden repetir día y horario en la misma actividad",
            )
        seen.add(key)

    # Validación 3: Nombre de actividad único
    existing_activity = (
        db.query(Activity).filter(Activity.name == activity_response.name).first()
    )
    if existing_activity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una actividad con ese nombre",
        )

    # Validación 4: Verificar que TODOS los días existan antes de guardar nada
    day_map = {}
    for d in activity_response.activity_days:
        day_obj = db.query(Day).filter(Day.name == d.day_name).first()
        if not day_obj:
            raise HTTPException(
                status_code=400,
                detail=f"El día '{d.day_name}' no existe",
            )
        day_map[d.day_name] = day_obj

    # Crear actividad (todavía NO se hace commit)
    new_activity = Activity(
        name=activity_response.name,
        professor_name=activity_response.professor_name,
        capacity=activity_response.capacity,
        is_active=True,
    )

    db.add(new_activity)
    db.flush()  # genera el ID sin cerrar la transacción

    # Crear los horarios de la actividad
    for day_data in activity_response.activity_days:
        day_obj = day_map[day_data.day_name]

        new_activity_day = Activity_day(
            activity_id=new_activity.id,
            day_id=day_obj.id,
            start_time=day_data.start_time,
        )
        db.add(new_activity_day)

    #  Guardar TODO junto recién al final
    db.commit()
    db.refresh(new_activity)

    return new_activity


@router.put("/{activity_id}", response_model=ActivitySchema)
def update_activity(
    activity_id: int,
    activity_update: UpdateActivity,
    db: Session = Depends(get_db),
):
    activity = db.query(Activity).filter(Activity.id == activity_id).first()

    if not activity:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")

    #  Validación estricta
    update_data = activity_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="Debe enviar al menos un campo para actualizar",
        )

    #  Actualización dinámica (más elegante que muchos if)
    for field, value in update_data.items():
        setattr(activity, field, value)

    db.commit()
    db.refresh(activity)

    return activity


# DELETE
@router.delete("/{activity_id}", response_model=ActivitySchema)
def deactivate_activity(activity_id: int, db: Session = Depends(get_db)):
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Actividad no encotrada")

    activity.is_active = False
    db.query(Enrollment).filter(Enrollment.activity_id == activity_id).update(
        {Enrollment.is_active: False}, synchronize_session=False
    )
    db.commit()
    db.refresh(activity)
    return activity
