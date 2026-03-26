import bcrypt
import uuid
from sqlalchemy.orm import Session
from .models import Usuario, Proyecto, Tarea

# Utils de Seguridad
def hash_pw(pwd: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd.encode(), salt).decode()

def verify_pw(pwd: str, h: str) -> bool:
    return bcrypt.checkpw(pwd.encode(), h.encode())

# Servicios de Usuario
def get_user_by_email(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.email == email).first()

def create_user(db: Session, email: str, nombre: str, password_plana: str):
    uid = f"usr_{uuid.uuid4().hex[:10]}"
    user = Usuario(id=uid, email=email, nombre=nombre, password=hash_pw(password_plana))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Servicios de Proyectos
def get_proyectos_by_user(db: Session, user_id: str):
    return db.query(Proyecto).filter(Proyecto.usuario_id == user_id).all()

def create_proyecto(db: Session, user_id: str, nombre: str, descripcion: str = ""):
    pid = f"prj_{uuid.uuid4().hex[:10]}"
    proyecto = Proyecto(id=pid, nombre=nombre, descripcion=descripcion, usuario_id=user_id)
    db.add(proyecto)
    db.commit()
    db.refresh(proyecto)
    return proyecto

# Servicios de Tareas
def get_tareas_by_user(db: Session, user_id: str, proyecto_id: str = None):
    query = db.query(Tarea).filter(Tarea.usuario_id == user_id)
    if proyecto_id:
        query = query.filter(Tarea.proyecto_id == proyecto_id)
    return query.all()

def create_tarea(db: Session, user_id: str, proyecto_id: str, titulo: str, prioridad: str = "media"):
    tid = f"tsk_{uuid.uuid4().hex[:10]}"
    tarea = Tarea(id=tid, titulo=titulo, prioridad=prioridad, proyecto_id=proyecto_id, usuario_id=user_id)
    db.add(tarea)
    db.commit()
    db.refresh(tarea)
    return tarea

def update_tarea(db: Session, tid: str, user_id: str, data: dict):
    tarea = db.query(Tarea).filter(Tarea.id == tid, Tarea.usuario_id == user_id).first()
    if not tarea:
        return None
    for key, value in data.items():
        if hasattr(tarea, key):
            setattr(tarea, key, value)
    db.commit()
    db.refresh(tarea)
    return tarea

def delete_tarea(db: Session, tid: str, user_id: str):
    tarea = db.query(Tarea).filter(Tarea.id == tid, Tarea.usuario_id == user_id).first()
    if tarea:
        db.delete(tarea)
        db.commit()
        return True
    return False
