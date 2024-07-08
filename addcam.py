from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

# SQLAlchemy database configuration
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:@localhost:3306/iccc"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy models
class Camera(Base):
    __tablename__ = "camera_configuration"
    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String, index=True)
    location = Column(String)
    status = Column(String)

# Pydantic models
class CameraBase(BaseModel):
    ip: str
    location: str
    status: str

class CameraIn(CameraBase):
    pass

class CameraOut(CameraBase):
    id: int

    class Config:
        orm_mode = True

# FastAPI application
app = FastAPI()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/camera_configuration/", response_model=CameraOut)
def create_camera(camera: CameraIn, db: Session = Depends(get_db)):
    db_camera = Camera(ip=camera.ip, location=camera.location, status=camera.status)
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera
