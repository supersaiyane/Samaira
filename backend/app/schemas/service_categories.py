from pydantic import BaseModel

class ServiceCategoryBase(BaseModel):
    category_name: str

class ServiceCategoryCreate(ServiceCategoryBase):
    pass

class ServiceCategoryResponse(ServiceCategoryBase):
    category_id: int

    class Config:
        orm_mode = True
