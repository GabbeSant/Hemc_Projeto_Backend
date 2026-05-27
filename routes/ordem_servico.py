from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.equipamento import Equipamento
from models.manutencao import Manutencao
from models.ordem_servico import OrdemServico
from schemas.ordem_servico import OrdemServicoCreate, OrdemServicoOut, OrdemServicoUpdate

router = APIRouter(prefix="/ordens-servico", tags=["Ordens de Serviço"])


def gerar_os_preventivas_pendentes(db: Session) -> list[int]:
    """
    Percorre equipamentos ativos e cria OS preventiva quando a próxima data de
    manutenção está a ≤ 7 dias e não existe OS preventiva aberta/em_execucao.
    A base de cálculo é a última preventiva concluída ou, na ausência dela,
    a data_aquisicao do equipamento. Delta: 30 dias (mensal) ou 90 (trimestral).
    Projetada para ser chamada no startup e em /api/indicadores, mantendo tudo
    síncrono sem APScheduler — suficiente para o volume hospitalar esperado.
    """
    hoje = datetime.now().date()
    criadas: list[int] = []

    equipamentos = (
        db.query(Equipamento)
        .filter(Equipamento.status_atual != "fora_de_operacao")
        .all()
    )

    for equip in equipamentos:
        delta = timedelta(days=30 if equip.frequencia_preventiva == "mensal" else 90)

        ultima_prev = (
            db.query(Manutencao)
            .filter(
                Manutencao.id_equipamento == equip.id_equipamento,
                Manutencao.tipo == "preventiva",
            )
            .order_by(Manutencao.data_execucao.desc())
            .first()
        )

        if ultima_prev:
            base = datetime.strptime(ultima_prev.data_execucao, "%Y-%m-%d %H:%M:%S").date()
        elif equip.data_aquisicao:
            base = datetime.strptime(equip.data_aquisicao, "%Y-%m-%d").date()
        else:
            base = hoje

        proxima = base + delta

        if proxima > hoje + timedelta(days=7):
            continue

        os_aberta = (
            db.query(OrdemServico)
            .filter(
                OrdemServico.id_equipamento == equip.id_equipamento,
                OrdemServico.tipo == "preventiva",
                OrdemServico.status_os.in_(["aberta", "em_execucao"]),
            )
            .first()
        )

        if os_aberta:
            continue

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        os_ = OrdemServico(
            tipo="preventiva",
            data_geracao=now_str,
            data_programada=proxima.strftime("%Y-%m-%d"),
            id_equipamento=equip.id_equipamento,
            status_os="aberta",
        )
        db.add(os_)
        db.flush()
        criadas.append(os_.id_os)

    if criadas:
        db.commit()

    return criadas


@router.get("/", response_model=list[OrdemServicoOut])
def listar(db: Session = Depends(get_db)):
    return db.query(OrdemServico).order_by(OrdemServico.id_os.desc()).all()


@router.get("/{id_os}", response_model=OrdemServicoOut)
def buscar(id_os: int, db: Session = Depends(get_db)):
    os_ = db.get(OrdemServico, id_os)
    if not os_:
        raise HTTPException(status_code=404, detail="Ordem de serviço não encontrada")
    return os_


@router.post("/gerar-preventivas", status_code=200)
def gerar_preventivas(db: Session = Depends(get_db)):
    """Aciona manualmente a geração de OS preventivas pendentes (ação do admin)."""
    criadas = gerar_os_preventivas_pendentes(db)
    return {"criadas": len(criadas), "ids_os": criadas}


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
