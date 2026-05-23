from sqlalchemy import Column, Integer, String, Float, ForeignKey, CheckConstraint
from database import Base


class Equipamento(Base):
    __tablename__ = "equipamento"

    id_equipamento = Column(Integer, primary_key=True, autoincrement=True)
    num_patrimonio = Column(String, nullable=False, unique=True)
    modelo = Column(String)
    num_serie = Column(String)
    data_aquisicao = Column(String)        # ISO 'AAAA-MM-DD'
    valor_aquisicao = Column(Float)
    grau_criticidade = Column(String, nullable=False)
    frequencia_preventiva = Column(String, nullable=False)
    status_atual = Column(String, nullable=False, default="em_funcionamento")
    id_setor = Column(Integer, ForeignKey("setor.id_setor"), nullable=False)
    id_tipo = Column(Integer, ForeignKey("tipo_equipamento.id_tipo"), nullable=False)
    id_fabricante = Column(Integer, ForeignKey("fabricante.id_fabricante"), nullable=False)

    __table_args__ = (
        CheckConstraint("grau_criticidade IN ('A','B','C')", name="ck_criticidade"),
        CheckConstraint(
            "frequencia_preventiva IN ('mensal','trimestral')",
            name="ck_frequencia",
        ),
        CheckConstraint(
            "status_atual IN ('em_funcionamento','em_manutencao','aguardando_reparo','fora_de_operacao')",
            name="ck_status",
        ),
    )
