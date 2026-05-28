from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.catalogs import Fabricante, Setor, TipoEquipamento, Unidade
from models.usuario import Usuario
from routes.auth import get_current_user

router = APIRouter(tags=["Catálogos"])


@router.get("/unidades")
def listar_unidades(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return [{"id_unidade": u.id_unidade, "nome_unidade": u.nome_unidade}
            for u in db.query(Unidade).all()]


@router.get("/setores")
def listar_setores(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return [{"id_setor": s.id_setor, "nome_setor": s.nome_setor, "id_unidade": s.id_unidade}
            for s in db.query(Setor).all()]


@router.get("/tipos")
def listar_tipos(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return [{"id_tipo": t.id_tipo, "nome_tipo": t.nome_tipo} for t in db.query(TipoEquipamento).all()]


@router.get("/fabricantes")
def listar_fabricantes(db: Session = Depends(get_db), _: Usuario = Depends(get_current_user)):
    return [{"id_fabricante": f.id_fabricante, "nome_fabricante": f.nome_fabricante} for f in db.query(Fabricante).all()]
