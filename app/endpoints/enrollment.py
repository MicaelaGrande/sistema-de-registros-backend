from fastapi import HTTPException, APIRouter, Depends, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.enrollment import Enrollment
from app.models.students import Student
from app.models.activity import Activity
from app.schemas.enrollment import ShowEnrollment, CreateEnrollment, UpdateEnrollment
from app.core.dependencies import get_current_user

router = APIRouter(
    prefix="/enrollment",
    tags=["enrollment"],
    dependencies=[Depends(get_current_user)]
)


@router.get("/", response_model=list[ShowEnrollment])
def get_all_enrollment(db: Session = Depends(get_db)):
    enrollments = db.query(Enrollment).all()

    return enrollments


@router.post("/", response_model=ShowEnrollment)
def post_new_enrollment(
    new_enrollment: CreateEnrollment, db: Session = Depends(get_db)
):

    existing_student = (
        db.query(Student).filter(Student.id == new_enrollment.student_id).first()
    )
    if not existing_student:
        raise HTTPException(status_code=404, detail="El alumno no existe")

    existing_activity = (
        db.query(Activity).filter(Activity.id == new_enrollment.activity_id).first()
    )
    if not existing_student.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede inscribir un alumno inactivo",
        )
    if not existing_activity:
        raise HTTPException(status_code=404, detail="La actividad no existe")

    if not existing_activity.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede inscribir en una actividad inactiva",
        )

    # 🔹 Buscar si ya existe inscripción
    existing_enrollment = (
        db.query(Enrollment)
        .filter(
            Enrollment.activity_id == new_enrollment.activity_id,
            Enrollment.student_id == new_enrollment.student_id,
        )
        .first()
    )

    if existing_enrollment:
        if existing_enrollment.is_active:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una inscripción activa",
            )
        else:
            # 🔹 Validar capacidad antes de reactivar
            active_enrollments = (
                db.query(Enrollment)
                .filter(
                    Enrollment.activity_id == new_enrollment.activity_id,
                    Enrollment.is_active == True,
                )
                .count()
            )

            if active_enrollments >= existing_activity.capacity:
                raise HTTPException(
                    status_code=400,
                    detail="La actividad alcanzó su capacidad máxima",
                )

            existing_enrollment.is_active = True
            db.commit()
            db.refresh(existing_enrollment)
            return existing_enrollment

    # 🔹 Validar capacidad antes de crear nueva inscripción
    active_enrollments = (
        db.query(Enrollment)
        .filter(
            Enrollment.activity_id == new_enrollment.activity_id,
            Enrollment.is_active == True,
        )
        .count()
    )

    if active_enrollments >= existing_activity.capacity:
        raise HTTPException(
            status_code=400,
            detail="La actividad alcanzó su capacidad máxima",
        )

    enrollment = Enrollment(
        student_id=new_enrollment.student_id,
        activity_id=new_enrollment.activity_id,
    )

    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)

    return enrollment


@router.patch("/{enrollment_id}", response_model=ShowEnrollment)
def update_enrollment(
    enrollment_id: int,
    update_data: UpdateEnrollment,
    db: Session = Depends(get_db),
):
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()

    if not enrollment:
        raise HTTPException(
            status_code=404,
            detail="Inscripción no encontrada",
        )
    if update_data.is_active:

        activity = (
            db.query(Activity).filter(Activity.id == enrollment.activity_id).first()
        )

        active_enrollments = (
            db.query(Enrollment)
            .filter(
                Enrollment.activity_id == enrollment.activity_id,
                Enrollment.is_active == True,
            )
            .count()
        )

        if active_enrollments >= activity.capacity:
            raise HTTPException(
                status_code=400,
                detail="La actividad alcanzó su capacidad máxima",
            )

    enrollment.is_active = update_data.is_active

    db.commit()
    db.refresh(enrollment)

    return enrollment


@router.delete("/{enrollment_id}", response_model=ShowEnrollment)
def deactivate_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()

    if not enrollment:
        raise HTTPException(status_code=404, detail="No existe la incripcion")

    enrollment.is_active = False
    db.commit()
    db.refresh(enrollment)

    return enrollment
