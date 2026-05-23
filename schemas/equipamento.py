from typing import Literal, Optional
from pydantic import BaseModel


Criticidade = Literal["A", "B", "C"]
Frequencia = Literal["mensal", "trimestral"]
StatusEquipamento = Literal[
    "em_funcionamento", "em_manutencao", "aguardando_reparo", "fora_de_operacao"
]


class EquipamentoBase(BaseModel):
    num_patrimonio: str
    modelo: Optional[str] = None
    num_serie: Optional[str] = None
    data_aquisicao: Optional[str] = None   # formato AAAA-MM-DD
    valor_aquisicao: Optional[float] = None
    grau_criticidade: Criticidade
    frequencia_preventiva: Frequencia
    status_atual: StatusEquipamento = "em_funcionamento"
    id_setor: int
    id_tipo: int
    id_fabricante: int


class EquipamentoCreate(EquipamentoBase):
    pass


class EquipamentoUpdate(BaseModel):
    num_patrimonio: Optional[str] = None
    modelo: Optional[str] = None
    num_serie: Optional[str] = None
    data_aquisicao: Optional[str] = None
    valor_aquisicao: Optional[float] = None
    grau_criticidade: Optional[Criticidade] = None
    frequencia_preventiva: Optional[Frequencia] = None
    status_atual: Optional[StatusEquipamento] = None
    id_setor: Optional[int] = None
    id_tipo: Optional[int] = None
    id_fabricante: Optional[int] = None


class EquipamentoOut(EquipamentoBase):
    id_equipamento: int

    model_config = {"from_attributes": True}
