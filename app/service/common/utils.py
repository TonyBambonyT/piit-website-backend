import os
import shutil
from datetime import datetime, timedelta
import httpx
from fastapi import UploadFile
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from app.config.config import settings


def generate_url(url_template: str, year: int, session_num: int) -> str:
    return url_template.format(year=year, session_num=session_num)


def fetch_data_until_found(url_template: str, extract_fn, save_fn):
    """
    Универсальная функция для попыток получить данные с подстановкой года и сессии.
    `extract_fn` — функция, извлекающая данные из ответа.
    `save_fn` — функция, сохраняющая извлеченные данные.
    """
    current_year = datetime.now().year

    while True:
        for session_num in (2, 1):
            if try_fetch_and_save(url_template, current_year, session_num, extract_fn, save_fn):
                # Если нашли, пробуем и другую сессию того же года
                if session_num == 2:
                    try_fetch_and_save(url_template, current_year, 1, extract_fn, save_fn)
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
