

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import date
from typing import List

from fastapi.middleware.cors import CORSMiddleware

# -------------------- Database Setup --------------------
DATABASE_URL = "postgresql://Postgres_sql_owner:z31bWYweGVFd@ep-white-tree-a7pollpn-pooler.ap-southeast-2.aws.neon.tech/Postgres_sql?sslmode=require"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# -------------------- SQLAlchemy Model --------------------
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    student_class = Column(String)
    section = Column(String)
    gender = Column(String)
    contact = Column(String)
    admission_date = Column(Date)
    status = Column(Boolean, default=True)

# Create the table if it doesn't exist
Base.metadata.create_all(bind=engine)

# -------------------- Pydantic Schemas --------------------
class StudentSchema(BaseModel):
    name: str
    student_class: str
    section: str
    gender: str
    contact: str
    admission_date: date
    status: bool

class StudentResponse(BaseModel):
    id: int
    name: str
    student_class: str
    section: str
    gender: str
    contact: str
    admission_date: date
    status: bool

    class Config:
        orm_mode = True

# -------------------- FastAPI App --------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace '*' with your frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Student
@app.post("/add-student")
def add_student(student: StudentSchema):
    db = SessionLocal()
    try:
        new_student = Student(**student.dict())
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        return {"message": "Student added successfully", "student_id": new_student.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# Get All Students
@app.get("/students", response_model=List[StudentResponse])
def get_students():
    db = SessionLocal()
    try:
        return db.query(Student).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# ✅ Delete Student by ID
@app.delete("/delete_students/{student_id}")
def delete_student(student_id: int):
    db = SessionLocal()
    try:
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        db.delete(student)
        db.commit()
        return {"message": f"Student with ID {student_id} deleted successfully"}
    finally:
        db.close()

# ✅ Edit Student by ID
@app.put("/update_students/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, updated_data: StudentSchema):
    db = SessionLocal()
    try:
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        for key, value in updated_data.dict().items():
            setattr(student, key, value)

        db.commit()
        db.refresh(student)
        return student
    finally:
        db.close()

# -------------------- Run the App --------------------
if __name__ == "__main__":
    import uvicorn

    def main():
        uvicorn.run("main:app", host="0.0.0.0", port=2323, reload=True)

    main()
