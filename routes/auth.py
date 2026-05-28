import hashlib
import secrets

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.sessao import Sessao
from models.usuario import Usuario

router = APIRouter(tags=["Autenticação"])


class LoginInput(BaseModel):
    nome: str
    senha: str


def _hash(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()


def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)) -> Usuario:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Não autorizado")
    token = authorization[7:]
    sessao = db.query(Sessao).filter(Sessao.token == token).first()
    if not sessao:
        raise HTTPException(status_code=401, detail="Sessão inválida")
    usuario = db.get(Usuario, sessao.id_usuario)
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return usuario


def require_admin(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    if usuario.perfil != "admin":
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores")
    return usuario


def require_tecnico(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    if usuario.perfil not in ("admin", "tecnico"):
        raise HTTPException(status_code=403, detail="Acesso restrito a técnicos")
    return usuario


def require_enfermeira(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    if usuario.perfil not in ("admin", "enfermeira"):
        raise HTTPException(status_code=403, detail="Acesso restrito a enfermeiras")
    return usuario


@router.post("/login")
def login(dados: LoginInput, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.nome == dados.nome).first()
    if not usuario or usuario.senha_hash != _hash(dados.senha):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    token = secrets.token_urlsafe(32)
    db.add(Sessao(token=token, id_usuario=usuario.id_usuario))
    db.commit()
    return {
        "token": token,
        "usuario": {
            "id_usuario": usuario.id_usuario,
            "nome": usuario.nome,
            "perfil": usuario.perfil,
        },
    }


@router.post("/logout")
def logout(authorization: str = Header(None), db: Session = Depends(get_db)):
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        sessao = db.query(Sessao).filter(Sessao.token == token).first()
        if sessao:
            db.delete(sessao)
            db.commit()
    return {"msg": "Logout realizado com sucesso"}


@router.get("/me")
def me(usuario: Usuario = Depends(get_current_user)):
    return {
        "id_usuario": usuario.id_usuario,
        "nome": usuario.nome,
        "perfil": usuario.perfil,
        "id_setor": usuario.id_setor,
    }
