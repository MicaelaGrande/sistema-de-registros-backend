from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.students import Student
from app.models.activity import Activity
from app.models.enrollment import Enrollment

from app.schemas.student import ShowStudents, CreateStudent, UpdateStudent
from app.core.dependencies import get_current_user

router = APIRouter(
    prefix="/students",
    tags=["students"],
    dependencies=[Depends(get_current_user)]
)


@router.get("/", response_model=list[ShowStudents])
def get_all_students(db: Session = Depends(get_db)):
    students = (
        db.query(Student)
        .options(joinedload(Student.enrollments).joinedload(Enrollment.activity))
        .order_by(Student.lastname, Student.name)
        .all()
    )
    return students


@router.get("/{student_id}", response_model=ShowStudents)
def get_student_by_id(student_id: int, db: Session = Depends(get_db)):
    student = (
        db.query(Student)
        .options(joinedload(Student.enrollments).joinedload(Enrollment.activity))
        .filter(Student.id == student_id)
        .first()
    )
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return student


@router.post("/", response_model=ShowStudents)
def post_new_student(new_student: CreateStudent, db: Session = Depends(get_db)):

    # Validar DNI único
    existing_student = db.query(Student).filter(Student.dni == new_student.dni).first()

    if existing_student:
        raise HTTPException(
            status_code=409,
            detail="Ya existe un estudiante con ese DNI",
        )

    # Validar que tenga al menos una actividad
    if not new_student.activities_id:
        raise HTTPException(
            status_code=400,
            detail="El estudiante debe estar inscripto en al menos una actividad",
        )

    # Buscar actividades
    activities = (
        db.query(Activity).filter(Activity.id.in_(new_student.activities_id)).all()
    )

    if len(activities) != len(new_student.activities_id):
        raise HTTPException(
            status_code=400,
            detail="Una o más actividades no existen",
        )

    # Crear estudiante
    student = Student(
        name=new_student.name,
        lastname=new_student.lastname,
        dni=new_student.dni,
        age=new_student.age,
        celphone=new_student.celphone,
        celphone_optional=new_student.celphone_optional,
    )

    db.add(student)
    db.flush()

    for activity in activities:
        enrollment = Enrollment(student_id=student.id, activity_id=activity.id)
        db.add(enrollment)
    db.commit()
    db.refresh(student)

    return student


@router.put("/{student_id}", response_model=ShowStudents)
def put_update_student(
    student_id: int, new_data: UpdateStudent, db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="El estudiante ingresado no existe")

    if new_data.dni is not None:
        dni = (
            db.query(Student)
            .filter(Student.dni == new_data.dni, Student.id != student_id)
            .first()
        )
        if dni:
            raise HTTPException(status_code=409, detail="El DNI ingresado ya existe")

    update_data = new_data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="Debe enviar al menos un campo para actualizar",
        )

    for field, value in update_data.items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)

    return student


@router.delete("/{student_id}", response_model=ShowStudents)
def deactivate_student(student_id: int, db: Student = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="El alumno no existe")

    student.is_active = False
    for enrollment in student.enrollments:
      enrollment.is_active = False

    db.commit()
    db.refresh(student)

    return student
