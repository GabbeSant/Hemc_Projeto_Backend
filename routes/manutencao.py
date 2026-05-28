from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.equipamento import Equipamento
from models.manutencao import (
    ChecklistItem,
    Manutencao,
    ManutencaoChecklist,
    ManutencaoCorretiva,
    ManutencaoPreventiva,
    Peca,
    PecaSubstituida,
)
from models.ordem_servico import OrdemServico
from models.usuario import Usuario
from routes.auth import get_current_user, require_tecnico
from schemas.manutencao import (
    ManutencaoCorretivaCreate,
    ManutencaoOut,
    ManutencaoPreventivaCreate,
)

router = APIRouter(prefix="/manutencoes", tags=["Manutenção"])


@router.get("/", response_model=list[ManutencaoOut])
def listar(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return db.query(Manutencao).order_by(Manutencao.id_manutencao.desc()).all()


@router.get("/equipamento/{id_equipamento}", response_model=list[ManutencaoOut])
def historico(id_equipamento: int, db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return (
        db.query(Manutencao)
        .filter(Manutencao.id_equipamento == id_equipamento)
        .order_by(Manutencao.data_execucao.desc())
        .all()
    )


@router.post("/preventiva", response_model=ManutencaoOut, status_code=201)
def registrar_preventiva(dados: ManutencaoPreventivaCreate, db: Session = Depends(get_db), _: Usuario = Depends(require_tecnico)):
    os_ = db.get(OrdemServico, dados.id_os)
    if not os_:
        raise HTTPException(status_code=404, detail="OS não encontrada")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    m = Manutencao(
        tipo="preventiva",
        data_execucao=now,
        id_equipamento=dados.id_equipamento,
        id_responsavel=dados.id_responsavel,
        id_os=dados.id_os,
    )
    db.add(m)
    db.flush()

    mp = ManutencaoPreventiva(
        id_manutencao=m.id_manutencao,
        houve_substituicao=int(dados.houve_substituicao),
        checklist_concluido=int(len(dados.checklist) > 0),
    )
    db.add(mp)

    for p in dados.pecas:
        db.add(PecaSubstituida(
            id_manutencao=m.id_manutencao,
            id_peca=p.id_peca,
            quantidade=p.quantidade,
        ))

    for item in dados.checklist:
        db.add(ManutencaoChecklist(
            id_manutencao=m.id_manutencao,
            id_item=item.id_item,
            resultado=item.resultado,
            observacao=item.observacao,
        ))

    os_.status_os = "concluida"
    equip = db.get(Equipamento, dados.id_equipamento)
    if equip:
        equip.status_atual = "em_funcionamento"

    db.commit()
    db.refresh(m)
    return m


@router.post("/corretiva", response_model=ManutencaoOut, status_code=201)
def registrar_corretiva(dados: ManutencaoCorretivaCreate, db: Session = Depends(get_db), _: Usuario = Depends(require_tecnico)):
    os_ = db.get(OrdemServico, dados.id_os)
    if not os_:
        raise HTTPException(status_code=404, detail="OS não encontrada")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    m = Manutencao(
        tipo="corretiva",
        data_execucao=now,
        id_equipamento=dados.id_equipamento,
        id_responsavel=dados.id_responsavel,
        id_os=dados.id_os,
    )
    db.add(m)
    db.flush()

    mc = ManutencaoCorretiva(
        id_manutencao=m.id_manutencao,
        descricao_reparo=dados.descricao_reparo,
        testes_finais=dados.testes_finais,
        status_resultante=dados.status_resultante,
    )
    db.add(mc)

    for p in dados.pecas:
        db.add(PecaSubstituida(
            id_manutencao=m.id_manutencao,
            id_peca=p.id_peca,
            quantidade=p.quantidade,
        ))

    os_.status_os = "concluida"
    equip = db.get(Equipamento, dados.id_equipamento)
    if equip:
        equip.status_atual = dados.status_resultante

    if os_.id_chamado:
        from models.chamado import Chamado
        chamado = db.get(Chamado, os_.id_chamado)
        if chamado:
            chamado.status_chamado = "fechado"

    db.commit()
    db.refresh(m)
    return m


@router.get("/pecas")
def listar_pecas(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return [{"id_peca": p.id_peca, "nome_peca": p.nome_peca, "codigo": p.codigo}
            for p in db.query(Peca).all()]


@router.get("/checklist-itens")
def listar_checklist(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return [{"id_item": i.id_item, "descricao_teste": i.descricao_teste, "tipo_teste": i.tipo_teste}
            for i in db.query(ChecklistItem).all()]
