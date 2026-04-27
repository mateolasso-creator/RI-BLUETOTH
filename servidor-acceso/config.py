"""
Configuración del servidor de acceso por Bluetooth
"""
import os
from datetime import datetime

# Configuración de la aplicación Flask
DEBUG = True
HOST = '0.0.0.0'
PORT = 5000

# Configuración de la base de datos
SQLALCHEMY_DATABASE_URI = 'sqlite:///acceso_usuarios.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Directorio de la base de datos
INSTANCE_PATH = os.path.join(os.path.dirname(__file__), 'instance')

# Crear directorio si no existe
if not os.path.exists(INSTANCE_PATH):
    os.makedirs(INSTANCE_PATH)
