import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from typing import List

# SQLAlchemy database configuration
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:@localhost:3306/iccc"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# SQLAlchemy models
class ANPR(Base):
    __tablename__ = "anpr"
    id = Column(Integer, primary_key=True, index=True)
    vehicle_image = Column(String)
    vehicle_no = Column(String)
    geo_location = Column(String)
    lattitude = Column(Float)
    lngitude = Column(Float)
    status = Column(String)
    speed = Column(Float)
    classification = Column(String)


# Pydantic models
class ANPRBase(BaseModel):
    vehicle_image: str
    vehicle_no: str
    geo_location: str
    lattitude: float
    lngitude: float
    status: str
    speed: float
    classification: str


class ANPRCreate(ANPRBase):
    pass


class ANPROut(ANPRBase):
    id: int

    class Config:
        from_attributes = True


# FastAPI application
app = FastAPI()


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/anpr/{anpr_id}", response_model=ANPROut)
def read_anpr(anpr_id: int, db: Session = Depends(get_db)):
    anpr = db.query(ANPR).filter(ANPR.id == anpr_id).first()
    if anpr is None:
        raise HTTPException(status_code=404, detail="ANPR not found")
    return anpr


@app.get("/anpr/", response_model=List[ANPROut])
def read_all_anpr(db: Session = Depends(get_db)):
    return db.query(ANPR).all()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    uvicorn.run(app, host="127.0.0.1", port=8000)
