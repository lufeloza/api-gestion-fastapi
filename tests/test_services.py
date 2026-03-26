import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app import services
import os

# Base de datos de prueba en memoria
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_create_user(db):
    email = "test@example.com"
    nombre = "Test User"
    password = "password123"
    
    user = services.create_user(db, email, nombre, password)
    
    assert user.email == email
    assert user.nombre == nombre
    assert services.verify_pw(password, user.password)

def test_get_user_by_email(db):
    email = "findme@example.com"
    services.create_user(db, email, "Find Me", "pass")
    
    user = services.get_user_by_email(db, email)
    assert user is not None
    assert user.email == email

def test_create_proyecto(db):
    user = services.create_user(db, "owner@test.com", "Owner", "pass")
    proyecto = services.create_proyecto(db, user.id, "Mi Proyecto", "Descripcion")
    
    assert proyecto.nombre == "Mi Proyecto"
    assert proyecto.usuario_id == user.id

def test_create_tarea(db):
    user = services.create_user(db, "owner@test.com", "Owner", "pass")
    proyecto = services.create_proyecto(db, user.id, "Proyecto 1", "Desc")
    tarea = services.create_tarea(db, user.id, proyecto.id, "Tarea 1", "alta")
    
    assert tarea.titulo == "Tarea 1"
    assert tarea.proyecto_id == proyecto.id
    assert tarea.estado == "pendiente"

def test_update_tarea(db):
    user = services.create_user(db, "owner@test.com", "Owner", "pass")
    proyecto = services.create_proyecto(db, user.id, "P1", "D")
    tarea = services.create_tarea(db, user.id, proyecto.id, "T1", "media")
    
    updated = services.update_tarea(db, tarea.id, user.id, {"estado": "completado", "titulo": "Cambiado"})
    assert updated.estado == "completado"
    assert updated.titulo == "Cambiado"
