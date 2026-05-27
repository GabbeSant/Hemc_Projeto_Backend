from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.ordem_servico import OrdemServico
from schemas.ordem_servico import OrdemServicoCreate, OrdemServicoOut, OrdemServicoUpdate

router = APIRouter(prefix="/ordens-servico", tags=["Ordens de Serviço"])


@router.get("/", response_model=list[OrdemServicoOut])
def listar(db: Session = Depends(get_db)):
    return db.query(OrdemServico).order_by(OrdemServico.id_os.desc()).all()


@router.get("/{id_os}", response_model=OrdemServicoOut)
def buscar(id_os: int, db: Session = Depends(get_db)):
    os_ = db.get(OrdemServico, id_os)
    if not os_:
        raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")
    return os_


@router.post("/", response_model=OrdemServicoOut, status_code=201)
def criar(dados: OrdemServicoCreate, db: Session = Depends(get_db)):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os_ = OrdemServico(**dados.model_dump(), data_geracao=now, status_os="aberta")
    db.add(os_)
    db.commit()
    db.refresh(os_)
    return os_


@router.patch("/{id_os}", response_model=OrdemServicoOut)
def atualizar(id_os: int, dados: OrdemServicoUpdate, db: Session = Depends(get_db)):
    os_ = db.get(OrdemServico, id_os)
    if not os_:
        raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(os_, campo, valor)
    db.commit()
    db.refresh(os_)
    return os_
