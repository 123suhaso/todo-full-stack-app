from fastapi import APIRouter, HTTPException, Depends
import psycopg2.extras
from db import get_db_connection
from pydantic import BaseModel,EmailStr
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta

router = APIRouter()
    

# =====================
# Password Hashing
# =====================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# =====================
# JWT Config
# =====================
SECRET_KEY = "9e9e678059bcb6443637877f438d90c5f3d6167a32e40e1833c37d5ef067f4c4"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# OAuth2 scheme (matches login route)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# =====================
# User Models
# =====================
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    username: str
    password: str
    role: str = "user"
    is_active: bool = True

# =====================
# Get Current User
# =====================
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("id")
        username: str = payload.get("sub")
        role: str = payload.get("role")

        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        return {"id": user_id, "username": username, "role": role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# =====================
# Routes
# =====================
@router.post("/users")
def create_user(user: UserCreate):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        hashed_password = get_password_hash(user.password)

        cursor.execute(
            """
            INSERT INTO users (name, email, username, hashed_password, role, is_active)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, name, email, username, role, is_active
            """,
            (user.name, user.email, user.username, hashed_password, user.role, user.is_active),
        )
        new_user = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "User created successfully", "user": new_user}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("SELECT * FROM users WHERE username=%s", (form_data.username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Create JWT token including user id
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"], "id": user["id"]}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"id": user["id"], "username": user["username"], "role": user["role"]}
    }


@router.get("/me")
def read_users_me(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}
