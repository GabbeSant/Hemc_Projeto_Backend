from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.equipamento import Equipamento
from schemas.equipamento import EquipamentoCreate, EquipamentoOut, EquipamentoUpdate

router = APIRouter(prefix="/equipamentos", tags=["Equipamentos"])


@router.get("/", response_model=list[EquipamentoOut])
def listar(db: Session = Depends(get_db)):
    return db.query(Equipamento).all()


@router.get("/{id_equipamento}", response_model=EquipamentoOut)
def buscar(id_equipamento: int, db: Session = Depends(get_db)):
    equip = db.get(Equipamento, id_equipamento)
    if not equip:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")
    return equip


@router.post("/", response_model=EquipamentoOut, status_code=201)
def criar(dados: EquipamentoCreate, db: Session = Depends(get_db)):
    equip = Equipamento(**dados.model_dump())
    db.add(equip)
    db.commit()
    db.refresh(equip)
    return equip


@router.put("/{id_equipamento}", response_model=EquipamentoOut)
def atualizar(id_equipamento: int, dados: EquipamentoUpdate, db: Session = Depends(get_db)):
    equip = db.get(Equipamento, id_equipamento)
    if not equip:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(equip, campo, valor)
    db.commit()
    db.refresh(equip)
    return equip


@router.delete("/{id_equipamento}", status_code=204)
def remover(id_equipamento: int, db: Session = Depends(get_db)):
    equip = db.get(Equipamento, id_equipamento)
    if not equip:
        raise HTTPException(status_code=404, detail="Equipamento não encontrado")
    db.delete(equip)
    db.commit()
