from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint
from database import Base


class OrdemServico(Base):
    __tablename__ = "ordem_servico"

    id_os = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(String, nullable=False)
    data_geracao = Column(String, nullable=False)
    data_programada = Column(String)
    status_os = Column(String, nullable=False, default="aberta")
    id_equipamento = Column(Integer, ForeignKey("equipamento.id_equipamento"), nullable=False)
    id_chamado = Column(Integer, ForeignKey("chamado.id_chamado"), nullable=True)

    __table_args__ = (
        CheckConstraint("tipo IN ('preventiva','corretiva')", name="ck_tipo_os"),
        CheckConstraint(
            "status_os IN ('aberta','em_execucao','concluida','cancelada')",
            name="ck_status_os",
        ),
    )
