from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel
from jose import JWTError, jwt
import subprocess
import sys
import os

import models
from database import engine, SessionLocal

# Konfiguracja JWT
SECRET_KEY = "tajnykluczdogrygameboy"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

GAMES = {1: "snake", 2: "tetris", 3: "labirynt", 4: "kolko"}
LOWER_IS_BETTER = set()   
SUM_GAMES = {4}           

# Inicjalizacja bazy danych
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gameboy Backend", version="1.0.0")

# --- KONFIGURACJA CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- SCHEMATY PYDANTIC ---
class UserCreate(BaseModel):
    username: str
    password: str

class AdminUserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"

class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ScoreCreate(BaseModel):
    game_id: int
    score: int

class ScoreUpdate(BaseModel):
    game_id: Optional[int] = None
    score: Optional[int] = None

class ScoreResponse(BaseModel):
    id: int
    game_id: int
    score: int
    user_id: int

    class Config:
        from_attributes = True

# --- FUNKCJE POMOCNICZE ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Weryfikacja uprawnień administratora na podstawie tokenu JWT
def get_current_admin_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Brak tokenu autoryzacji")

    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role != "admin":
            raise HTTPException(status_code=403, detail="Brak uprawnień administratora")
    except JWTError:
        raise HTTPException(status_code=403, detail="Niepoprawny token")

    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Użytkownik nie znaleziony")
    return user

# Weryfikacja zalogowanego użytkownika na podstawie tokenu JWT
def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Brak tokenu autoryzacji")

    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Niepoprawny lub wygasły token")

    if username is None:
        raise HTTPException(status_code=401, detail="Niepoprawny token")

    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Użytkownik nie znaleziony")
    return user

# --- ENDPOINTY: AUTORYZACJA ---
@app.get("/")
def read_root():
    return {"message": "Serwer projektu Gameboy działa!"}

@app.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Taki użytkownik już istnieje.")

    hashed_password = pwd_context.hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_password, role="user")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/api/auth/login", response_model=Token)
def login_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Niepoprawna nazwa użytkownika lub hasło",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username, "role": db_user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- ENDPOINT URUCHAMIANIA GAMEBOYA PYGAME ---
@app.post("/api/launch-gameboy")
def launch_gameboy(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Brak tokenu autoryzacji")

    token = authorization.split(" ")[1]
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=403, detail="Niepoprawny token")

    try:
        
        menu_path = os.path.join("Gameboy", "Gameboy", "main_menu.py")
        if not os.path.exists(menu_path):
            menu_path = "main_menu.py"  

        folder = os.path.dirname(menu_path)
        subprocess.Popen([sys.executable, os.path.basename(menu_path)], cwd=folder if folder else None)

        return {"message": "Wirtualny Gameboy został uruchomiony pomyślnie!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd uruchamiania gry: {str(e)}")

# --- PUBLICZNA LISTA UŻYTKOWNIKÓW do tabeli wyników ---
@app.get("/api/users", response_model=List[UserResponse])
def get_public_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

# --- ENDPOINTY: WYNIKI (SCORES) ---
@app.post("/api/scores", response_model=ScoreResponse, status_code=status.HTTP_201_CREATED)
def create_score(
    score_data: ScoreCreate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if score_data.game_id not in GAMES:
        raise HTTPException(status_code=400, detail="Nieznana gra")

    existing = db.query(models.Score).filter(
        models.Score.user_id == user.id,
        models.Score.game_id == score_data.game_id
    ).first()

    
    if existing is None:
        new_score = models.Score(
            game_id=score_data.game_id,
            score=score_data.score,
            user_id=user.id
        )
        db.add(new_score)
        db.commit()
        db.refresh(new_score)
        return new_score

    
    if score_data.game_id in SUM_GAMES:
        existing.score += score_data.score
    elif score_data.game_id in LOWER_IS_BETTER:
        if score_data.score < existing.score:
            existing.score = score_data.score
    else:
        if score_data.score > existing.score:
            existing.score = score_data.score

    db.commit()
    db.refresh(existing)
    return existing

@app.get("/api/scores", response_model=List[ScoreResponse])
def get_scores(game_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(models.Score)
    if game_id is not None:
        query = query.filter(models.Score.game_id == game_id)
    scores = query.order_by(models.Score.score.desc()).all()
    return scores

# --- RANKING DLA TABELI WYNIKÓW GRACZA ---
@app.get("/api/leaderboard/{game_id}")
def leaderboard(game_id: int, db: Session = Depends(get_db)):
    if game_id not in GAMES:
        raise HTTPException(status_code=404, detail="Nieznana gra")

    q = (
        db.query(models.Score, models.User.username)
        .join(models.User, models.User.id == models.Score.user_id)
        .filter(models.Score.game_id == game_id)
    )
    if game_id in LOWER_IS_BETTER:
        q = q.order_by(models.Score.score.asc())
    else:
        q = q.order_by(models.Score.score.desc())

    return [{"username": u, "score": s.score} for s, u in q.limit(50).all()]

# --- ENDPOINTY ADMINISTRACYJNE TYLKO DLA ADMINA ---

@app.get("/api/admin/users", response_model=List[UserResponse])
def admin_get_users(admin: models.User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    return db.query(models.User).all()

@app.post("/api/admin/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def admin_create_user(user_data: AdminUserCreate, admin: models.User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Taki użytkownik już istnieje.")

    hashed_password = pwd_context.hash(user_data.password)
    new_user = models.User(username=user_data.username, hashed_password=hashed_password, role=user_data.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.delete("/api/admin/users/{user_id}", status_code=status.HTTP_200_OK)
def admin_delete_user(user_id: int, admin: models.User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Użytkownik nie istnieje")
    db.delete(user)
    db.commit()
    return {"message": f"Użytkownik o ID {user_id} został usunięty"}

@app.get("/api/admin/scores", response_model=List[ScoreResponse])
def admin_get_scores(admin: models.User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    return db.query(models.Score).all()

@app.put("/api/admin/scores/{score_id}", response_model=ScoreResponse)
def admin_update_score(
    score_id: int,
    score_data: ScoreUpdate,
    admin: models.User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    score_obj = db.query(models.Score).filter(models.Score.id == score_id).first()
    if not score_obj:
        raise HTTPException(status_code=404, detail="Wynik nie istnieje")

    if score_data.score is not None:
        score_obj.score = score_data.score
    if score_data.game_id is not None:
        score_obj.game_id = score_data.game_id

    db.commit()
    db.refresh(score_obj)
    return score_obj

@app.delete("/api/admin/scores/{score_id}", status_code=status.HTTP_200_OK)
def admin_delete_score(score_id: int, admin: models.User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    score_obj = db.query(models.Score).filter(models.Score.id == score_id).first()
    if not score_obj:
        raise HTTPException(status_code=404, detail="Wynik nie istnieje")
    db.delete(score_obj)
    db.commit()
    return {"message": f"Wynik o ID {score_id} został usunięty"}