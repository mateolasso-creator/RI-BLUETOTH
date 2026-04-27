"""
Servidor HTTP para control de acceso por Bluetooth
Práctica C-3: Implementación de servidor de acceso con autenticación por token

API REST:
- GET /check?token={TOKEN} - Verifica autorización
- POST /log - Registra evento de acceso
- GET /usuarios - Lista usuarios registrados
- POST /usuarios - Registra nuevo usuario
"""

from flask import Flask, request, jsonify
from datetime import datetime
from models import db, Usuario, EventoAcceso
import config
import uuid
import string
import random


app = Flask(__name__)
app.config.from_object(config)

# Inicializar extensiones
db.init_app(app)


# ============================================================================
# CONTEXTO DE APLICACIÓN Y INICIALIZACIÓN
# ============================================================================

@app.before_request
def before_request():
    """Hook que se ejecuta antes de cada solicitud."""
    # Log de solicitud
    print(f"\n[{datetime.utcnow().isoformat()}] {request.method} {request.path}")
    if request.method in ['POST', 'PUT']:
        print(f"  Body: {request.get_json()}")


@app.after_request
def after_request(response):
    """Hook que se ejecuta después de cada solicitud."""
    # CORS headers (opcional, para desarrollo)
    response.headers['Content-Type'] = 'application/json'
    return response


# ============================================================================
# ENDPOINT 1: GET /check - Verificar autorización
# ============================================================================

@app.route('/check', methods=['GET'])
def check_authorization():
    """
    Verifica si un token está autorizado.
    
    Parámetros:
        token (query string): Token del usuario a verificar
    
    Respuesta:
        {
            "autorizado": true/false,
            "nombre": "nombre_usuario",
            "timestamp": "ISO-8601",
            "mensaje": "descripción"
        }
    """
    token = request.args.get('token')
    
    if not token:
        return jsonify({
            "autorizado": False,
            "nombre": None,
            "timestamp": datetime.utcnow().isoformat(),
            "mensaje": "Token no proporcionado"
        }), 400
    
    try:
        # Buscar usuario por token
        usuario = Usuario.query.filter_by(token=token).first()
        
        if usuario is None:
            # Token no encontrado
            evento = EventoAcceso(
                token=token,
                timestamp=datetime.utcnow(),
                resultado='denegado',
                descripcion='Token no registrado',
                ip_origen=request.remote_addr
            )
            db.session.add(evento)
            db.session.commit()
            
            return jsonify({
                "autorizado": False,
                "nombre": None,
                "timestamp": datetime.utcnow().isoformat(),
                "mensaje": "Token no registrado"
            }), 401
        
        if not usuario.autorizado:
            # Usuario existe pero no está autorizado
            evento = EventoAcceso(
                usuario_id=usuario.id,
                token=token,
                timestamp=datetime.utcnow(),
                resultado='denegado',
                descripcion='Usuario no autorizado',
                ip_origen=request.remote_addr
            )
            db.session.add(evento)
            db.session.commit()
            
            return jsonify({
                "autorizado": False,
                "nombre": usuario.nombre,
                "timestamp": datetime.utcnow().isoformat(),
                "mensaje": "Usuario no autorizado"
            }), 403
        
        # Usuario autorizado - actualizar último acceso
        usuario.fecha_ultimo_acceso = datetime.utcnow()
        
        evento = EventoAcceso(
            usuario_id=usuario.id,
            token=token,
            timestamp=datetime.utcnow(),
            resultado='autorizado',
            descripcion='Acceso autorizado',
            ip_origen=request.remote_addr
        )
        db.session.add(evento)
        db.session.commit()
        
        return jsonify({
            "autorizado": True,
            "nombre": usuario.nombre,
            "timestamp": datetime.utcnow().isoformat(),
            "mensaje": "Acceso autorizado"
        }), 200
    
    except Exception as e:
        print(f"Error en /check: {str(e)}")
        return jsonify({
            "autorizado": False,
            "nombre": None,
            "timestamp": datetime.utcnow().isoformat(),
            "mensaje": f"Error del servidor: {str(e)}"
        }), 500


# ============================================================================
# ENDPOINT 2: POST /log - Registrar evento de acceso
# ============================================================================

@app.route('/log', methods=['POST'])
def log_event():
    """
    Registra un evento de acceso en la base de datos.
    
    Body esperado:
    {
        "token": "token_usuario",
        "timestamp": "ISO-8601 o epoch",
        "resultado": "autorizado/denegado/error"
    }
    
    Respuesta:
    {
        "éxito": true/false,
        "mensaje": "descripción",
        "evento_id": id
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            "éxito": False,
            "mensaje": "Body vacío"
        }), 400
    
    try:
        token = data.get('token')
        timestamp_str = data.get('timestamp')
        resultado = data.get('resultado', 'desconocido')
        descripcion = data.get('descripcion', '')
        
        if not token or not resultado:
            return jsonify({
                "éxito": False,
                "mensaje": "Faltan campos: token, resultado"
            }), 400
        
        # Validar resultado
        resultados_validos = ['autorizado', 'denegado', 'error']
        if resultado not in resultados_validos:
            return jsonify({
                "éxito": False,
                "mensaje": f"Resultado inválido. Valores válidos: {resultados_validos}"
            }), 400
        
        # Procesar timestamp
        if timestamp_str:
            try:
                # Intentar parsear como ISO-8601
                if 'T' in timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                else:
                    # Intentar como epoch
                    timestamp = datetime.fromtimestamp(float(timestamp_str))
            except:
                timestamp = datetime.utcnow()
        else:
            timestamp = datetime.utcnow()
        
        # Buscar usuario por token
        usuario = Usuario.query.filter_by(token=token).first()
        usuario_id = usuario.id if usuario else None
        
        # Crear evento
        evento = EventoAcceso(
            usuario_id=usuario_id,
            token=token,
            timestamp=timestamp,
            resultado=resultado,
            descripcion=descripcion,
            ip_origen=request.remote_addr
        )
        
        db.session.add(evento)
        db.session.commit()
        
        return jsonify({
            "éxito": True,
            "mensaje": "Evento registrado correctamente",
            "evento_id": evento.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        print(f"Error en /log: {str(e)}")
        return jsonify({
            "éxito": False,
            "mensaje": f"Error del servidor: {str(e)}"
        }), 500


# ============================================================================
# ENDPOINT 3: GET /usuarios - Listar usuarios registrados
# ============================================================================

@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    """
    Lista todos los usuarios registrados.
    
    Parámetros opcionales (query string):
        - autorizado: true/false (filtrar por estado)
        - token: filtrar por token específico
    
    Respuesta:
    {
        "total": número,
        "usuarios": [
            {
                "id": id,
                "nombre": "nombre",
                "token": "token",
                "email": "email",
                "autorizado": true/false,
                "fecha_registro": "ISO-8601",
                "fecha_ultimo_acceso": "ISO-8601"
            },
            ...
        ]
    }
    """
    try:
        # Construir query base
        query = Usuario.query
        
        # Filtros opcionales
        autorizado_filter = request.args.get('autorizado')
        if autorizado_filter:
            autorizado_filter = autorizado_filter.lower() == 'true'
            query = query.filter_by(autorizado=autorizado_filter)
        
        token_filter = request.args.get('token')
        if token_filter:
            query = query.filter_by(token=token_filter)
        
        # Ejecutar query
        usuarios = query.order_by(Usuario.fecha_registro.desc()).all()
        
        return jsonify({
            "total": len(usuarios),
            "usuarios": [usuario.to_dict() for usuario in usuarios]
        }), 200
    
    except Exception as e:
        print(f"Error en GET /usuarios: {str(e)}")
        return jsonify({
            "éxito": False,
            "mensaje": f"Error del servidor: {str(e)}"
        }), 500


# ============================================================================
# ENDPOINT 4: POST /usuarios - Registrar nuevo usuario
# ============================================================================

def generar_token(longitud=12):
    """
    Genera un token alfanumérico único.
    
    Args:
        longitud: Longitud del token (por defecto 12)
    
    Returns:
        Cadena alfanumérica
    """
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for _ in range(longitud))


@app.route('/usuarios', methods=['POST'])
def crear_usuario():
    """
    Registra un nuevo usuario con su token único.
    
    Body esperado (opción 1 - token automático):
    {
        "nombre": "nombre_usuario",
        "email": "email@example.com"
    }
    
    Body esperado (opción 2 - token específico):
    {
        "nombre": "nombre_usuario",
        "email": "email@example.com",
        "token": "token_específico"
    }
    
    Respuesta:
    {
        "éxito": true/false,
        "mensaje": "descripción",
        "usuario": {
            "id": id,
            "nombre": "nombre",
            "token": "token_generado",
            "email": "email",
            "autorizado": true,
            "fecha_registro": "ISO-8601"
        }
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            "éxito": False,
            "mensaje": "Body vacío"
        }), 400
    
    try:
        nombre = data.get('nombre')
        email = data.get('email')
        token = data.get('token')
        
        # Validar campos obligatorios
        if not nombre:
            return jsonify({
                "éxito": False,
                "mensaje": "Campo obligatorio: nombre"
            }), 400
        
        if not email:
            return jsonify({
                "éxito": False,
                "mensaje": "Campo obligatorio: email"
            }), 400
        
        # Validar que el email no exista
        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            return jsonify({
                "éxito": False,
                "mensaje": f"El email {email} ya está registrado"
            }), 409
        
        # Generar o validar token
        if not token:
            # Generar token único
            token = generar_token()
            while Usuario.query.filter_by(token=token).first():
                token = generar_token()
        else:
            # Validar que el token no exista
            usuario_existente = Usuario.query.filter_by(token=token).first()
            if usuario_existente:
                return jsonify({
                    "éxito": False,
                    "mensaje": f"El token {token} ya está registrado"
                }), 409
        
        # Crear nuevo usuario
        nuevo_usuario = Usuario(
            nombre=nombre,
            email=email,
            token=token,
            autorizado=True,
            fecha_registro=datetime.utcnow()
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        return jsonify({
            "éxito": True,
            "mensaje": "Usuario registrado correctamente",
            "usuario": nuevo_usuario.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        print(f"Error en POST /usuarios: {str(e)}")
        return jsonify({
            "éxito": False,
            "mensaje": f"Error del servidor: {str(e)}"
        }), 500


# ============================================================================
# ENDPOINT ADICIONAL: GET /usuarios/<int:usuario_id> - Obtener usuario específico
# ============================================================================

@app.route('/usuarios/<int:usuario_id>', methods=['GET'])
def get_usuario(usuario_id):
    """
    Obtiene la información de un usuario específico.
    
    Parámetros:
        usuario_id: ID del usuario
    
    Respuesta:
    {
        "éxito": true/false,
        "usuario": {...} o null
    }
    """
    try:
        usuario = Usuario.query.get(usuario_id)
        
        if not usuario:
            return jsonify({
                "éxito": False,
                "mensaje": f"Usuario con ID {usuario_id} no encontrado"
            }), 404
        
        return jsonify({
            "éxito": True,
            "usuario": usuario.to_dict()
        }), 200
    
    except Exception as e:
        print(f"Error en GET /usuarios/{usuario_id}: {str(e)}")
        return jsonify({
            "éxito": False,
            "mensaje": f"Error del servidor: {str(e)}"
        }), 500


# ============================================================================
# ENDPOINT ADICIONAL: GET /log - Listar eventos
# ============================================================================

@app.route('/log', methods=['GET'])
def get_log():
    """
    Lista eventos de acceso con filtros opcionales.
    
    Parámetros opcionales:
        - token: Filtrar por token
        - resultado: Filtrar por resultado (autorizado/denegado/error)
        - usuario_id: Filtrar por usuario
        - limit: Número máximo de eventos (default 100)
    
    Respuesta:
    {
        "total": número,
        "eventos": [...]
    }
    """
    try:
        # Construir query
        query = EventoAcceso.query
        
        # Filtros opcionales
        token_filter = request.args.get('token')
        if token_filter:
            query = query.filter_by(token=token_filter)
        
        resultado_filter = request.args.get('resultado')
        if resultado_filter:
            query = query.filter_by(resultado=resultado_filter)
        
        usuario_id_filter = request.args.get('usuario_id')
        if usuario_id_filter:
            query = query.filter_by(usuario_id=int(usuario_id_filter))
        
        # Límite
        limit = request.args.get('limit', default=100, type=int)
        
        # Ejecutar query
        eventos = query.order_by(EventoAcceso.timestamp.desc()).limit(limit).all()
        
        return jsonify({
            "total": len(eventos),
            "eventos": [evento.to_dict() for evento in eventos]
        }), 200
    
    except Exception as e:
        print(f"Error en GET /log: {str(e)}")
        return jsonify({
            "éxito": False,
            "mensaje": f"Error del servidor: {str(e)}"
        }), 500


# ============================================================================
# MANEJO DE ERRORES
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Maneja errores 404."""
    return jsonify({
        "éxito": False,
        "mensaje": "Endpoint no encontrado",
        "ruta": request.path
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Maneja errores 405 - método no permitido."""
    return jsonify({
        "éxito": False,
        "mensaje": "Método no permitido",
        "método": request.method,
        "ruta": request.path
    }), 405


@app.errorhandler(500)
def internal_error(error):
    """Maneja errores internos del servidor."""
    db.session.rollback()
    return jsonify({
        "éxito": False,
        "mensaje": "Error interno del servidor"
    }), 500


# ============================================================================
# COMANDOS DE INICIALIZACIÓN
# ============================================================================

def init_db():
    """Inicializa la base de datos y crea tablas."""
    with app.app_context():
        db.create_all()
        print("✓ Base de datos inicializada")
        
        # Crear usuario de prueba
        if Usuario.query.count() == 0:
            usuario_prueba = Usuario(
                nombre="Usuario Prueba",
                email="prueba@example.com",
                token="PRUEBA12345",
                autorizado=True
            )
            db.session.add(usuario_prueba)
            db.session.commit()
            print(f"✓ Usuario de prueba creado: token={usuario_prueba.token}")


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == '__main__':
    init_db()
    print(f"\n{'='*60}")
    print(f"  Servidor de Acceso - Práctica C-3")
    print(f"  Escuchando en http://{config.HOST}:{config.PORT}")
    print(f"{'='*60}\n")
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
