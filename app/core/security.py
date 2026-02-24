from datetime import datetime, timedelta, timezone
import bcrypt
from jose import JWTError, jwt

ALGORITHM = "HS256"
MAX_BCRYPT_PASSWORD_BYTES = 72


def hash_password(password: str) -> str:
    """Devuelve el hash bcrypt de la contrasena."""
    if len(password.encode("utf-8")) > MAX_BCRYPT_PASSWORD_BYTES:
        raise ValueError("Password cannot be longer than 72 bytes for bcrypt.")
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Devuelve True si plain_password coincide con hashed_password."""
    if len(plain_password.encode("utf-8")) > MAX_BCRYPT_PASSWORD_BYTES:
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except ValueError:
        return False


def create_access_token(data: dict, secret_key: str, minutes: int) -> str:
    """Devuelve un JWT firmado que expira en 'minutes' minutos."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)


def decode_token(token: str, secret_key: str) -> dict:
    """
    Devuelve el payload del JWT si es valido.
    Si no, lanza ValueError (token invalido, mal formado o expirado).
    """
    try:
        return jwt.decode(token, secret_key, algorithms=[ALGORITHM])
    except JWTError as e:
        raise ValueError("Token invalido o expirado") from e
