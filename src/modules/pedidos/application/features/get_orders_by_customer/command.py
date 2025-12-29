from pydantic import BaseModel

class GetOrdersByCustomerCommand(BaseModel):
    """Comando para obtener las órdenes de un cliente."""
    customer_id: str
    skip: int = 0
    limit: int = 100
