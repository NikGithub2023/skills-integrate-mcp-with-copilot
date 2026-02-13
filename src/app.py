"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import os
from pathlib import Path
from database import get_db, init_db, Activity, Student, Registration

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(db: Session = Depends(get_db)):
    """Get all activities with participant information"""
    activities_list = db.query(Activity).all()
    
    # Format response to match existing API structure
    result = {}
    for activity in activities_list:
        participants = [reg.student.email for reg in activity.registrations]
        result[activity.name] = {
            "description": activity.description,
            "schedule": activity.schedule,
            "max_participants": activity.max_participants,
            "participants": participants
        }
    
    return result


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Sign up a student for an activity"""
    # Get or create student
    student = db.query(Student).filter(Student.email == email).first()
    if not student:
        student = Student(email=email)
        db.add(student)
        db.flush()
    
    # Get activity
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Check if already registered
    existing_registration = db.query(Registration).filter(
        Registration.student_id == student.id,
        Registration.activity_id == activity.id
    ).first()
    
    if existing_registration:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )
    
    # Create registration
    registration = Registration(student_id=student.id, activity_id=activity.id)
    db.add(registration)
    db.commit()
    
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Unregister a student from an activity"""
    # Get student
    student = db.query(Student).filter(Student.email == email).first()
    if not student:
        raise HTTPException(
            status_code=400,
            detail="Student not found"
        )
    
    # Get activity
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Find registration
    registration = db.query(Registration).filter(
        Registration.student_id == student.id,
        Registration.activity_id == activity.id
    ).first()
    
    if not registration:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )
    
    # Delete registration
    db.delete(registration)
    db.commit()
    
    return {"message": f"Unregistered {email} from {activity_name}"}
