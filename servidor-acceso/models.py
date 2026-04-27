"""
Modelos de base de datos para el servidor de acceso
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Usuario(db.Model):
    """
    Modelo para almacenar información de usuarios registrados.
    
    Atributos:
        id: Identificador único del usuario
        nombre: Nombre del usuario
        token: Token único alfanumérico para autenticación
        email: Email del usuario
        autorizado: Estado de autorización
        fecha_registro: Fecha de registro
        fecha_ultimo_acceso: Última vez que accedió
    """
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    token = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True)
    autorizado = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_ultimo_acceso = db.Column(db.DateTime)
    
    # Relación con eventos de acceso
    eventos = db.relationship('EventoAcceso', backref='usuario', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Usuario {self.nombre} ({self.token})>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario JSON."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'token': self.token,
            'email': self.email,
            'autorizado': self.autorizado,
            'fecha_registro': self.fecha_registro.isoformat(),
            'fecha_ultimo_acceso': self.fecha_ultimo_acceso.isoformat() if self.fecha_ultimo_acceso else None
        }


class EventoAcceso(db.Model):
    """
    Modelo para registrar eventos de acceso (intentos de autenticación).
    
    Atributos:
        id: Identificador único del evento
        usuario_id: ID del usuario que generó el evento
        token: Token utilizado en el intento
        timestamp: Marca de tiempo del evento
        resultado: Resultado del intento (autorizado/denegado)
        descripcion: Descripción adicional del evento
        ip_origen: IP desde donde se originó la solicitud (opcional)
    """
    __tablename__ = 'eventos_acceso'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    token = db.Column(db.String(50), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    resultado = db.Column(db.String(20), nullable=False)  # 'autorizado', 'denegado', 'error'
    descripcion = db.Column(db.String(255))
    ip_origen = db.Column(db.String(45))
    
    def __repr__(self):
        return f'<EventoAcceso {self.resultado} - {self.timestamp}>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario JSON."""
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'token': self.token,
            'timestamp': self.timestamp.isoformat(),
            'resultado': self.resultado,
            'descripcion': self.descripcion,
            'ip_origen': self.ip_origen
        }
