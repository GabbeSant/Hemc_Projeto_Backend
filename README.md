# HEMC — Controle de Manutenção de Equipamentos Hospitalares

Sistema web para gestão de manutenção preventiva e corretiva de equipamentos médico-hospitalares.

## Tecnologias

- **Backend:** Python 3.13 · FastAPI · SQLAlchemy · Pydantic
- **Banco de dados:** SQLite
- **Frontend:** HTML · CSS · JavaScript (vanilla)

## Estrutura do Projeto

```
├── main.py               # Ponto de entrada da aplicação FastAPI
├── database.py           # Configuração do banco de dados (engine, sessão, Base)
├── hemc_schema.sql       # Esquema DDL documentado (normalizado até 3FN)
├── models/               # Modelos SQLAlchemy (tabelas do banco)
│   ├── equipamento.py
│   ├── chamado.py
│   ├── ordem_servico.py
│   ├── manutencao.py
│   ├── usuario.py
│   ├── sessao.py
│   └── catalogs.py
├── schemas/              # Schemas Pydantic (validação de entrada/saída da API)
│   ├── equipamento.py
│   ├── chamado.py
│   ├── ordem_servico.py
│   └── manutencao.py
├── routes/               # Roteadores FastAPI (endpoints da API)
│   ├── auth.py
│   ├── equipamento.py
│   ├── chamado.py
│   ├── ordem_servico.py
│   ├── manutencao.py
│   ├── catalogs.py
│   └── usuario.py
└── static/               # Frontend (servido diretamente pelo FastAPI)
    ├── pages/            # Páginas HTML
    ├── css/              # Estilos por página
    ├── js/               # Scripts JavaScript
    └── Images/           # Imagens, ícones e favicon
```

## Instalação

**Pré-requisito:** Python 3.11 ou superior.

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd Hemc_Projeto_Backend

# Crie e ative o ambiente virtual
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

# Instale as dependências
pip install fastapi uvicorn sqlalchemy pydantic
```

## Executando o servidor

```bash
uvicorn main:app --reload
```

O servidor estará disponível em **http://localhost:8000**.

## Populando o banco com dados de exemplo

Após iniciar o servidor pela primeira vez, execute:

```bash
curl -X POST http://localhost:8000/seed
```

Isso criará a unidade hospitalar, setores, tipos de equipamento, fabricantes, usuários, itens de checklist e peças iniciais.

**Credenciais padrão de todos os usuários criados pelo seed:** `senha123`

| Nome           | Perfil    |
|----------------|-----------|
| Rafaela Lima   | enfermeira |
| Carlos Santos  | tecnico   |
| Ana Oliveira   | enfermeira |
| Admin Sistema  | admin     |

## Acessando o sistema

Acesse **http://localhost:8000** e faça login com qualquer credencial da tabela acima.

## Documentação automática da API

O FastAPI gera documentação interativa automaticamente:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Endpoints principais

| Método | Endpoint                          | Descrição                                      | Perfil mínimo |
|--------|-----------------------------------|------------------------------------------------|---------------|
| POST   | `/api/login`                      | Autenticação — retorna token de sessão         | público       |
| POST   | `/api/logout`                     | Encerra a sessão atual                         | qualquer      |
| GET    | `/api/me`                         | Dados do usuário autenticado                   | qualquer      |
| GET    | `/api/indicadores`                | Indicadores do dashboard                       | qualquer      |
| GET    | `/api/equipamentos/`              | Lista todos os equipamentos                    | qualquer      |
| POST   | `/api/equipamentos/`              | Cadastra novo equipamento                      | admin         |
| PUT    | `/api/equipamentos/{id}`          | Atualiza equipamento                           | admin         |
| DELETE | `/api/equipamentos/{id}`          | Remove equipamento                             | admin         |
| GET    | `/api/chamados/`                  | Lista chamados                                 | qualquer      |
| POST   | `/api/chamados/`                  | Abre chamado + gera OS corretiva automaticamente | enfermeira  |
| GET    | `/api/ordens-servico/`            | Lista ordens de serviço                        | qualquer      |
| POST   | `/api/ordens-servico/gerar-preventivas` | Gera OS preventivas pendentes manualmente | admin    |
| POST   | `/api/manutencoes/preventiva`     | Registra manutenção preventiva                 | tecnico       |
| POST   | `/api/manutencoes/corretiva`      | Registra manutenção corretiva                  | tecnico       |
| GET    | `/api/manutencoes/pecas`          | Lista peças disponíveis                        | qualquer      |
| GET    | `/api/manutencoes/checklist-itens`| Lista itens de checklist                       | qualquer      |

## Perfis de acesso

| Perfil     | Permissões                                                        |
|------------|-------------------------------------------------------------------|
| admin      | Acesso total — CRUD de equipamentos, usuários, geração de OS      |
| tecnico    | Registra manutenções preventivas e corretivas                     |
| enfermeira | Abre chamados de manutenção corretiva                             |

## Banco de dados

O banco é criado automaticamente no primeiro start em `hemc.db`. As tabelas seguem o esquema documentado em `hemc_schema.sql`, normalizado até a 3FN, com:

- Especialização disjunta de `manutencao` em `manutencao_preventiva` e `manutencao_corretiva`
- Tabelas associativas para peças substituídas e checklist
- `CHECK CONSTRAINT` em todos os campos com domínio fixo
- `PRAGMA foreign_keys = ON` ativado a cada conexão

## Geração automática de OS preventivas

O sistema verifica automaticamente, a cada inicialização e a cada acesso ao dashboard, se algum equipamento está com manutenção preventiva vencida ou a menos de 7 dias do vencimento. Quando isso ocorre, uma OS preventiva é gerada sem intervenção do usuário, com base na frequência configurada por equipamento (mensal = 30 dias, trimestral = 90 dias).
