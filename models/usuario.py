from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint
from database import Base


class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    perfil = Column(String, nullable=False)
    id_setor = Column(Integer, ForeignKey("setor.id_setor"), nullable=False)
    senha_hash = Column(String, nullable=True)

    __table_args__ = (
        CheckConstraint("perfil IN ('admin','enfermeira','tecnico')", name="ck_perfil"),
    )
