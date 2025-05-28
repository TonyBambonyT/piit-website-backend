import os
import shutil
from datetime import datetime, timedelta
from typing import Callable
import httpx
from fastapi import UploadFile
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from app.config.config import settings


def generate_url(url_template: str, year: int, session_num: int) -> str:
    return url_template.format(year=year, session_num=session_num)


def collect_data_until_found(url_template: str, extract_fn: Callable[[dict], list[dict]]) -> list[dict]:
    current_year = datetime.now().year

    while True:
        # Пробуем текущий год, сессия 2
        data_2 = _try_fetch(url_template, current_year, 2, extract_fn)
        if data_2:
            # если есть данные — пробуем 1-ю сессию этого же года
            data_1 = _try_fetch(url_template, current_year, 1, extract_fn)
            return data_2 + (data_1 or [])

        # Пробуем текущий год, сессия 1
        data_1 = _try_fetch(url_template, current_year, 1, extract_fn)
        if data_1:
            # если есть 1 — пробуем предыдущий год, сессия 2
            data_prev_2 = _try_fetch(url_template, current_year - 1, 2, extract_fn)
            return data_1 + (data_prev_2 or [])
        current_year -= 1


def _try_fetch(url_template: str, year: int, session_num: int, extract_fn: Callable[[dict], list[dict]]) -> list[dict]:
    url = url_template.format(year=year, session_num=session_num)
    response = httpx.get(url)
    if response.status_code != 200:
        return []
    return extract_fn(response.json()) or []


def fetch_data_until_found(url_template: str, extract_fn, save_fn):
    """
    Универсальная функция для попыток получить данные с подстановкой года и сессии.
    `extract_fn` — функция, извлекающая данные из ответа.
    `save_fn` — функция, сохраняющая извлеченные данные.
    """
    current_year = datetime.now().year

    while True:
        found_2 = try_fetch_and_save(url_template, current_year, 2, extract_fn, save_fn)
        if found_2:
            try_fetch_and_save(url_template, current_year, 1, extract_fn, save_fn)
            return
        found_1 = try_fetch_and_save(url_template, current_year, 1, extract_fn, save_fn)
        if found_1:
            try_fetch_and_save(url_template, current_year - 1, 2, extract_fn, save_fn)
            return
        current_year -= 1


def try_fetch_and_save(url_template, year, session_num, extract_fn, save_fn) -> bool:
    url = generate_url(url_template, year, session_num)
    try:
        response = httpx.get(url)
        data = response.json()
        extracted = extract_fn(data)
        if extracted:
            save_fn(extracted)
            return True
        return False
    except httpx.RequestError as e:
        raise Exception(f"Error fetching data: {e}")


def save_icon_file(icon: UploadFile, prefix: str) -> str:
    """
    Проверяет тип файла и сохраняет иконку.
    Возвращает путь вида "/static/icons/filename.png"
    """
    if not icon.content_type.startswith("image/"):
        raise ValueError("Invalid file type. Expected an image.")
    filename = f"{prefix.replace(' ', '_')}_{icon.filename}"
    icon_path = os.path.join(settings.UPLOAD_DIR, filename)
    with open(icon_path, "wb") as buffer:
        shutil.copyfileobj(icon.file, buffer)
    return f"/static/icons/{filename}"


def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=12)) -> str:
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + expires_delta})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def admin_required(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        if "sub" not in payload:
            raise ValueError
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
