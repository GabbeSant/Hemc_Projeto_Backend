from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.usuario import Usuario

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


class UsuarioCreate(BaseModel):
    nome: str
    perfil: str
    id_setor: int


class UsuarioOut(BaseModel):
    id_usuario: int
    nome: str
    perfil: str
    id_setor: int

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[UsuarioOut])
def listar(db: Session = Depends(get_db)):
    return db.query(Usuario).all()


@router.get("/{id_usuario}", response_model=UsuarioOut)
def buscar(id_usuario: int, db: Session = Depends(get_db)):
    u = db.get(Usuario, id_usuario)
    if not u:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return u


@router.post("/", response_model=UsuarioOut, status_code=201)
def criar(dados: UsuarioCreate, db: Session = Depends(get_db)):
    u = Usuario(**dados.model_dump())
    db.add(u)
    db.commit()
    db.refresh(u)
    return u
