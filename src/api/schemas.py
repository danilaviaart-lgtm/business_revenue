from pydantic import BaseModel
from pydantic import Field

class PredictInput(BaseModel):
    Administrative: int = Field(..., description="Número de páginas administrativas visitadas", example=0)
    Administrative_Duration: float = Field(..., description="Tiempo total en páginas administrativas", example=0.0)
    Informational: int = Field(..., description="Número de páginas informativas visitadas", example=0)
    Informational_Duration: float = Field(..., description="Tiempo total en páginas informativas", example=0.0)
    ProductRelated: int = Field(..., description="Número de páginas relacionadas con productos visitadas", example=1)
    ProductRelated_Duration: float = Field(..., description="Tiempo total en páginas de productos", example=11.25)
    BounceRates: float = Field(..., description="Porcentaje de rebote de la página", example=0.0)
    ExitRates: float = Field(..., description="Porcentaje de salida de la página", example=0.1)
    PageValues: float = Field(..., description="Valor medio de la página web", example=0.0)
    Nombre_cliente: str = Field(..., description="Nombre del cliente", example="Beatriz Barreda")
    SpecialDay: float = Field(..., description="Cercanía a una fecha especial o festivo (0.0 a 1.0)", example=0.0)
    Month: str = Field(..., description="Mes de la sesión (ej: Feb, Mar, May, Nov)", example="May")
    OperatingSystems: int = Field(..., description="ID del sistema operativo del usuario", example=2)
    Browser: int = Field(..., description="ID del navegador utilizado", example=2)
    Region: int = Field(..., description="ID de la región del usuario", example=1)
    TrafficType: int = Field(..., description="ID del tipo de tráfico de origen", example=1)
    VisitorType: str = Field(..., description="Tipo de visitante: Returning_Visitor, New_Visitor, Other", example="Returning_Visitor")
    Weekend: bool = Field(..., description="Indica si la sesión ocurrió en fin de semana", example=True)
