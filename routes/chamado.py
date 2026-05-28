from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.chamado import Chamado
from models.equipamento import Equipamento
from models.ordem_servico import OrdemServico
from models.usuario import Usuario
from routes.auth import get_current_user, require_enfermeira
from schemas.chamado import ChamadoCreate, ChamadoOut, ChamadoUpdate

router = APIRouter(prefix="/chamados", tags=["Chamados"])


@router.get("/", response_model=list[ChamadoOut])
def listar(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return db.query(Chamado).all()


@router.get("/{id_chamado}", response_model=ChamadoOut)
def buscar(id_chamado: int, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    c = db.get(Chamado, id_chamado)
    if not c:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    return c


@router.post("/", response_model=ChamadoOut, status_code=201)
def abrir(dados: ChamadoCreate, db: Session = Depends(get_db), _: Usuario = Depends(require_enfermeira)):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    chamado = Chamado(**dados.model_dump(), data_abertura=now, status_chamado="aberto")
    db.add(chamado)
    db.flush()

    os_ = OrdemServico(
        tipo="corretiva",
        data_geracao=now,
        id_equipamento=dados.id_equipamento,
        id_chamado=chamado.id_chamado,
        status_os="aberta",
    )
    db.add(os_)

    equip = db.get(Equipamento, dados.id_equipamento)
    if equip:
        equip.status_atual = "aguardando_reparo"

    db.commit()
    db.refresh(chamado)
    return chamado


@router.patch("/{id_chamado}", response_model=ChamadoOut)
def atualizar(id_chamado: int, dados: ChamadoUpdate, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    c = db.get(Chamado, id_chamado)
    if not c:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(c, campo, valor)
    db.commit()
    db.refresh(c)
    return c
