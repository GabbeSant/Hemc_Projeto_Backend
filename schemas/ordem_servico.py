from typing import Literal, Optional
from pydantic import BaseModel

TipoOS = Literal["preventiva", "corretiva"]
StatusOS = Literal["aberta", "em_execucao", "concluida", "cancelada"]


class OrdemServicoCreate(BaseModel):
    tipo: TipoOS
    data_programada: Optional[str] = None
    id_equipamento: int
    id_chamado: Optional[int] = None


class OrdemServicoUpdate(BaseModel):
    status_os: Optional[StatusOS] = None
    data_programada: Optional[str] = None


class OrdemServicoOut(BaseModel):
    id_os: int
    tipo: str
    data_geracao: str
    data_programada: Optional[str]
    status_os: str
    id_equipamento: int
    id_chamado: Optional[int]

    model_config = {"from_attributes": True}
