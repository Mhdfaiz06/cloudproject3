from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
import uuid

app = FastAPI(title="Student Management API", version="1.0.0")

# In-memory storage (for simplicity)
students = {}
classes = {}
registrations = {}

# Pydantic Models
class Student(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    age: int
    city: str

class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    age: Optional[int] = None
    city: Optional[str] = None

class Class(BaseModel):
    class_name: str
    description: str
    start_date: date
    end_date: date
    number_of_hours: int

class ClassUpdate(BaseModel):
    class_name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    number_of_hours: Optional[int] = None

# Student Operations
@app.post("/students", status_code=201)
def create_student(student: Student):
    student_id = str(uuid.uuid4())
    students[student_id] = {**student.dict(), "id": student_id}
    return {"message": "Student created successfully", "student_id": student_id, "student": students[student_id]}

@app.get("/students")
def read_students():
    return {"students": list(students.values())}

@app.put("/students/{student_id}")
def update_student(student_id: str, student_update: StudentUpdate):
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student_data = students[student_id]
    update_data = student_update.dict(exclude_unset=True)
    student_data.update(update_data)
    
    return {"message": "Student updated successfully", "student": student_data}

@app.delete("/students/{student_id}")
def delete_student(student_id: str):
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    
    deleted_student = students.pop(student_id)
    return {"message": "Student deleted successfully", "deleted_student": deleted_student}

# Class Operations
@app.post("/classes", status_code=201)
def create_class(class_info: Class):
    class_id = str(uuid.uuid4())
    classes[class_id] = {**class_info.dict(), "id": class_id}
    registrations[class_id] = []
    return {"message": "Class created successfully", "class_id": class_id, "class": classes[class_id]}

@app.get("/classes")
def get_classes():
    return {"classes": list(classes.values())}

@app.put("/classes/{class_id}")
def update_class(class_id: str, class_update: ClassUpdate):
    if class_id not in classes:
        raise HTTPException(status_code=404, detail="Class not found")
    
    class_data = classes[class_id]
    update_data = class_update.dict(exclude_unset=True)
    
    # Convert date strings to date objects if needed
    for key, value in update_data.items():
        if key in ['start_date', 'end_date'] and isinstance(value, str):
            update_data[key] = date.fromisoformat(value)
    
    class_data.update(update_data)
    return {"message": "Class updated successfully", "class": class_data}

@app.delete("/classes/{class_id}")
def delete_class(class_id: str):
    if class_id not in classes:
        raise HTTPException(status_code=404, detail="Class not found")
    
    deleted_class = classes.pop(class_id)
    registrations.pop(class_id, None)
    return {"message": "Class deleted successfully", "deleted_class": deleted_class}

# Registration Operations
@app.post("/classes/{class_id}/students/{student_id}")
def register_student_to_class(class_id: str, student_id: str):
    if class_id not in classes:
        raise HTTPException(status_code=404, detail="Class not found")
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    
    if student_id in registrations[class_id]:
        raise HTTPException(status_code=400, detail="Student already registered in this class")
    
    registrations[class_id].append(student_id)
    return {
        "message": "Student registered successfully",
        "class": classes[class_id]["class_name"],
        "student": f"{students[student_id]['first_name']} {students[student_id]['last_name']}"
    }

@app.get("/classes/{class_id}/students")
def list_students_in_class(class_id: str):
    if class_id not in classes:
        raise HTTPException(status_code=404, detail="Class not found")
    
    registered_students = []
    for student_id in registrations.get(class_id, []):
        if student_id in students:
            registered_students.append(students[student_id])
    
    return {
        "class": classes[class_id]["class_name"],
        "total_students": len(registered_students),
        "students": registered_students
    }

@app.get("/")
def root():
    return {"message": "Student Management API", "version": "1.0.0"}