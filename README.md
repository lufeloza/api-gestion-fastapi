# API de Gestión de Tareas y Proyectos

API REST para gestión de tareas y proyectos con autenticación JWT.

## 🎯 Para qué sirve

- Gestionar proyectos y tareas
- Registro e inicio de sesión de usuarios
- API REST lista para conectar con frontend o móvil

## ✨ Características

- **Autenticación JWT** segura
- **SQLAlchemy ORM** (compatible SQLite/PostgreSQL)
- **FastAPI** moderno y rápido
- **Documentación automática** (Swagger)
- **Tests incluidos**

## 🛠️ Stack

- FastAPI
- SQLAlchemy
- JWT (python-jose)
- bcrypt

## 🚀 Cómo ejecutarlo

```bash
cd api-gestion-fastapi
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API en: `http://localhost:8000`
Swagger: `http://localhost:8000/docs`

### Con Docker
```bash
docker-compose up -d
```

## 📡 Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/registro` | Registrar usuario |
| POST | `/api/login` | Iniciar sesión |
| GET | `/api/proyectos` | Listar proyectos |
| POST | `/api/proyectos` | Crear proyecto |
| GET | `/api/tareas` | Listar tareas |
| POST | `/api/tareas` | Crear tarea |
| DELETE | `/api/tareas/{id}` | Eliminar tarea |

## 📁 Estructura
```
api-gestion-fastapi/
├── app/main.py      # API completa
├── tests/           # Tests
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

**Lista para producción.** Desplegable en Railway, Render, etc.