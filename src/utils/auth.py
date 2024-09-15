from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from passlib.hash import bcrypt

from src import database
from src.entities.user import User

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 365
ALGORITHM = "HS256"
JWT_SECRET_KEY = "VERY_STRONG_AND_SECURE_JWT_SECRET_KEY"
COOKIE_NAME = "quiz_token"


def get_password_hash(password: str) -> str:
    return bcrypt.hash(password)


def validate_password(password: str, password_hash: str) -> bool:
    return bcrypt.verify(password, password_hash)


def create_access_token(subject: str) -> str:
    expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"exp": expires_delta, "sub": subject}, JWT_SECRET_KEY, ALGORITHM)


async def token_to_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login", scheme_name="JWT"))) -> Optional[User]:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])

        if datetime.fromtimestamp(payload["exp"]) < datetime.now():
            return None
    except jwt.exceptions.DecodeError:
        return None

    return database.get_user(username=payload["sub"])


async def get_user(request: Request) -> Optional[dict]:
    token = request.cookies.get(COOKIE_NAME)
    return await token_to_user(token)
