from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=list[schemas.ItemRead])
def list_items(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[schemas.ItemRead]:
    return crud.item_repository.list(db, skip=skip, limit=limit)


@router.get("/{item_id}", response_model=schemas.ItemRead)
def get_item(item_id: int, db: Session = Depends(get_db)) -> schemas.ItemRead:
    return crud.item_repository.get(db, item_id)


@router.post("", response_model=schemas.ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: schemas.ItemCreate, db: Session = Depends(get_db)) -> schemas.ItemRead:
    return crud.item_repository.create(db, payload)


@router.put("/{item_id}", response_model=schemas.ItemRead)
def update_item(
    item_id: int,
    payload: schemas.ItemUpdate,
    db: Session = Depends(get_db),
) -> schemas.ItemRead:
    return crud.item_repository.update(db, item_id, payload)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)) -> Response:
    crud.item_repository.delete(db, item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
