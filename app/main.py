"""
API de Gestion - Simple y Funcional
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from datetime import datetime, timedelta
from pathlib import Path
import uuid
import hashlib
from jose import jwt as pyjwt

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
engine = create_engine("sqlite:///./gestion.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Modelos
class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    nombre = Column(String, nullable=False)
    password = Column(String, nullable=False)
    activo = Column(Boolean, default=True)
    fecha = Column(DateTime, default=datetime.utcnow)

class Proyecto(Base):
    __tablename__ = "proyectos"
    id = Column(String, primary_key=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text)
    usuario_id = Column(String, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)

class Tarea(Base):
    __tablename__ = "tareas"
    id = Column(String, primary_key=True)
    titulo = Column(String, nullable=False)
    descripcion = Column(Text)
    estado = Column(String, default="pendiente")
    prioridad = Column(String, default="media")
    proyecto_id = Column(String, nullable=False)
    usuario_id = Column(String, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)

# Crear tablas
Base.metadata.create_all(engine)

# Seguridad
SECRET = "mi-clave-secreta-2026"
security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_pw(pwd):
    import bcrypt
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

def verify_pw(pwd, h):
    import bcrypt
    return bcrypt.checkpw(pwd.encode(), h.encode())

def create_token(uid):
    return pyjwt.encode({"sub": uid, "exp": datetime.utcnow() + timedelta(hours=24)}, SECRET, algorithm="HS256")

def get_user(token: str = Depends(security)):
    try:
        payload = pyjwt.decode(token.credentials, SECRET, algorithms=["HS256"])
        return payload["sub"]
    except:
        raise HTTPException(401, "Token invalido")

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
    existente = db.query(Usuario).filter(Usuario.email == data.email).first()
    if existente:
        raise HTTPException(400, "Email ya registrado")
    
    uid = f"usr_{uuid.uuid4().hex[:10]}"
    user = Usuario(id=uid, email=data.email, nombre=data.nombre, password=hash_pw(data.password))
    db.add(user)
    db.commit()
    
    return {"token": create_token(uid), "usuario": {"id": uid, "email": data.email, "nombre": data.nombre}}

@app.post("/api/login")
async def login(data: Login, db=Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.email == data.email).first()
    if not user or not verify_pw(data.password, user.password):
        raise HTTPException(401, "Credenciales incorrectas")
    
    return {"token": create_token(user.id), "usuario": {"id": user.id, "email": user.email, "nombre": user.nombre}}

@app.get("/api/proyectos")
async def listar_proyectos(uid=Depends(get_user), db=Depends(get_db)):
    proyectos = db.query(Proyecto).filter(Proyecto.usuario_id == uid).all()
    return [{"id": p.id, "nombre": p.nombre, "descripcion": p.descripcion or ""} for p in proyectos]

@app.post("/api/proyectos")
async def crear_proyecto(data: ProyectoIn, uid=Depends(get_user), db=Depends(get_db)):
    pid = f"prj_{uuid.uuid4().hex[:10]}"
    proyecto = Proyecto(id=pid, nombre=data.nombre, descripcion=data.descripcion, usuario_id=uid)
    db.add(proyecto)
    db.commit()
    return {"id": pid, "nombre": data.nombre, "descripcion": data.descripcion}

@app.get("/api/tareas")
async def listar_tareas(proyecto_id: str = None, uid=Depends(get_user), db=Depends(get_db)):
    query = db.query(Tarea).filter(Tarea.usuario_id == uid)
    if proyecto_id:
        query = query.filter(Tarea.proyecto_id == proyecto_id)
    tareas = query.all()
    return [{"id": t.id, "titulo": t.titulo, "estado": t.estado, "prioridad": t.prioridad, "proyecto_id": t.proyecto_id} for t in tareas]

@app.post("/api/tareas")
async def crear_tarea(data: TareaIn, uid=Depends(get_user), db=Depends(get_db)):
    proyecto = db.query(Proyecto).filter(Proyecto.id == data.proyecto_id, Proyecto.usuario_id == uid).first()
    if not proyecto:
        raise HTTPException(404, "Proyecto no encontrado")
    
    tid = f"tsk_{uuid.uuid4().hex[:10]}"
    tarea = Tarea(id=tid, titulo=data.titulo, prioridad=data.prioridad, proyecto_id=data.proyecto_id, usuario_id=uid)
    db.add(tarea)
    db.commit()
    return {"id": tid, "titulo": data.titulo, "estado": "pendiente", "prioridad": data.prioridad}

@app.patch("/api/tareas/{tid}")
async def actualizar_tarea(tid: str, data: dict, uid=Depends(get_user), db=Depends(get_db)):
    tarea = db.query(Tarea).filter(Tarea.id == tid, Tarea.usuario_id == uid).first()
    if not tarea:
        raise HTTPException(404, "Tarea no encontrada")
    
    if "estado" in data:
        tarea.estado = data["estado"]
    if "titulo" in data:
        tarea.titulo = data["titulo"]
    
    db.commit()
    return {"id": tarea.id, "titulo": tarea.titulo, "estado": tarea.estado}

@app.delete("/api/tareas/{tid}")
async def eliminar_tarea(tid: str, uid=Depends(get_user), db=Depends(get_db)):
    tarea = db.query(Tarea).filter(Tarea.id == tid, Tarea.usuario_id == uid).first()
    if not tarea:
        raise HTTPException(404, "Tarea no encontrada")
    db.delete(tarea)
    db.commit()
    return {"msg": "Tarea eliminada"}
