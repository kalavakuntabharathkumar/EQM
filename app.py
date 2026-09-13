from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, String, Float, DateTime, select, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

engine = create_engine("sqlite:///equipment.db", connect_args={"check_same_thread": False})

class Base(DeclarativeBase):
    pass

class Equipment(Base):
    __tablename__ = "equipment"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(20), index=True)
    temperature: Mapped[float] = mapped_column(Float)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    __table_args__ = (Index("ix_equipment_status_updated", "status", "updated_at"),)

Base.metadata.create_all(engine)
app = FastAPI(title="Equipment Monitoring & Alert Platform", version="1.0")

class EquipmentIn(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    temperature: float = Field(ge=-50, le=150)
    status: str = Field(pattern="^(healthy|degraded|unavailable)$")

class EquipmentOut(EquipmentIn):
    id: int
    updated_at: datetime

@app.get("/health")
def health():
    return {"service": "equipment-monitor", "status": "healthy"}

@app.post("/equipment", response_model=EquipmentOut, status_code=201)
def create_equipment(item: EquipmentIn):
    with Session(engine) as db:
        existing = db.scalar(select(Equipment).where(Equipment.name == item.name))
        if existing:
            raise HTTPException(409, "Equipment already exists")
        row = Equipment(**item.model_dump(), updated_at=datetime.utcnow())
        db.add(row)
        db.commit()
        db.refresh(row)
        return row

@app.get("/equipment", response_model=list[EquipmentOut])
def list_equipment(status: Optional[str] = Query(None, pattern="^(healthy|degraded|unavailable)$")):
    with Session(engine) as db:
        query = select(Equipment).order_by(Equipment.updated_at.desc())
        if status:
            query = query.where(Equipment.status == status)
        return list(db.scalars(query))

@app.get("/equipment/{equipment_id}", response_model=EquipmentOut)
def get_equipment(equipment_id: int):
    with Session(engine) as db:
        row = db.get(Equipment, equipment_id)
        if not row:
            raise HTTPException(404, "Equipment not found")
        return row

@app.put("/equipment/{equipment_id}", response_model=EquipmentOut)
def update_equipment(equipment_id: int, item: EquipmentIn):
    with Session(engine) as db:
        row = db.get(Equipment, equipment_id)
        if not row:
            raise HTTPException(404, "Equipment not found")
        row.name, row.temperature, row.status = item.name, item.temperature, item.status
        row.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(row)
        return row

@app.delete("/equipment/{equipment_id}")
def delete_equipment(equipment_id: int):
    with Session(engine) as db:
        row = db.get(Equipment, equipment_id)
        if not row:
            raise HTTPException(404, "Equipment not found")
        db.delete(row)
        db.commit()
        return {"deleted": equipment_id}

@app.get("/alerts")
def alerts():
    with Session(engine) as db:
        rows = db.scalars(select(Equipment).where(Equipment.status != "healthy")).all()
        return [{"id": r.id, "name": r.name, "status": r.status, "temperature": r.temperature} for r in rows]
