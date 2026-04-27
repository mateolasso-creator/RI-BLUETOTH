# Guía Rápida - Servidor de Acceso

## Inicio Rápido (3 pasos)

### 1. Instalar dependencias
```bash
cd servidor-acceso
pip install -r requirements.txt
```

### 2. Ejecutar servidor
```bash
python app.py
```

Verás:
```
============================================================
  Servidor de Acceso - Práctica C-3
  Escuchando en http://0.0.0.0:5000
============================================================

✓ Base de datos inicializada
✓ Usuario de prueba creado: token=PRUEBA12345
```

### 3. Probar endpoints (en otra terminal)
```bash
python test_api.py
```

## Endpoints Principales

| Método | Endpoint | Descripción |
|--------|----------|------------|
| GET | `/check?token=TOKEN` | Verificar si token está autorizado |
| POST | `/log` | Registrar evento de acceso |
| GET | `/usuarios` | Listar usuarios |
| POST | `/usuarios` | Crear nuevo usuario |
| GET | `/log` | Listar eventos |

## Ejemplos Rápidos

### Crear usuario
```bash
curl -X POST http://localhost:5000/usuarios \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan",
    "email": "juan@example.com"
  }'
```

### Verificar token
```bash
curl "http://localhost:5000/check?token=PRUEBA12345"
```

### Registrar evento
```bash
curl -X POST http://localhost:5000/log \
  -H "Content-Type: application/json" \
  -d '{
    "token": "PRUEBA12345",
    "resultado": "autorizado"
  }'
```

### Listar usuarios
```bash
curl "http://localhost:5000/usuarios"
```

## Respuestas de Ejemplo

### Token Autorizado
```json
{
  "autorizado": true,
  "nombre": "Usuario Prueba",
  "timestamp": "2026-04-27T12:30:45.123456",
  "mensaje": "Acceso autorizado"
}
```

### Token No Registrado
```json
{
  "autorizado": false,
  "nombre": null,
  "timestamp": "2026-04-27T12:30:45.123456",
  "mensaje": "Token no registrado"
}
```

## Estructura de Datos

### Usuario
```json
{
  "id": 1,
  "nombre": "Usuario Prueba",
  "token": "PRUEBA12345",
  "email": "prueba@example.com",
  "autorizado": true,
  "fecha_registro": "2026-04-27T12:00:00",
  "fecha_ultimo_acceso": "2026-04-27T12:30:45"
}
```

### Evento
```json
{
  "id": 1,
  "usuario_id": 1,
  "token": "PRUEBA12345",
  "timestamp": "2026-04-27T12:30:45",
  "resultado": "autorizado",
  "descripcion": "Acceso autorizado",
  "ip_origen": "127.0.0.1"
}
```

## Solución de Problemas

| Problema | Solución |
|----------|----------|
| Puerto ocupado | Cambiar `PORT` en `config.py` |
| Módulo no encontrado | Ejecutar: `pip install -r requirements.txt` |
| DB corrupta | Borrar `acceso_usuarios.db` y reiniciar |

## Información Adicional

Ver [README.md](README.md) para documentación completa.
