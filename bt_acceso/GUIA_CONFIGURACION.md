# Guía de Configuración - bt_acceso

## 1. Requisitos Previos

- ESP-IDF instalado (versión >= 5.1)
- Python 3.7 o superior
- Git
- Puerto serial disponible para el ESP32

## 2. Estructura del Proyecto Creada

```
bt_acceso/
├── CMakeLists.txt              # Archivo de configuración CMake raíz
├── sdkconfig.defaults          # Configuraciones predeterminadas de SDK
├── main/
│   ├── CMakeLists.txt          # Configuración CMake para el componente
│   ├── idf_component.yml       # Declaración de dependencias
│   └── main.c                  # Código principal de la aplicación
└── CONFIGURACION.md            # Este archivo
```

## 3. Dependencias Declaradas (idf_component.yml)

```yaml
dependencies:
  idf: ">=5.1"
```

## 4. Configuración CMakeLists.txt

**main/CMakeLists.txt:**
```cmake
idf_component_register(SRCS "main.c"
                       INCLUDE_DIRS ".")
```

## 5. Configuración de Bluetooth Classic

El proyecto incluye `sdkconfig.defaults` con las siguientes opciones habilitadas:

### Bluetooth Controller
- **CONFIG_BT_ENABLED=y** - Bluetooth habilitado
- **CONFIG_BT_CLASSIC_ENABLED=y** - Bluetooth Classic habilitado
- **CONFIG_BT_CTRL_MODE_BR_EDR_ONLY=y** - Modo BR/EDR Only

### Bluedroid Stack
- **CONFIG_BT_BLUEDROID_ENABLED=y** - Stack Bluedroid habilitado
- **CONFIG_BT_BLUEDROID_CLASSIC_BT=y** - Bluetooth Classic en Bluedroid
- **CONFIG_BT_SPP_ENABLED=y** - Serial Port Profile habilitado

## 6. Próximos Pasos

### A. Configurar el Chip Destino

```bash
cd bt_acceso
idf.py set-target esp32
```

### B. Abrir menuconfig

```bash
idf.py menuconfig
```

**Verificar:**
- Component config → Bluetooth → Bluetooth → ✓ Enabled
- Component config → Bluetooth → Bluetooth controller mode → ✓ BR/EDR Only
- Component config → Bluetooth → Bluedroid → Classic Bluetooth → SPP → ✓ Enabled

### C. Compilar el Proyecto

```bash
idf.py build
```

### D. Flashear en el ESP32

```bash
idf.py -p COM#X flash
```
(Reemplaza `#X` con el número de puerto serial, ej: `COM3`)

### E. Monitorear Salida

```bash
idf.py -p COM#X monitor
```

## 7. Notas Importantes

- Bluetooth Classic y Wi-Fi comparten la radio de 2.4 GHz en ESP32
- Esta configuración es solo para Bluetooth Classic (BR/EDR)
- Para BLE (Bluetooth Low Energy), se requiere configuración diferente
- SPP (Serial Port Profile) permite comunicación UART sobre Bluetooth

## 8. Coexistencia WiFi + Bluetooth

Si deseas usar WiFi + Bluetooth simultáneamente:

```c
// En menuconfig:
// Component config → Common ESP-related → 
// → Multiple PHY → Allow coexistence
```

## 9. Archivos Generados Automáticamente

Después de ejecutar `idf.py build`, se crearán:
- `sdkconfig` - Archivo de configuración compilado
- `build/` - Directorio con binarios compilados
- `.git/` - Si inicializas un repositorio Git
