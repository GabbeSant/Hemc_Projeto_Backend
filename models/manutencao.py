from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint
from database import Base


class Manutencao(Base):
    __tablename__ = "manutencao"

    id_manutencao = Column(Integer, primary_key=True, autoincrement=True)
    tipo = Column(String, nullable=False)
    data_execucao = Column(String, nullable=False)
    id_equipamento = Column(Integer, ForeignKey("equipamento.id_equipamento"), nullable=False)
    id_responsavel = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    id_os = Column(Integer, ForeignKey("ordem_servico.id_os"), nullable=False, unique=True)

    __table_args__ = (
        CheckConstraint("tipo IN ('preventiva','corretiva')", name="ck_tipo_manut"),
    )


class ManutencaoPreventiva(Base):
    __tablename__ = "manutencao_preventiva"

    id_manutencao = Column(
        Integer,
        ForeignKey("manutencao.id_manutencao", ondelete="CASCADE"),
        primary_key=True,
    )
    houve_substituicao = Column(Integer, nullable=False, default=0)
    checklist_concluido = Column(Integer, nullable=False, default=0)


class ManutencaoCorretiva(Base):
    __tablename__ = "manutencao_corretiva"

    id_manutencao = Column(
        Integer,
        ForeignKey("manutencao.id_manutencao", ondelete="CASCADE"),
        primary_key=True,
    )
    descricao_reparo = Column(String)
    testes_finais = Column(String)
    status_resultante = Column(String)

    __table_args__ = (
        CheckConstraint(
            "status_resultante IN ('em_funcionamento','em_manutencao','aguardando_reparo','fora_de_operacao')",
            name="ck_status_resultante",
        ),
    )


class Peca(Base):
    __tablename__ = "peca"

    id_peca = Column(Integer, primary_key=True, autoincrement=True)
    nome_peca = Column(String, nullable=False)
    codigo = Column(String)


class PecaSubstituida(Base):
    __tablename__ = "peca_substituida"

    id_manutencao = Column(
        Integer,
        ForeignKey("manutencao.id_manutencao", ondelete="CASCADE"),
        primary_key=True,
    )
    id_peca = Column(Integer, ForeignKey("peca.id_peca"), primary_key=True)
    quantidade = Column(Integer, nullable=False, default=1)


class ChecklistItem(Base):
    __tablename__ = "checklist_item"

    id_item = Column(Integer, primary_key=True, autoincrement=True)
    descricao_teste = Column(String, nullable=False)
    tipo_teste = Column(String, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "tipo_teste IN ('seguranca','calibracao')",
            name="ck_tipo_teste",
        ),
    )


class ManutencaoChecklist(Base):
    __tablename__ = "manutencao_checklist"

    id_manutencao = Column(
        Integer,
        ForeignKey("manutencao_preventiva.id_manutencao", ondelete="CASCADE"),
        primary_key=True,
    )
    id_item = Column(Integer, ForeignKey("checklist_item.id_item"), primary_key=True)
    resultado = Column(String, nullable=False)
    observacao = Column(String)

    __table_args__ = (
        CheckConstraint(
            "resultado IN ('aprovado','reprovado','nao_aplicavel')",
            name="ck_resultado",
        ),
    )
