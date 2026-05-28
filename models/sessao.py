from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base


class Sessao(Base):
    __tablename__ = "sessao"

    id_sessao = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String, nullable=False, unique=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
