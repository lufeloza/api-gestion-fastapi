from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

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
