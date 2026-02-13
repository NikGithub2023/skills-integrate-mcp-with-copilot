"""
Database models and session management for Mergington High School Management System
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Create database engine
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mergington_high.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


# Models
class Activity(Base):
    """Activity/Event model"""
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=False)
    schedule = Column(String, nullable=False)
    max_participants = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    registrations = relationship("Registration", back_populates="activity", cascade="all, delete-orphan")


class Student(Base):
    """Student model"""
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=True)
    grade_level = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    registrations = relationship("Registration", back_populates="student", cascade="all, delete-orphan")


class Registration(Base):
    """Registration model (many-to-many relationship between students and activities)"""
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="registrations")
    activity = relationship("Activity", back_populates="registrations")


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database with tables and seed data"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Seed initial data
    db = SessionLocal()
    try:
        # Check if we already have data
        if db.query(Activity).count() > 0:
            print("Database already initialized")
            return
        
        # Create initial activities
        initial_activities = [
            {
                "name": "Chess Club",
                "description": "Learn strategies and compete in chess tournaments",
                "schedule": "Fridays, 3:30 PM - 5:00 PM",
                "max_participants": 12
            },
            {
                "name": "Programming Class",
                "description": "Learn programming fundamentals and build software projects",
                "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
                "max_participants": 20
            },
            {
                "name": "Gym Class",
                "description": "Physical education and sports activities",
                "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
                "max_participants": 30
            },
            {
                "name": "Soccer Team",
                "description": "Join the school soccer team and compete in matches",
                "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
                "max_participants": 22
            },
            {
                "name": "Basketball Team",
                "description": "Practice and play basketball with the school team",
                "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
                "max_participants": 15
            },
            {
                "name": "Art Club",
                "description": "Explore your creativity through painting and drawing",
                "schedule": "Thursdays, 3:30 PM - 5:00 PM",
                "max_participants": 15
            },
            {
                "name": "Drama Club",
                "description": "Act, direct, and produce plays and performances",
                "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
                "max_participants": 20
            },
            {
                "name": "Math Club",
                "description": "Solve challenging problems and participate in math competitions",
                "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
                "max_participants": 10
            },
            {
                "name": "Debate Team",
                "description": "Develop public speaking and argumentation skills",
                "schedule": "Fridays, 4:00 PM - 5:30 PM",
                "max_participants": 12
            }
        ]
        
        # Initial students data
        initial_students = [
            {"email": "michael@mergington.edu", "name": "Michael"},
            {"email": "daniel@mergington.edu", "name": "Daniel"},
            {"email": "emma@mergington.edu", "name": "Emma"},
            {"email": "sophia@mergington.edu", "name": "Sophia"},
            {"email": "john@mergington.edu", "name": "John"},
            {"email": "olivia@mergington.edu", "name": "Olivia"},
            {"email": "liam@mergington.edu", "name": "Liam"},
            {"email": "noah@mergington.edu", "name": "Noah"},
            {"email": "ava@mergington.edu", "name": "Ava"},
            {"email": "mia@mergington.edu", "name": "Mia"},
            {"email": "amelia@mergington.edu", "name": "Amelia"},
            {"email": "harper@mergington.edu", "name": "Harper"},
            {"email": "ella@mergington.edu", "name": "Ella"},
            {"email": "scarlett@mergington.edu", "name": "Scarlett"},
            {"email": "james@mergington.edu", "name": "James"},
            {"email": "benjamin@mergington.edu", "name": "Benjamin"},
            {"email": "charlotte@mergington.edu", "name": "Charlotte"},
            {"email": "henry@mergington.edu", "name": "Henry"}
        ]
        
        # Create activities
        activity_map = {}
        for activity_data in initial_activities:
            activity = Activity(**activity_data)
            db.add(activity)
            db.flush()
            activity_map[activity_data["name"]] = activity
        
        # Create students
        student_map = {}
        for student_data in initial_students:
            student = Student(**student_data)
            db.add(student)
            db.flush()
            student_map[student_data["email"]] = student
        
        # Create initial registrations
        initial_registrations = [
            ("Chess Club", ["michael@mergington.edu", "daniel@mergington.edu"]),
            ("Programming Class", ["emma@mergington.edu", "sophia@mergington.edu"]),
            ("Gym Class", ["john@mergington.edu", "olivia@mergington.edu"]),
            ("Soccer Team", ["liam@mergington.edu", "noah@mergington.edu"]),
            ("Basketball Team", ["ava@mergington.edu", "mia@mergington.edu"]),
            ("Art Club", ["amelia@mergington.edu", "harper@mergington.edu"]),
            ("Drama Club", ["ella@mergington.edu", "scarlett@mergington.edu"]),
            ("Math Club", ["james@mergington.edu", "benjamin@mergington.edu"]),
            ("Debate Team", ["charlotte@mergington.edu", "henry@mergington.edu"])
        ]
        
        for activity_name, student_emails in initial_registrations:
            activity = activity_map[activity_name]
            for email in student_emails:
                student = student_map[email]
                registration = Registration(student_id=student.id, activity_id=activity.id)
                db.add(registration)
        
        db.commit()
        print("Database initialized successfully with seed data")
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()
