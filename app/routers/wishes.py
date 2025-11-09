from __future__ import annotations

from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, Query, Request

from app.core.auth import get_current_user
from app.core.db import _DB
from app.core.errors import AppValidationError, NotFoundError
from app.core.jsonsec import JsonTooLargeError, safe_json_loads
from app.models.wish import Wish

MAX_IMPORT = 5000

router = APIRouter(prefix="/wishes", tags=["wishes"])


@router.get("", response_model=list[Wish])
def list_wishes(user: str = Depends(get_current_user)):
    return [w for w in _DB["wishes"] if w["owner"] == user]


@router.get("/price/less", response_model=list[Wish])
def wishes_price_less(price: Decimal, user: str = Depends(get_current_user)):
    return [
        w
        for w in _DB["wishes"]
        if w["owner"] == user
        and w.get("price_estimate") is not None
        and w["price_estimate"] < price
    ]


@router.get("/price/greater", response_model=list[Wish])
def wishes_price_greater(price: Decimal, user: str = Depends(get_current_user)):
    return [
        w
        for w in _DB["wishes"]
        if w["owner"] == user
        and w.get("price_estimate") is not None
        and w["price_estimate"] > price
    ]


@router.get("/category/{name}", response_model=list[Wish])
def get_wishes_by_category(name: str, user: str = Depends(get_current_user)):
    return [
        w for w in _DB["wishes"] if w["owner"] == user and w.get("category") == name
    ]


@router.get("/sorted", response_model=list[Wish])
def get_sorted_wishes(
    order_by: str = Query("price_estimate"),
    ascending: bool = True,
    user: str = Depends(get_current_user),
):
    raw = (order_by or "").strip().lower()
    aliases = {
        "price": "price_estimate",
        "price_estimate": "price_estimate",
        "title": "title",
    }
    key = aliases.get(raw)
    if key is None:
        raise AppValidationError("invalid sort key")

    items = [w for w in _DB["wishes"] if w["owner"] == user]
    return sorted(
        items,
        key=lambda w: (
            w[key]
            if (key in w and w[key] is not None)
            else (Decimal("0") if key == "price_estimate" else "")
        ),
        reverse=not ascending,
    )


@router.get("/export")
def export_wishes(user: str = Depends(get_current_user)):
    data = [w for w in _DB["wishes"] if w["owner"] == user]
    return {"backup": data, "count": len(data)}


@router.post("/import")
async def import_wishes(request: Request, user: str = Depends(get_current_user)):
    raw = await request.body()
    try:
        payload = safe_json_loads(raw)
    except JsonTooLargeError:
        raise AppValidationError("import body too large", status=413)
    except ValueError:
        raise AppValidationError("invalid import format")

    imported = payload.get("backup", [])
    if not isinstance(imported, list):
        raise AppValidationError("invalid import format")
    if len(imported) > MAX_IMPORT:
        raise AppValidationError(f"import too large (>{MAX_IMPORT})", status=413)

    validated: list[dict[str, Any]] = []
    for raw_item in imported:
        if not isinstance(raw_item, dict):
            raise AppValidationError("invalid record schema")
        obj = dict(raw_item)
        obj["owner"] = user
        try:
            w = Wish.model_validate(obj)
        except Exception:
            raise AppValidationError("invalid record schema")
        validated.append(w.model_dump())

    _DB["wishes"].extend(validated)
    return {"status": "restored", "count": len(validated)}


@router.post("", response_model=Wish)
def create_wish(wish: Wish, user: str = Depends(get_current_user)):
    if any(w["id"] == wish.id and w["owner"] == user for w in _DB["wishes"]):
        raise AppValidationError("id already exists for this user")
    wish_data = wish.model_dump()
    wish_data["owner"] = user
    _DB["wishes"].append(wish_data)
    return wish_data


@router.get("/{wish_id}", response_model=Wish)
def get_wish(wish_id: int, user: str = Depends(get_current_user)):
    for w in _DB["wishes"]:
        if w["id"] == wish_id and w["owner"] == user:
            return w
    raise NotFoundError("wish not found or not owned by user")


@router.put("/{wish_id}", response_model=Wish)
def update_wish(wish_id: int, wish: Wish, user: str = Depends(get_current_user)):
    for idx, w in enumerate(_DB["wishes"]):
        if w["id"] == wish_id and w["owner"] == user:
            new_wish = wish.model_dump()
            new_wish["owner"] = user
            _DB["wishes"][idx] = new_wish
            return new_wish
    raise NotFoundError("wish not found or not owned by user")


@router.delete("/{wish_id}")
def delete_wish(wish_id: int, user: str = Depends(get_current_user)):
    for idx, w in enumerate(_DB["wishes"]):
        if w["id"] == wish_id and w["owner"] == user:
            del _DB["wishes"][idx]
            return {"status": "deleted"}
    raise NotFoundError("wish not found or not owned by user")
