from typing import Literal, Optional
from pydantic import BaseModel

NivelUrgencia = Literal["A", "B", "C"]
StatusChamado = Literal["aberto", "em_andamento", "fechado"]


class ChamadoCreate(BaseModel):
    descricao_problema: str
    nivel_urgencia: NivelUrgencia
    id_equipamento: int
    id_usuario_abertura: int
    id_setor: int


class ChamadoUpdate(BaseModel):
    status_chamado: Optional[StatusChamado] = None
    descricao_problema: Optional[str] = None
    nivel_urgencia: Optional[NivelUrgencia] = None


class ChamadoOut(BaseModel):
    id_chamado: int
    descricao_problema: str
    nivel_urgencia: str
    data_abertura: str
    status_chamado: str
    id_equipamento: int
    id_usuario_abertura: int
    id_setor: int

    model_config = {"from_attributes": True}
