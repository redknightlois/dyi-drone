# Firmware de Drone

## Descripcion del Proyecto

Este proyecto contiene el firmware para un drone. El codigo esta desarrollado para microcontroladores compatibles con Arduino R4.

## Requisitos

- **arduino-cli**: Herramienta de linea de comandos para compilar y cargar firmware
- **SimulIDE**: Simulador de circuitos electronicos (opcional, para pruebas sin hardware)

## Compilacion con arduino-cli

### Instalar dependencias

```bash
arduino-cli core update-index
arduino-cli core install arduino:avr
```

### Compilar el firmware

```bash
arduino-cli compile --fqbn arduino:avr:mega .
```

### Cargar al dispositivo

```bash
arduino-cli upload -p COM3 --fqbn arduino:avr:mega .
```

> Nota: Reemplazar `COM3` con el puerto serial correspondiente del dispositivo.

## Simulacion con SimulIDE

1. Abrir SimulIDE
2. Cargar el archivo `.hex` generado en `build/`
3. Conectar el microcontrolador virtual al circuito del drone
4. Ejecutar la simulacion

### Ubicacion del archivo compilado

Despues de compilar, el archivo `.hex` se encuentra en:

```
build/arduino.avr.mega/firmware.ino.hex
```

## Estructura del Proyecto

```
drone/
├── src/           # Codigo fuente principal
├── lib/           # Bibliotecas externas
├── include/       # Archivos de cabecera
├── build/         # Archivos compilados (generado)
└── claude.md      # Este archivo
```

## Comandos Utiles

| Comando | Descripcion |
|---------|-------------|
| `arduino-cli board list` | Listar placas conectadas |
| `arduino-cli lib search <nombre>` | Buscar bibliotecas |
| `arduino-cli lib install <nombre>` | Instalar biblioteca |
| `arduino-cli monitor -p COM3` | Monitor serial |

## Notas de Desarrollo

- Verificar conexiones antes de cargar firmware al hardware real
- Usar SimulIDE para probar cambios antes de desplegar
- El firmware soporta comunicacion serial para depuracion
- El codigo propiamente dicho tiene que estar en ingles. 