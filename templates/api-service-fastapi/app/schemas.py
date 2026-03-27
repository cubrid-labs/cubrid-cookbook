from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    val: Optional[str] = Field(default=None, max_length=255)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    val: Optional[str] = Field(default=None, max_length=255)


class CategoryRead(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ItemBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    val: Optional[str] = Field(default=None, max_length=255)
    cnt: int = Field(default=0, ge=0)
    file_data: Optional[str] = None
    category_id: int = Field(gt=0)


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    val: Optional[str] = Field(default=None, max_length=255)
    cnt: Optional[int] = Field(default=None, ge=0)
    file_data: Optional[str] = None
    category_id: Optional[int] = Field(default=None, gt=0)


class ItemRead(ItemBase):
    id: int
    category: CategoryRead

    model_config = ConfigDict(from_attributes=True)
