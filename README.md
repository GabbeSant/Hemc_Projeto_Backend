# HEMC — Controle de Manutenção de Equipamentos Hospitalares

Sistema backend para gerenciamento de manutenções (preventivas e corretivas) de equipamentos médicos hospitalares, desenvolvido com FastAPI e SQLite.

---

## Tecnologias

| Camada       | Tecnologia                        |
|--------------|-----------------------------------|
| Framework    | FastAPI (Python)                  |
| ORM          | SQLAlchemy                        |
| Banco        | SQLite (`hemc.db`)                |
| Servidor     | Uvicorn                           |
| Frontend     | HTML + CSS + JavaScript (estático)|

---

## Instalação e execução

```bash
# Instalar dependências
pip install -r requirements.txt

# Iniciar o servidor (modo desenvolvimento)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

A aplicação estará disponível em `http://localhost:8000`.  
Documentação interativa (Swagger): `http://localhost:8000/docs`.

---

## Endpoints

### Equipamentos

| Método   | Rota                          | Descrição                       |
|----------|-------------------------------|---------------------------------|
| `GET`    | `/equipamentos/`              | Lista todos os equipamentos      |
| `GET`    | `/equipamentos/{id}`          | Retorna um equipamento pelo ID   |
| `POST`   | `/equipamentos/`              | Cadastra novo equipamento        |
| `PUT`    | `/equipamentos/{id}`          | Atualiza equipamento (parcial ou total) |
| `DELETE` | `/equipamentos/{id}`          | Remove equipamento               |

### Catálogos (tabelas de apoio)

| Método | Rota          | Descrição                   |
|--------|---------------|-----------------------------|
| `GET`  | `/setores`    | Lista setores hospitalares  |
| `GET`  | `/tipos`      | Lista tipos de equipamento  |
| `GET`  | `/fabricantes`| Lista fabricantes            |

### Utilitários

| Método | Rota     | Descrição                                        |
|--------|----------|--------------------------------------------------|
| `GET`  | `/`      | Interface web (SPA)                              |
| `POST` | `/seed`  | Popula o banco com dados de exemplo (idempotente)|

---

## Modelo de dados

### Equipamento

Campo                | Tipo/Domínio                                                               | Descrição
---------------------|----------------------------------------------------------------------------|----------------------------------
`num_patrimonio`     | `TEXT UNIQUE`                                                              | Número de patrimônio (identificador único)
`modelo`             | `TEXT`                                                                     | Modelo do equipamento
`num_serie`          | `TEXT`                                                                     | Número de série
`data_aquisicao`     | `DATE`                                                                     | Data de aquisição (`AAAA-MM-DD`)
`valor_aquisicao`    | `REAL`                                                                     | Valor de aquisição
`criticidade`        | `A` / `B` / `C`                                                            | Nível de criticidade
`freq_preventiva`    | `mensal` / `trimestral`                                                    | Frequência de manutenção preventiva
`status`             | `em_funcionamento` / `em_manutencao` / `aguardando_reparo` / `fora_de_operacao` | Status operacional

### Catálogos

- **`unidade`** — Unidades hospitalares
- **`setor`** — Setores (vinculados a uma unidade)
- **`fabricante`** — Fabricantes de equipamentos
- **`tipo_equipamento`** — Tipos de equipamento com descrição
- **`usuario`** — Usuários do sistema com perfis: `admin`, `tecnico`, `enfermagem`

### Manutenções

- **`chamado`** — Chamados de manutenção corretiva abertos por usuários, com urgência (A/B/C) e status (`aberto`, `em_andamento`, `fechado`)
- **`ordem_servico`** — Ordens de serviço (preventivas ou corretivas), com data programada
- **`manutencao`** — Registro histórico imutável de manutenções executadas
  - `manutencao_preventiva` — inclui checklist e registro de substituição de peças
  - `manutencao_corretiva` — inclui descrição do reparo, testes finais e status resultante

### Peças e Checklists

- **`peca`** — Catálogo de peças
- **`peca_substituida`** — Peças substituídas por manutenção (com quantidade)
- **`checklist_item`** — Itens de verificação (`seguranca` ou `calibracao`)
- **`manutencao_checklist`** — Resultado dos itens: `aprovado`, `reprovado`, `nao_aplicavel`

### Views (dados derivados)

- **`vw_indicadores_equipamento`** — Totais de manutenção por equipamento e data da última execução
- **`vw_alertas_vencimento`** — Equipamentos com manutenção preventiva vencida ou próxima do vencimento

---

## Funcionalidades

### Gestão de Equipamentos
- Cadastro completo com número de patrimônio único
- Classificação por criticidade (A, B, C) e frequência preventiva (mensal/trimestral)
- Controle de status operacional

### Manutenção Preventiva
- Gerada automaticamente conforme cronograma
- Independente de chamados
- Inclui checklist de segurança e calibração
- Registro de substituição de peças

### Manutenção Corretiva
- Originada a partir de chamados abertos por usuários
- Priorizada por nível de urgência (A, B, C)
- Executada por técnico responsável
- Documenta reparos, testes finais e status resultante

### Histórico Imutável
- Registros de manutenção nunca são deletados (regra de negócio)
- Rastreabilidade completa por equipamento

### Alertas
- View dedicada para equipamentos com preventiva vencida ou prestes a vencer
- Indicadores de quantidade e tipo de manutenções por equipamento

---

## Estrutura de pastas

```
Hemc_Projeto_Backend/
├── models/          # Modelos SQLAlchemy (ORM)
│   ├── catalogs.py
│   └── equipamento.py
├── routes/          # Endpoints FastAPI
│   ├── catalogs.py
│   └── equipamento.py
├── schemas/         # Schemas Pydantic (validação)
│   └── equipamento.py
├── static/          # Interface web
│   ├── index.html
│   └── style.css
├── database.py      # Configuração do banco e sessão
├── main.py          # Entrypoint da aplicação
├── hemc_schema.sql  # Schema completo do banco (referência)
└── requirements.txt
```

---

## Regras de negócio

- Manutenções preventivas são independentes de chamados e geradas por cronograma
- Manutenções corretivas dependem de um chamado aberto
- Nenhum registro de manutenção pode ser deletado
- Peças substituídas são vinculadas à manutenção com quantidade
- Checklists são obrigatórios na manutenção preventiva
- Foreign keys habilitados no SQLite via `PRAGMA foreign_keys = ON`
