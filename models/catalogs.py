from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class Unidade(Base):
    __tablename__ = "unidade"

    id_unidade = Column(Integer, primary_key=True, autoincrement=True)
    nome_unidade = Column(String, nullable=False)


class Setor(Base):
    __tablename__ = "setor"

    id_setor = Column(Integer, primary_key=True, autoincrement=True)
    nome_setor = Column(String, nullable=False)
    id_unidade = Column(Integer, ForeignKey("unidade.id_unidade"), nullable=False)


class Fabricante(Base):
    __tablename__ = "fabricante"

    id_fabricante = Column(Integer, primary_key=True, autoincrement=True)
    nome_fabricante = Column(String, nullable=False)


class TipoEquipamento(Base):
    __tablename__ = "tipo_equipamento"

    id_tipo = Column(Integer, primary_key=True, autoincrement=True)
    nome_tipo = Column(String, nullable=False)
    descricao = Column(String)
