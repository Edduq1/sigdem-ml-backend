from pydantic import BaseModel, ConfigDict


class TramiteMLClassifyRequest(BaseModel):
    tipo_tramite: str
    area_responsable: str
    dias_espera: int
    cantidad_documentos: int = 1
    tiene_observaciones: bool = False
    es_urgente: bool = False


class TramiteMLClassifyResponse(BaseModel):
    prioridad: str
    confidence: float


class TramiteMLTrainResponse(BaseModel):
    message: str
    accuracy: float
    total_samples: int


class TramiteMLMetricsResponse(BaseModel):
    model_name: str
    algorithm: str
    accuracy: float
    total_samples: int
    labels: list[str]

    model_config = ConfigDict(from_attributes=True)