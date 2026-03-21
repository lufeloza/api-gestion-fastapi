"""
Tests para la API de Gestion
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Patch bcrypt before importing app
import bcrypt
_original_hashpw = bcrypt.hashpw
bcrypt.hashpw = lambda p, s: _original_hashpw(p[:72], s)
bcrypt.checkpw = lambda p, h: _original_hashpw(p[:72], h)

from app.main import app, get_db, Usuario, Proyecto, Tarea

# Base de datos de test
engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def client():
    from app.main import Base
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def usuario(client):
    r = client.post("/api/registro", json={"email": "test@test.com", "nombre": "Test", "password": "123456"})
    return r.json()["token"]

class TestAuth:
    def test_registro(self, client):
        r = client.post("/api/registro", json={"email": "test@test.com", "nombre": "Test", "password": "123456"})
        assert r.status_code == 200
        assert "token" in r.json()

    def test_registro_duplicado(self, client):
        client.post("/api/registro", json={"email": "test@test.com", "nombre": "Test", "password": "123456"})
        r = client.post("/api/registro", json={"email": "test@test.com", "nombre": "Test", "password": "123456"})
        assert r.status_code == 400

    def test_login(self, client):
        client.post("/api/registro", json={"email": "test@test.com", "nombre": "Test", "password": "123456"})
        r = client.post("/api/login", json={"email": "test@test.com", "password": "123456"})
        assert r.status_code == 200
        assert "token" in r.json()

    def test_login_incorrecto(self, client):
        r = client.post("/api/login", json={"email": "noexiste@test.com", "password": "123456"})
        assert r.status_code == 401

class TestProyectos:
    def test_crear_proyecto(self, client, usuario):
        r = client.post("/api/proyectos", json={"nombre": "Proyecto 1", "descripcion": "Test"}, headers={"Authorization": f"Bearer {usuario}"})
        assert r.status_code == 200
        assert r.json()["nombre"] == "Proyecto 1"

    def test_listar_proyectos(self, client, usuario):
        client.post("/api/proyectos", json={"nombre": "P1"}, headers={"Authorization": f"Bearer {usuario}"})
        r = client.get("/api/proyectos", headers={"Authorization": f"Bearer {usuario}"})
        assert r.status_code == 200
        assert len(r.json()) == 1

    def test_proyecto_sin_auth(self, client):
        r = client.get("/api/proyectos")
        assert r.status_code == 403

class TestTareas:
    def test_crear_tarea(self, client, usuario):
        p = client.post("/api/proyectos", json={"nombre": "P1"}, headers={"Authorization": f"Bearer {usuario}"})
        pid = p.json()["id"]
        r = client.post("/api/tareas", json={"titulo": "Tarea 1", "prioridad": "alta", "proyecto_id": pid}, headers={"Authorization": f"Bearer {usuario}"})
        assert r.status_code == 200
        assert r.json()["titulo"] == "Tarea 1"

    def test_listar_tareas(self, client, usuario):
        p = client.post("/api/proyectos", json={"nombre": "P1"}, headers={"Authorization": f"Bearer {usuario}"})
        pid = p.json()["id"]
        client.post("/api/tareas", json={"titulo": "T1", "proyecto_id": pid}, headers={"Authorization": f"Bearer {usuario}"})
        r = client.get("/api/tareas", headers={"Authorization": f"Bearer {usuario}"})
        assert len(r.json()) == 1

    def test_actualizar_tarea(self, client, usuario):
        p = client.post("/api/proyectos", json={"nombre": "P1"}, headers={"Authorization": f"Bearer {usuario}"})
        pid = p.json()["id"]
        t = client.post("/api/tareas", json={"titulo": "T1", "proyecto_id": pid}, headers={"Authorization": f"Bearer {usuario}"})
        tid = t.json()["id"]
        r = client.patch(f"/api/tareas/{tid}", json={"estado": "completada"}, headers={"Authorization": f"Bearer {usuario}"})
        assert r.json()["estado"] == "completada"

    def test_eliminar_tarea(self, client, usuario):
        p = client.post("/api/proyectos", json={"nombre": "P1"}, headers={"Authorization": f"Bearer {usuario}"})
        pid = p.json()["id"]
        t = client.post("/api/tareas", json={"titulo": "T1", "proyecto_id": pid}, headers={"Authorization": f"Bearer {usuario}"})
        tid = t.json()["id"]
        r = client.delete(f"/api/tareas/{tid}", headers={"Authorization": f"Bearer {usuario}"})
        assert r.status_code == 200
