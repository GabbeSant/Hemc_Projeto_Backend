from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import database
from models import catalogs as _catalog_models   # noqa: F401
from models import equipamento as _equip_model   # noqa: F401
from models.catalogs import Fabricante, Setor, TipoEquipamento, Unidade
from routes.catalogs import router as catalogs_router
from routes.equipamento import router as equipamento_router

app = FastAPI(title="HEMC - Controle de Manutenção de Equipamentos Hospitalares")

database.Base.metadata.create_all(bind=database.engine)

app.include_router(equipamento_router)
app.include_router(catalogs_router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
def frontend():
    return FileResponse("static/index.html")


@app.post("/seed", include_in_schema=False, status_code=200)
def seed(db: Session = Depends(database.get_db)):
    """Popula o banco com dados de exemplo, se ainda estiver vazio."""
    if db.query(Unidade).count() > 0:
        return {"status": "ja_populado", "msg": "Banco já contém dados."}

    unidade = Unidade(nome_unidade="Hospital Central")
    db.add(unidade)
    db.flush()

    for nome in ["UTI", "Centro Cirúrgico", "Pronto-Socorro", "Maternidade"]:
        db.add(Setor(nome_setor=nome, id_unidade=unidade.id_unidade))

    for nome, desc in [
        ("Monitor Cardíaco",    "Monitoramento de sinais vitais"),
        ("Ventilador Mecânico", "Suporte ventilatório invasivo e não-invasivo"),
        ("Bomba de Infusão",    "Administração controlada de medicamentos IV"),
        ("Desfibrilador",       "Cardioversão e desfibrilação elétrica"),
    ]:
        db.add(TipoEquipamento(nome_tipo=nome, descricao=desc))

    for nome in ["Philips", "GE Healthcare", "Mindray", "Dräger"]:
        db.add(Fabricante(nome_fabricante=nome))

    db.commit()
    return {"status": "ok", "msg": "Dados de exemplo carregados com sucesso."}
