from __future__ import annotations

import uuid
from pathlib import Path
from typing import Literal, Tuple

from app.core.errors import AppValidationError

# Лимит: 5 МБ
MAX_BYTES = 5_000_000

# Поддерживаем только PNG и JPEG
PNG = b"\x89PNG\r\n\x1a\n"
JPEG_SOI = b"\xff\xd8"
JPEG_EOI = b"\xff\xd9"

MimeType = Literal["image/png", "image/jpeg"]


def sniff_image_type(data: bytes) -> MimeType | None:
    if data.startswith(PNG):
        return "image/png"
    if data.startswith(JPEG_SOI) and data.endswith(JPEG_EOI):
        return "image/jpeg"
    return None


def secure_save(base_dir: str | Path, data: bytes) -> Tuple[Path, MimeType]:
    if len(data) > MAX_BYTES:
        raise AppValidationError("file too big", status=413)

    mt = sniff_image_type(data)
    if mt is None:
        raise AppValidationError("unsupported file type")

    # Канонизируем и требуем, чтобы корневая папка существовала
    root = Path(base_dir).resolve(strict=True)

    # Запрет симлинков в родителях
    if any(p.is_symlink() for p in root.parents):
        raise AppValidationError("symlink parent not allowed")

    # Имя файла — UUID + расширение по типу
    ext = ".png" if mt == "image/png" else ".jpg"
    name = f"{uuid.uuid4()}{ext}"
    path = (root / name).resolve()

    # Гарантируем, что путь остаётся внутри корня
    if not str(path).startswith(str(root)):
        raise AppValidationError("path traversal detected")

    # Сохраняем
    with open(path, "wb") as f:
        f.write(data)
    return path, mt
