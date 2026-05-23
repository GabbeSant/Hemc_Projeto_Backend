# Stack
- FastAPI
- SQLite
- SQLAlchemy
- HTML/CSS/JS básico

# Regras
- Simplicidade acima de sofisticação
- Sem arquitetura enterprise
- Sem async avançado

# Estrutura
/models
/routes
/schemas

# Fluxos principais
1. Equipamento
2. Chamado
3. Ordem de serviço
4. Manutenção

# Regras importantes
- Preventiva não depende de chamado
- Corretiva depende
- Histórico não pode ser excluído