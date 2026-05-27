from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint
from database import Base


class Chamado(Base):
    __tablename__ = "chamado"

    id_chamado = Column(Integer, primary_key=True, autoincrement=True)
    descricao_problema = Column(String, nullable=False)
    nivel_urgencia = Column(String, nullable=False)
    data_abertura = Column(String, nullable=False)
    status_chamado = Column(String, nullable=False, default="aberto")
    id_equipamento = Column(Integer, ForeignKey("equipamento.id_equipamento"), nullable=False)
    id_usuario_abertura = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    id_setor = Column(Integer, ForeignKey("setor.id_setor"), nullable=False)

    __table_args__ = (
        CheckConstraint("nivel_urgencia IN ('A','B','C')", name="ck_urgencia"),
        CheckConstraint(
            "status_chamado IN ('aberto','em_andamento','fechado')",
            name="ck_status_chamado",
        ),
    )
