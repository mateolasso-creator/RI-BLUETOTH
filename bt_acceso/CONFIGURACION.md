# Proyecto: bt_acceso - Acceso por Bluetooth Classic
# Chip: ESP32
# Framework: ESP-IDF >= 5.1

## Configuración Completada

✓ Proyecto creado: `bt_acceso`
✓ Chip destino: ESP32
✓ Dependencias declaradas en `main/idf_component.yml`: ESP-IDF >= 5.1
✓ Estructura de carpetas correcta
✓ CMakeLists.txt configurado
✓ Configuración Bluetooth aplicada

## Configuraciones de Bluetooth (Ya incluidas en sdkconfig.defaults)

### Componente: Bluetooth
- [x] Bluetooth → Enabled
- [x] Bluetooth controller mode → BR/EDR Only
- [x] Bluedroid → Classic Bluetooth → SPP (Serial Port Profile)

## Pasos siguientes:

1. Abre el proyecto en tu IDE (VS Code con ESP-IDF extension)
2. Ejecuta: `idf.py menuconfig`
3. Verifica que las configuraciones de Bluetooth aparezcan habilitadas
4. Guarda y compila: `idf.py build`
5. Flashea en el ESP32: `idf.py -p COM# flash` (reemplaza # con tu puerto)

## Estructura del Proyecto:

```
bt_acceso/
├── CMakeLists.txt                (configuración de compilación raíz)
├── sdkconfig.defaults            (configuraciones predeterminadas)
├── main/
│   ├── CMakeLists.txt           (configuración del componente main)
│   ├── idf_component.yml        (dependencias del componente)
│   └── main.c                   (código fuente principal)
```

## Verificación:

Para verificar que todo está correctamente configurado:
```bash
cd bt_acceso
idf.py set-target esp32
idf.py menuconfig
```

En menuconfig, confirma:
- Component config → Bluetooth → Bluetooth → Enabled ✓
- Component config → Bluetooth → Bluetooth → Bluetooth controller mode → BR/EDR Only ✓
- Component config → Bluetooth → Bluedroid → Classic Bluetooth → SPP ✓
