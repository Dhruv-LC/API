from fastapi import FastAPI, Depends, HTTPException, status
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

# Update camera endpoint
@app.put("/camera_configuration/{camera_id}", response_model=CameraOut)
def update_camera(camera_id: int, camera: CameraIn, db: Session = Depends(get_db)):
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if db_camera is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")
    
    db_camera.ip = camera.ip
    db_camera.location = camera.location
    db_camera.status = camera.status
    
    db.commit()
    db.refresh(db_camera)
    return db_camera

# Entry point if this file is run directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
