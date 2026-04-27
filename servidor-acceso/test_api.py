"""
Script para probar los endpoints del servidor
Ejecutar: python test_api.py
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def print_response(response, title=""):
    """Imprime la respuesta de forma legible."""
    print(f"\n{'='*60}")
    if title:
        print(f"  {title}")
    print(f"  Status: {response.status_code}")
    print(f"{'='*60}")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(response.text)


def test_crear_usuario():
    """Test: Crear un nuevo usuario"""
    print("\n\n>>> TEST 1: Crear usuario")
    data = {
        "nombre": "Juan Pérez",
        "email": "juan@example.com"
    }
    response = requests.post(f"{BASE_URL}/usuarios", json=data)
    print_response(response, "Crear Usuario")
    return response.json().get('usuario', {}).get('token') if response.status_code == 201 else None


def test_listar_usuarios():
    """Test: Listar usuarios"""
    print("\n\n>>> TEST 2: Listar usuarios")
    response = requests.get(f"{BASE_URL}/usuarios")
    print_response(response, "Listar Usuarios")


def test_check_token(token):
    """Test: Verificar autorización con token"""
    print(f"\n\n>>> TEST 3: Verificar token: {token}")
    response = requests.get(f"{BASE_URL}/check?token={token}")
    print_response(response, f"Check Authorization - Token: {token}")


def test_check_token_invalido():
    """Test: Verificar token inválido"""
    print("\n\n>>> TEST 4: Verificar token inválido")
    response = requests.get(f"{BASE_URL}/check?token=TOKENINVALIDO123")
    print_response(response, "Check Authorization - Token Inválido")


def test_registrar_evento():
    """Test: Registrar evento de acceso"""
    print("\n\n>>> TEST 5: Registrar evento")
    data = {
        "token": "PRUEBA12345",
        "timestamp": datetime.utcnow().isoformat(),
        "resultado": "autorizado",
        "descripcion": "Evento de prueba"
    }
    response = requests.post(f"{BASE_URL}/log", json=data)
    print_response(response, "Registrar Evento")


def test_listar_eventos():
    """Test: Listar eventos"""
    print("\n\n>>> TEST 6: Listar eventos")
    response = requests.get(f"{BASE_URL}/log?limit=5")
    print_response(response, "Listar Eventos")


def test_listar_eventos_por_resultado():
    """Test: Listar eventos filtrados"""
    print("\n\n>>> TEST 7: Listar eventos por resultado")
    response = requests.get(f"{BASE_URL}/log?resultado=autorizado&limit=5")
    print_response(response, "Listar Eventos - Filtro: autorizado")


def test_casos_error():
    """Test: Casos de error"""
    print("\n\n>>> TEST 8: Casos de error")
    
    # Email duplicado
    print("\n  8a) Email duplicado")
    data = {
        "nombre": "Test",
        "email": "juan@example.com"  # Email que ya existe
    }
    response = requests.post(f"{BASE_URL}/usuarios", json=data)
    print_response(response, "Error: Email Duplicado")
    
    # Token duplicado
    print("\n  8b) Token duplicado")
    data = {
        "nombre": "Test2",
        "email": "test2@example.com",
        "token": "PRUEBA12345"  # Token que ya existe
    }
    response = requests.post(f"{BASE_URL}/usuarios", json=data)
    print_response(response, "Error: Token Duplicado")
    
    # Check sin token
    print("\n  8c) Check sin token")
    response = requests.get(f"{BASE_URL}/check")
    print_response(response, "Error: Check sin token")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("  TESTS DEL SERVIDOR DE ACCESO")
    print("  Asegúrate de que el servidor está ejecutándose")
    print("="*60)
    
    try:
        # Verificar que el servidor esté activo
        response = requests.get(f"{BASE_URL}/usuarios", timeout=2)
        print("\n✓ Servidor activo en", BASE_URL)
    except:
        print("\n✗ Error: No se puede conectar al servidor")
        print("  Ejecuta: python app.py")
        exit(1)
    
    # Ejecutar tests
    token_nuevo = test_crear_usuario()
    test_listar_usuarios()
    test_check_token("PRUEBA12345")
    if token_nuevo:
        test_check_token(token_nuevo)
    test_check_token_invalido()
    test_registrar_evento()
    test_listar_eventos()
    test_listar_eventos_por_resultado()
    test_casos_error()
    
    print("\n\n" + "="*60)
    print("  TESTS COMPLETADOS")
    print("="*60 + "\n")
