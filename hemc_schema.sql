-- =============================================================================
-- HEMC - Controle de Manutenção de Equipamentos Hospitalares
-- Esquema do banco de dados (SGBD: SQLite) - Normalizado até a 3FN
-- =============================================================================
-- Decisões de modelagem refletidas neste script:
--   * Especialização total e disjunta (t,d) de Manutenção em preventiva/corretiva
--     -> tabela supertipo "manutencao" + duas tabelas subtipo que herdam a PK.
--   * Relacionamentos N:M (peças substituídas, checklist) resolvidos com
--     tabelas associativas que carregam seus próprios atributos.
--   * Domínios fixos (criticidade, frequência, status, etc.) controlados por
--     CHECK, pois são códigos sem atributos próprios (não viram entidade).
--   * Dados derivados (indicadores REQ16) NÃO são armazenados: serão VIEWs/consultas.
-- =============================================================================

-- O SQLite só aplica integridade referencial se as FKs forem habilitadas.
-- Esta diretiva deve ser executada a cada conexão.
PRAGMA foreign_keys = ON;

-- -----------------------------------------------------------------------------
-- 1. LOCALIZAÇÃO E CATÁLOGOS
-- -----------------------------------------------------------------------------

-- Unidade hospitalar (1:N com Setor)
CREATE TABLE unidade (
    id_unidade    INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_unidade  TEXT NOT NULL
);

-- Setor pertence a uma unidade (REQ19). A FK id_unidade materializa o
-- relacionamento "Tem"; a unidade é deduzida pelo setor, evitando dependência
-- transitiva no chamado (3FN).
CREATE TABLE setor (
    id_setor    INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_setor  TEXT NOT NULL,
    id_unidade  INTEGER NOT NULL,
    FOREIGN KEY (id_unidade) REFERENCES unidade (id_unidade)
);

-- Fabricante do equipamento (extraído de equipamento para evitar repetição -> 3FN)
CREATE TABLE fabricante (
    id_fabricante    INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_fabricante  TEXT NOT NULL
);

-- Tipo de equipamento (catálogo)
CREATE TABLE tipo_equipamento (
    id_tipo    INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_tipo  TEXT NOT NULL,
    descricao  TEXT
);

-- Usuário do sistema. Um único conceito para Administrador, Enfermeira e
-- Técnico, diferenciados pelo atributo "perfil" (REQ15). Pertence a um setor.
CREATE TABLE usuario (
    id_usuario  INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        TEXT NOT NULL,
    perfil      TEXT NOT NULL CHECK (perfil IN ('admin', 'enfermeira', 'tecnico')),
    id_setor    INTEGER NOT NULL,
    FOREIGN KEY (id_setor) REFERENCES setor (id_setor)
);

-- -----------------------------------------------------------------------------
-- 2. EQUIPAMENTO (núcleo do sistema - REQ1 a REQ7)
-- -----------------------------------------------------------------------------
CREATE TABLE equipamento (
    id_equipamento        INTEGER PRIMARY KEY AUTOINCREMENT,
    num_patrimonio        TEXT NOT NULL UNIQUE,
    modelo                TEXT,
    num_serie             TEXT,
    data_aquisicao        TEXT,   -- data ISO 'AAAA-MM-DD'
    valor_aquisicao       REAL,
    -- Domínios fixos controlados por CHECK:
    grau_criticidade      TEXT NOT NULL CHECK (grau_criticidade IN ('A', 'B', 'C')),       -- REQ2
    frequencia_preventiva TEXT NOT NULL CHECK (frequencia_preventiva IN ('mensal', 'trimestral')), -- REQ3
    status_atual          TEXT NOT NULL DEFAULT 'em_funcionamento'
                          CHECK (status_atual IN ('em_funcionamento', 'em_manutencao',
                                                  'aguardando_reparo', 'fora_de_operacao')), -- REQ24
    -- Relacionamentos: cada equipamento tem 1 setor, 1 tipo e 1 fabricante.
    id_setor       INTEGER NOT NULL,
    id_tipo        INTEGER NOT NULL,
    id_fabricante  INTEGER NOT NULL,
    FOREIGN KEY (id_setor)      REFERENCES setor (id_setor),
    FOREIGN KEY (id_tipo)       REFERENCES tipo_equipamento (id_tipo),
    FOREIGN KEY (id_fabricante) REFERENCES fabricante (id_fabricante)
);

-- -----------------------------------------------------------------------------
-- 3. CHAMADO (manutenção corretiva - REQ18, REQ19)
-- -----------------------------------------------------------------------------
-- Aberto por um usuário (enfermeira ou técnico) sobre um equipamento.
-- O setor de origem é registrado diretamente; a unidade vem por setor->unidade.
CREATE TABLE chamado (
    id_chamado         INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao_problema TEXT NOT NULL,
    nivel_urgencia     TEXT NOT NULL CHECK (nivel_urgencia IN ('A', 'B', 'C')),
    data_abertura      TEXT NOT NULL DEFAULT (datetime('now')),
    status_chamado     TEXT NOT NULL DEFAULT 'aberto'
                       CHECK (status_chamado IN ('aberto', 'em_andamento', 'fechado')),
    id_equipamento     INTEGER NOT NULL,
    id_usuario_abertura INTEGER NOT NULL,  -- quem abriu (relacionamento "Abre")
    id_setor           INTEGER NOT NULL,   -- setor de origem do chamado
    FOREIGN KEY (id_equipamento)      REFERENCES equipamento (id_equipamento),
    FOREIGN KEY (id_usuario_abertura) REFERENCES usuario (id_usuario),
    FOREIGN KEY (id_setor)            REFERENCES setor (id_setor)
);

-- -----------------------------------------------------------------------------
-- 4. ORDEM DE SERVIÇO (REQ8)
-- -----------------------------------------------------------------------------
-- Gerada automaticamente (preventiva) ou a partir de um chamado (corretiva).
-- id_chamado é NULO para OS preventiva -> cardinalidade (0,1) do lado do chamado.
CREATE TABLE ordem_servico (
    id_os           INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo            TEXT NOT NULL CHECK (tipo IN ('preventiva', 'corretiva')),
    data_geracao    TEXT NOT NULL DEFAULT (datetime('now')),
    data_programada TEXT,           -- usada nos alertas de vencimento (REQ9)
    status_os       TEXT NOT NULL DEFAULT 'aberta'
                    CHECK (status_os IN ('aberta', 'em_execucao', 'concluida', 'cancelada')),
    id_equipamento  INTEGER NOT NULL,
    id_chamado      INTEGER,        -- NULL = OS preventiva (sem chamado de origem)
    FOREIGN KEY (id_equipamento) REFERENCES equipamento (id_equipamento),
    FOREIGN KEY (id_chamado)     REFERENCES chamado (id_chamado)
);

-- -----------------------------------------------------------------------------
-- 5. MANUTENÇÃO - SUPERTIPO + SUBTIPOS (especialização total e disjunta)
-- -----------------------------------------------------------------------------
-- O supertipo guarda o que é comum a toda manutenção (REQ14/REQ23: é o
-- histórico do equipamento). O campo "tipo" é o discriminador da especialização.
-- Cada manutenção pertence a 1 equipamento, 1 responsável e 1 OS.
CREATE TABLE manutencao (
    id_manutencao   INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo            TEXT NOT NULL CHECK (tipo IN ('preventiva', 'corretiva')), -- REQ25
    data_execucao   TEXT NOT NULL DEFAULT (datetime('now')),
    id_equipamento  INTEGER NOT NULL,  -- "Sofre"  (1,1)
    id_responsavel  INTEGER NOT NULL,  -- "Executa" (1,1) - usuário técnico (REQ15)
    id_os           INTEGER NOT NULL UNIQUE, -- "Gera" - 1 OS gera no máximo 1 manutenção
    FOREIGN KEY (id_equipamento) REFERENCES equipamento (id_equipamento),
    FOREIGN KEY (id_responsavel) REFERENCES usuario (id_usuario),
    FOREIGN KEY (id_os)          REFERENCES ordem_servico (id_os)
);

-- Subtipo PREVENTIVA: a PK é a mesma do supertipo (FK + PK simultâneas).
-- O ON DELETE CASCADE garante que apagar a manutenção apaga o subtipo.
CREATE TABLE manutencao_preventiva (
    id_manutencao       INTEGER PRIMARY KEY,
    houve_substituicao  INTEGER NOT NULL DEFAULT 0 CHECK (houve_substituicao IN (0, 1)), -- REQ13 (booleano)
    checklist_concluido INTEGER NOT NULL DEFAULT 0 CHECK (checklist_concluido IN (0, 1)),
    FOREIGN KEY (id_manutencao) REFERENCES manutencao (id_manutencao) ON DELETE CASCADE
);

-- Subtipo CORRETIVA (REQ20, REQ22, REQ24)
CREATE TABLE manutencao_corretiva (
    id_manutencao     INTEGER PRIMARY KEY,
    descricao_reparo  TEXT,            -- serviços realizados (REQ20)
    testes_finais     TEXT,            -- testes após o reparo (REQ22)
    status_resultante TEXT CHECK (status_resultante IN ('em_funcionamento', 'em_manutencao',
                                                        'aguardando_reparo', 'fora_de_operacao')),
    FOREIGN KEY (id_manutencao) REFERENCES manutencao (id_manutencao) ON DELETE CASCADE
);

-- -----------------------------------------------------------------------------
-- 6. PEÇAS E CHECKLIST (relacionamentos N:M com atributos próprios)
-- -----------------------------------------------------------------------------

-- Catálogo de peças (REQ13, REQ21)
CREATE TABLE peca (
    id_peca    INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_peca  TEXT NOT NULL,
    codigo     TEXT
);

-- Associativa Manutenção <-> Peça ("Substitui"). PK composta.
-- O atributo "quantidade" só faz sentido na combinação dos dois -> fica aqui.
CREATE TABLE peca_substituida (
    id_manutencao  INTEGER NOT NULL,
    id_peca        INTEGER NOT NULL,
    quantidade     INTEGER NOT NULL DEFAULT 1 CHECK (quantidade > 0),
    PRIMARY KEY (id_manutencao, id_peca),
    FOREIGN KEY (id_manutencao) REFERENCES manutencao (id_manutencao) ON DELETE CASCADE,
    FOREIGN KEY (id_peca)       REFERENCES peca (id_peca)
);

-- Catálogo de itens de checklist (REQ12: testes de segurança e calibração)
CREATE TABLE checklist_item (
    id_item         INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao_teste TEXT NOT NULL,
    tipo_teste      TEXT NOT NULL CHECK (tipo_teste IN ('seguranca', 'calibracao'))
);

-- Associativa manutencao_preventiva <-> checklist_item ("Verifica").
-- O checklist é específico da preventiva, por isso liga ao subtipo.
CREATE TABLE manutencao_checklist (
    id_manutencao  INTEGER NOT NULL,
    id_item        INTEGER NOT NULL,
    resultado      TEXT NOT NULL CHECK (resultado IN ('aprovado', 'reprovado', 'nao_aplicavel')),
    observacao     TEXT,
    PRIMARY KEY (id_manutencao, id_item),
    FOREIGN KEY (id_manutencao) REFERENCES manutencao_preventiva (id_manutencao) ON DELETE CASCADE,
    FOREIGN KEY (id_item)       REFERENCES checklist_item (id_item)
);

-- -----------------------------------------------------------------------------
-- 7. INDICADORES (REQ16) - dados DERIVADOS, modelados como VIEW (não armazenados)
-- -----------------------------------------------------------------------------
-- Exemplo: total de manutenções e equipamentos com manutenção vencida.
CREATE VIEW vw_indicadores_equipamento AS
SELECT
    e.id_equipamento,
    e.num_patrimonio,
    e.grau_criticidade,
    e.status_atual,
    COUNT(m.id_manutencao)                                          AS total_manutencoes,
    SUM(CASE WHEN m.tipo = 'preventiva' THEN 1 ELSE 0 END)          AS total_preventivas,
    SUM(CASE WHEN m.tipo = 'corretiva'  THEN 1 ELSE 0 END)          AS total_corretivas,
    MAX(m.data_execucao)                                           AS ultima_manutencao
FROM equipamento e
LEFT JOIN manutencao m ON m.id_equipamento = e.id_equipamento
GROUP BY e.id_equipamento;

-- Alertas de vencimento (REQ9/REQ10): OS preventivas com data programada
-- vencida ou próxima do vencimento.
CREATE VIEW vw_alertas_vencimento AS
SELECT
    os.id_os,
    os.id_equipamento,
    e.num_patrimonio,
    e.grau_criticidade,
    os.data_programada,
    CASE
        WHEN os.data_programada < date('now') THEN 'VENCIDO'
        ELSE 'PROXIMO'
    END AS situacao
FROM ordem_servico os
JOIN equipamento e ON e.id_equipamento = os.id_equipamento
WHERE os.tipo = 'preventiva'
  AND os.status_os IN ('aberta', 'em_execucao')
  AND os.data_programada <= date('now', '+7 days');
