# Servidor de Acceso por Bluetooth - Práctica C-3

## Descripción

Servidor HTTP REST que implementa un sistema de control de acceso basado en tokens únicos. Los usuarios se registran con un token específico que se almacena en el servidor y se configura en sus dispositivos (app Android, app ESP32, etc.).

### Características Principales

- ✓ Autenticación por token alfanumérico
- ✓ Base de datos SQLite con usuarios y eventos
- ✓ Registro completo de intentos de acceso
- ✓ API REST con endpoints definidos
- ✓ Filtrado y consultas flexibles
- ✓ Manejo de errores robusto

## Estructura del Proyecto

```
servidor-acceso/
├── app.py                  # Aplicación Flask principal
├── models.py               # Modelos de base de datos
├── config.py               # Configuración
├── requirements.txt        # Dependencias Python
├── test_api.py            # Script de pruebas
├── README.md              # Este archivo
├── acceso_usuarios.db     # Base de datos SQLite (se crea automáticamente)
└── instance/              # Directorio de instancia (se crea automáticamente)
```

## Instalación y Configuración

### 1. Requisitos Previos

- Python 3.7 o superior
- pip (gestor de paquetes de Python)

### 2. Instalar Dependencias

```bash
cd servidor-acceso
pip install -r requirements.txt
```

**Paquetes instalados:**
- Flask 2.3.3 - Framework web
- Flask-SQLAlchemy 3.0.5 - ORM para base de datos
- python-dateutil 2.8.2 - Utilidades de fecha/hora

### 3. Inicializar la Base de Datos

Al ejecutar la aplicación por primera vez:

```bash
python app.py
```

Esto:
- Crea el archivo `acceso_usuarios.db`
- Crea las tablas necesarias
- Crea un usuario de prueba: `PRUEBA12345`

### 4. Ejecutar el Servidor

```bash
python app.py
```

El servidor escuchará en: **http://localhost:5000**

## API REST - Endpoints

### 1. GET /check - Verificar Autorización

Verifica si un token está autorizado para acceder.

**Uso:**
```bash
curl "http://localhost:5000/check?token=PRUEBA12345"
```

**Respuesta exitosa (200):**
```json
{
  "autorizado": true,
  "nombre": "Usuario Prueba",
  "timestamp": "2026-04-27T12:30:45.123456",
  "mensaje": "Acceso autorizado"
}
```

**Respuesta token no registrado (401):**
```json
{
  "autorizado": false,
  "nombre": null,
  "timestamp": "2026-04-27T12:30:45.123456",
  "mensaje": "Token no registrado"
}
```

### 2. POST /log - Registrar Evento

Registra un evento de acceso en la base de datos.

**Uso:**
```bash
curl -X POST http://localhost:5000/log \
  -H "Content-Type: application/json" \
  -d '{
    "token": "PRUEBA12345",
    "timestamp": "2026-04-27T12:30:45",
    "resultado": "autorizado"
  }'
```

**Body esperado:**
```json
{
  "token": "string",           // [Requerido] Token del usuario
  "timestamp": "ISO-8601",     // [Opcional] Marca de tiempo
  "resultado": "string",       // [Requerido] autorizado|denegado|error
  "descripcion": "string"      // [Opcional] Descripción adicional
}
```

**Respuesta exitosa (201):**
```json
{
  "éxito": true,
  "mensaje": "Evento registrado correctamente",
  "evento_id": 1
}
```

### 3. GET /usuarios - Listar Usuarios

Lista todos los usuarios registrados con filtros opcionales.

**Uso sin filtros:**
```bash
curl "http://localhost:5000/usuarios"
```

**Uso con filtros:**
```bash
curl "http://localhost:5000/usuarios?autorizado=true&token=PRUEBA12345"
```

**Parámetros:**
- `autorizado`: true/false - Filtrar por estado
- `token`: string - Filtrar por token específico

**Respuesta (200):**
```json
{
  "total": 2,
  "usuarios": [
    {
      "id": 1,
      "nombre": "Usuario Prueba",
      "token": "PRUEBA12345",
      "email": "prueba@example.com",
      "autorizado": true,
      "fecha_registro": "2026-04-27T12:00:00",
      "fecha_ultimo_acceso": "2026-04-27T12:30:45"
    },
    {
      "id": 2,
      "nombre": "Juan Pérez",
      "token": "JP7489XKWQ",
      "email": "juan@example.com",
      "autorizado": true,
      "fecha_registro": "2026-04-27T12:15:00",
      "fecha_ultimo_acceso": null
    }
  ]
}
```

### 4. POST /usuarios - Crear Usuario

Registra un nuevo usuario con token único.

**Opción 1: Token generado automáticamente**
```bash
curl -X POST http://localhost:5000/usuarios \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "María González",
    "email": "maria@example.com"
  }'
```

**Opción 2: Token específico**
```bash
curl -X POST http://localhost:5000/usuarios \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Carlos López",
    "email": "carlos@example.com",
    "token": "CARLOSLÓPEZ01"
  }'
```

**Body esperado:**
```json
{
  "nombre": "string",    // [Requerido] Nombre del usuario
  "email": "string",     // [Requerido] Email único
  "token": "string"      // [Opcional] Token (se genera si no se proporciona)
}
```

**Respuesta exitosa (201):**
```json
{
  "éxito": true,
  "mensaje": "Usuario registrado correctamente",
  "usuario": {
    "id": 3,
    "nombre": "María González",
    "token": "MG8XQKP9VL",
    "email": "maria@example.com",
    "autorizado": true,
    "fecha_registro": "2026-04-27T12:45:00",
    "fecha_ultimo_acceso": null
  }
}
```

**Respuesta error: Email duplicado (409):**
```json
{
  "éxito": false,
  "mensaje": "El email maria@example.com ya está registrado"
}
```

### 5. GET /log - Listar Eventos (Adicional)

Lista eventos de acceso con filtros opcionales.

**Uso:**
```bash
curl "http://localhost:5000/log?token=PRUEBA12345&limit=10"
```

**Parámetros:**
- `token`: string - Filtrar por token
- `resultado`: autorizado|denegado|error - Filtrar por resultado
- `usuario_id`: number - Filtrar por usuario
- `limit`: number - Límite de resultados (default 100)

**Respuesta (200):**
```json
{
  "total": 3,
  "eventos": [
    {
      "id": 1,
      "usuario_id": 1,
      "token": "PRUEBA12345",
      "timestamp": "2026-04-27T12:30:45",
      "resultado": "autorizado",
      "descripcion": "Acceso autorizado",
      "ip_origen": "127.0.0.1"
    }
  ]
}
```

## Pruebas Automatizadas

Se incluye un script `test_api.py` que prueba todos los endpoints:

```bash
python test_api.py
```

El script ejecuta:
1. Crear usuario
2. Listar usuarios
3. Verificar token existente
4. Verificar token nuevo
5. Verificar token inválido
6. Registrar evento
7. Listar eventos
8. Listar eventos filtrados
9. Pruebas de errores

## Ejemplos de Uso

### Ejemplo 1: Registrar usuario y obtener token

```bash
# 1. Crear usuario
curl -X POST http://localhost:5000/usuarios \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Nuevo Usuario","email":"nuevo@example.com"}'

# Respuesta incluye el token generado:
# {"éxito": true, "usuario": {"token": "A7B9C2D5E8F..."}}

# 2. Verificar autorización
curl "http://localhost:5000/check?token=A7B9C2D5E8F"

# Respuesta: {"autorizado": true, "nombre": "Nuevo Usuario", ...}
```

### Ejemplo 2: Monitorear accesos

```bash
# Listar últimos 20 intentos de acceso
curl "http://localhost:5000/log?limit=20"

# Listar solo accesos autorizados
curl "http://localhost:5000/log?resultado=autorizado&limit=50"

# Listar accesos denegados
curl "http://localhost:5000/log?resultado=denegado"
```

### Ejemplo 3: Gestión de usuarios

```bash
# Listar solo usuarios autorizados
curl "http://localhost:5000/usuarios?autorizado=true"

# Buscar usuario por token
curl "http://localhost:5000/usuarios?token=PRUEBA12345"

# Obtener usuario específico por ID
curl "http://localhost:5000/usuarios/1"
```

## Códigos de Estado HTTP

| Código | Significado |
|--------|------------|
| 200 | OK - Solicitud exitosa |
| 201 | Created - Recurso creado |
| 400 | Bad Request - Solicitud inválida |
| 401 | Unauthorized - Token no autorizado |
| 403 | Forbidden - Acceso denegado |
| 404 | Not Found - Recurso no encontrado |
| 405 | Method Not Allowed - Método no permitido |
| 409 | Conflict - Recurso duplicado |
| 500 | Internal Server Error - Error del servidor |

## Configuración Avanzada

### Cambiar puerto

Editar `config.py`:
```python
PORT = 8080  # Puerto personalizado
```

### Deshabilitar modo DEBUG

```python
DEBUG = False
```

### Acceso desde otras máquinas

Editar `config.py`:
```python
HOST = '0.0.0.0'  # Escuchar en todas las interfaces
```

Luego acceder desde otra máquina:
```bash
curl "http://<IP_DEL_SERVIDOR>:5000/usuarios"
```

## Base de Datos

### Esquema

**Tabla: usuarios**
- `id` (Integer, PK)
- `nombre` (String)
- `token` (String, UNIQUE, INDEX)
- `email` (String, UNIQUE)
- `autorizado` (Boolean)
- `fecha_registro` (DateTime)
- `fecha_ultimo_acceso` (DateTime)

**Tabla: eventos_acceso**
- `id` (Integer, PK)
- `usuario_id` (Integer, FK)
- `token` (String, INDEX)
- `timestamp` (DateTime, INDEX)
- `resultado` (String)
- `descripcion` (String)
- `ip_origen` (String)

### Acceder a la base de datos

```bash
# Usar sqlite3
sqlite3 acceso_usuarios.db

# Dentro de sqlite3:
sqlite> .tables
sqlite> SELECT * FROM usuarios;
sqlite> SELECT * FROM eventos_acceso;
sqlite> .exit
```

## Troubleshooting

### Error: "Port 5000 already in use"

Cambiar puerto en `config.py`:
```python
PORT = 5001
```

### Error: "ImportError: No module named flask"

Instalar dependencias:
```bash
pip install -r requirements.txt
```

### Base de datos corrupta

Eliminar y recrear:
```bash
rm acceso_usuarios.db
python app.py
```

## Integración con ESP32

El ESP32 puede hacer solicitudes al servidor:

```c
#include <esp_http_client.h>

// Verificar autorización
// GET /check?token=XXXXX

// Registrar evento
// POST /log con JSON
```

## Integración con Android

La app Android puede usar bibliotecas como Retrofit o OkHttp para hacer peticiones HTTP.

## Notas de Seguridad

⚠️ **Importante:** Esta implementación es para propósitos educativos.

Para producción:
- [ ] Usar HTTPS con certificados SSL
- [ ] Implementar autenticación del servidor
- [ ] Validar y sanitizar todas las entradas
- [ ] Usar bases de datos más robustas (PostgreSQL)
- [ ] Implementar rate limiting
- [ ] Usar tokens con expiración
- [ ] Encriptar tokens sensibles
- [ ] Implementar logging más detallado
- [ ] Proteger contra inyección SQL (ya se maneja con ORM)

## Licencia

Práctica universitaria - Uso educativo
