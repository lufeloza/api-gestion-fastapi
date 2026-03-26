"""
API de Gestion - Simple y Funcional
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .models import Base, Usuario, Proyecto, Tarea
from . import services
import uuid
from jose import jwt as pyjwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Configuracion
app = FastAPI(title="API de Gestion", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base de datos
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# (Modelos movidos a models.py)

# Crear tablas
Base.metadata.create_all(engine)

# Seguridad
SECRET = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# (Lógica de hashing movida a services.py)

def create_token(uid):
    return pyjwt.encode({"sub": uid, "exp": datetime.utcnow() + timedelta(hours=24)}, SECRET, algorithm="HS256")

def get_user(token: str = Depends(security)):
    try:
        payload = pyjwt.decode(token.credentials, SECRET, algorithms=[ALGORITHM])
        return payload["sub"]
    except Exception as e:
        raise HTTPException(401, f"Token invalido: {str(e)}")

# Pydantic
class Login(BaseModel):
    email: str
    password: str

class Register(BaseModel):
    email: str
    nombre: str
    password: str

class ProyectoIn(BaseModel):
    nombre: str
    descripcion: str = ""

class TareaIn(BaseModel):
    titulo: str
    prioridad: str = "media"
    proyecto_id: str

# Rutas
@app.get("/")
async def root():
    return FileResponse(str(Path(__file__).parent.parent / "index.html"))

@app.get("/api/salud")
async def salud():
    return {"msg": "API funcionando", "version": "1.0"}

@app.post("/api/registro")
async def registro(data: Register, db=Depends(get_db)):
    existente = services.get_user_by_email(db, data.email)
    if existente:
        raise HTTPException(400, "Email ya registrado")
    
    user = services.create_user(db, data.email, data.nombre, data.password)
    return {
        "token": create_token(user.id), 
        "usuario": {"id": user.id, "email": user.email, "nombre": user.nombre}
    }

@app.post("/api/login")
async def login(data: Login, db=Depends(get_db)):
    user = services.get_user_by_email(db, data.email)
    if not user or not services.verify_pw(data.password, user.password):
        raise HTTPException(401, "Credenciales incorrectas")
    
    return {
        "token": create_token(user.id), 
        "usuario": {"id": user.id, "email": user.email, "nombre": user.nombre}
    }

@app.get("/api/proyectos")
async def listar_proyectos(uid=Depends(get_user), db=Depends(get_db)):
    proyectos = services.get_proyectos_by_user(db, uid)
    return [{"id": p.id, "nombre": p.nombre, "descripcion": p.descripcion or ""} for p in proyectos]

@app.post("/api/proyectos")
async def crear_proyecto(data: ProyectoIn, uid=Depends(get_user), db=Depends(get_db)):
    proyecto = services.create_proyecto(db, uid, data.nombre, data.descripcion)
    return {"id": proyecto.id, "nombre": proyecto.nombre, "descripcion": proyecto.descripcion}

@app.get("/api/tareas")
async def listar_tareas(proyecto_id: str = None, uid=Depends(get_user), db=Depends(get_db)):
    tareas = services.get_tareas_by_user(db, uid, proyecto_id)
    return [{"id": t.id, "titulo": t.titulo, "estado": t.estado, "prioridad": t.prioridad, "proyecto_id": t.proyecto_id} for t in tareas]

@app.post("/api/tareas")
async def crear_tarea(data: TareaIn, uid=Depends(get_user), db=Depends(get_db)):
    tarea = services.create_tarea(db, uid, data.proyecto_id, data.titulo, data.prioridad)
    return {"id": tarea.id, "titulo": tarea.titulo, "estado": "pendiente", "prioridad": tarea.prioridad}

@app.patch("/api/tareas/{tid}")
async def actualizar_tarea(tid: str, data: dict, uid=Depends(get_user), db=Depends(get_db)):
    tarea = services.update_tarea(db, tid, uid, data)
    if not tarea:
        raise HTTPException(404, "Tarea no encontrada")
    return {"id": tarea.id, "titulo": tarea.titulo, "estado": tarea.estado}

@app.delete("/api/tareas/{tid}")
async def eliminar_tarea(tid: str, uid=Depends(get_user), db=Depends(get_db)):
    if services.delete_tarea(db, tid, uid):
        return {"msg": "Tarea eliminada"}
    raise HTTPException(404, "Tarea no encontrada")
