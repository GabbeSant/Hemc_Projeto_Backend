from typing import Literal, Optional
from pydantic import BaseModel

StatusEquip = Literal["em_funcionamento", "em_manutencao", "aguardando_reparo", "fora_de_operacao"]
ResultadoChecklist = Literal["aprovado", "reprovado", "nao_aplicavel"]


class PecaSubstituidaIn(BaseModel):
    id_peca: int
    quantidade: int = 1


class ChecklistItemIn(BaseModel):
    id_item: int
    resultado: ResultadoChecklist
    observacao: Optional[str] = None


class ManutencaoPreventivaCreate(BaseModel):
    id_os: int
    id_equipamento: int
    id_responsavel: int
    houve_substituicao: bool = False
    pecas: list[PecaSubstituidaIn] = []
    checklist: list[ChecklistItemIn] = []


class ManutencaoCorretivaCreate(BaseModel):
    id_os: int
    id_equipamento: int
    id_responsavel: int
    descricao_reparo: Optional[str] = None
    testes_finais: Optional[str] = None
    status_resultante: StatusEquip = "em_funcionamento"
    pecas: list[PecaSubstituidaIn] = []


class ManutencaoOut(BaseModel):
    id_manutencao: int
    tipo: str
    data_execucao: str
    id_equipamento: int
    id_responsavel: int
    id_os: int

    model_config = {"from_attributes": True}
