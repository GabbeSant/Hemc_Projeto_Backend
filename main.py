from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import database
from models import catalogs as _catalog_models      # noqa: F401
from models import equipamento as _equip_model      # noqa: F401
from models import usuario as _usuario_model        # noqa: F401
from models import chamado as _chamado_model        # noqa: F401
from models import ordem_servico as _os_model       # noqa: F401
from models import manutencao as _manut_model       # noqa: F401
from models.catalogs import Fabricante, Setor, TipoEquipamento, Unidade
from models.usuario import Usuario
from models.manutencao import ChecklistItem, Peca
from routes.catalogs import router as catalogs_router
from routes.equipamento import router as equipamento_router
from routes.chamado import router as chamado_router
from routes.ordem_servico import router as os_router
from routes.manutencao import router as manut_router
from routes.usuario import router as usuario_router

app = FastAPI(title="HEMC - Controle de Manutenção de Equipamentos Hospitalares")

database.Base.metadata.create_all(bind=database.engine)

app.include_router(equipamento_router, prefix="/api")
app.include_router(catalogs_router, prefix="/api")
app.include_router(chamado_router, prefix="/api")
app.include_router(os_router, prefix="/api")
app.include_router(manut_router, prefix="/api")
app.include_router(usuario_router, prefix="/api")

# Serve cada subdiretório no caminho que o HTML já referencia
app.mount("/css", StaticFiles(directory="static/css"), name="css")
app.mount("/images-DEV-EV", StaticFiles(directory="static/images-DEV-EV"), name="images-dev")
app.mount("/Images", StaticFiles(directory="static/Images"), name="images")
app.mount("/fonts", StaticFiles(directory="static/fonts"), name="fonts")
app.mount("/js", StaticFiles(directory="static/js"), name="js")
app.mount("/pages", StaticFiles(directory="static/pages", html=True), name="pages")


@app.get("/api/indicadores", tags=["Indicadores"])
def indicadores(db: Session = Depends(database.get_db)):
    from models.equipamento import Equipamento
    from models.chamado import Chamado
    from models.ordem_servico import OrdemServico as OS
    from models.manutencao import Manutencao

    total = db.query(Equipamento).count()
    criticos = db.query(Equipamento).filter(Equipamento.grau_criticidade == "A").count()
    em_reparo = db.query(Equipamento).filter(
        Equipamento.status_atual.in_(["em_manutencao", "aguardando_reparo"])
    ).count()
    fora = db.query(Equipamento).filter(Equipamento.status_atual == "fora_de_operacao").count()
    operando = db.query(Equipamento).filter(Equipamento.status_atual == "em_funcionamento").count()

    chamados_abertos = db.query(Chamado).filter(Chamado.status_chamado != "fechado").count()
    chamados_fechados = db.query(Chamado).filter(Chamado.status_chamado == "fechado").count()

    os_abertas = db.query(OS).filter(OS.status_os.in_(["aberta", "em_execucao"])).count()
    os_concluidas = db.query(OS).filter(OS.status_os == "concluida").count()

    preventivas = db.query(Manutencao).filter(Manutencao.tipo == "preventiva").count()
    corretivas = db.query(Manutencao).filter(Manutencao.tipo == "corretiva").count()
    total_manut = preventivas + corretivas

    conformidade = round((operando / total * 100) if total > 0 else 0)

    return {
        "total_equipamentos": total,
        "criticos": criticos,
        "em_reparo": em_reparo,
        "fora_de_operacao": fora,
        "operando": operando,
        "conformidade": conformidade,
        "chamados_abertos": chamados_abertos,
        "chamados_fechados": chamados_fechados,
        "os_abertas": os_abertas,
        "os_concluidas": os_concluidas,
        "total_manutencoes": total_manut,
        "preventivas": preventivas,
        "corretivas": corretivas,
    }


@app.get("/", include_in_schema=False)
def frontend():
    return FileResponse("static/index.html")


@app.post("/seed", include_in_schema=False, status_code=200)
def seed(db: Session = Depends(database.get_db)):
    """Popula o banco com dados de exemplo. Cada bloco só insere se ainda estiver vazio."""
    adicionado = []

    # --- Catálogos base (unidade, setores, tipos, fabricantes) ---
    if db.query(Unidade).count() == 0:
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

        db.flush()
        adicionado.append("catalogos")

    # --- Usuários (inseridos separadamente para sobreviver a seeds parciais) ---
    if db.query(Usuario).count() == 0:
        setor_uti = db.query(Setor).filter(Setor.nome_setor == "UTI").first()
        setor_cc  = db.query(Setor).filter(Setor.nome_setor == "Centro Cirúrgico").first()
        if setor_uti and setor_cc:
            for nome, perfil, setor in [
                ("Rafaela Lima",   "enfermeira", setor_uti),
                ("Carlos Santos",  "tecnico",    setor_uti),
                ("Ana Oliveira",   "enfermeira", setor_cc),
                ("Admin Sistema",  "admin",      setor_uti),
            ]:
                db.add(Usuario(nome=nome, perfil=perfil, id_setor=setor.id_setor))
            adicionado.append("usuarios")

    # --- Checklist e peças ---
    if db.query(ChecklistItem).count() == 0:
        for descricao, tipo in [
            ("Verificar cabos e conectores",           "seguranca"),
            ("Testar alarmes sonoros e visuais",       "seguranca"),
            ("Calibrar sensor de SpO2",                "calibracao"),
            ("Verificar leitura de pressão arterial",  "calibracao"),
            ("Limpar filtros e telas",                 "seguranca"),
            ("Testar bateria e nobreak",               "seguranca"),
        ]:
            db.add(ChecklistItem(descricao_teste=descricao, tipo_teste=tipo))
        adicionado.append("checklist")

    if db.query(Peca).count() == 0:
        for nome, codigo in [
            ("Filtro HEPA",         "FLT-001"),
            ("Sensor de SpO2",      "SNS-002"),
            ("Cabo de ECG",         "CAB-003"),
            ("Bateria 12V",         "BAT-004"),
            ("Manguito adulto",     "MNG-005"),
        ]:
            db.add(Peca(nome_peca=nome, codigo=codigo))
        adicionado.append("pecas")

    if not adicionado:
        return {"status": "ja_populado", "msg": "Banco já contém dados."}

    db.commit()
    return {"status": "ok", "msg": f"Inserido: {', '.join(adicionado)}."}
