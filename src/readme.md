# Drone Circuit

## Componentes

| Componente | Modelo | Cantidad | Proposito |
|------------|--------|----------|-----------|
| Microcontrolador | Arduino R4 WiFi | 1 | Control + comunicacion WiFi |
| Motores DC | 5V 60RPM | 4 | Propulsion |
| Driver de motores | L298P | 2 | Control PWM de motores |
| IMU | MPU6050 | 1 | Estabilizacion de vuelo |
| Bateria | LiPo 2S (8.4V) | 1 | Alimentacion |
| Regulador | LM7805 | 1 | 8.4V a 5V |

## Distribucion de Motores

```
        FRENTE
     [M5]   [M9]      Front-Left (pin 5), Front-Right (pin 9)
       \     /
        \   /
         [A]          Arduino R4 WiFi
        /   \
       /     \
     [M6]   [M10]     Back-Left (pin 6), Back-Right (pin 10)
        ATRAS
```

## Conexiones de Pines

| Motor | Pin PWM | Driver |
|-------|---------|--------|
| Front-Right | 9 | L298P-Right (EnA) |
| Back-Right | 10 | L298P-Right (EnB) |
| Front-Left | 5 | L298P-Left (EnA) |
| Back-Left | 6 | L298P-Left (EnB) |

## Alimentacion

```
LiPo 2S (8.4V) ──┬──> Motores DC (via L298P)
                 │
                 └──> LM7805 ──> 5V ──> Arduino + Logica L298P
```

## Archivos

- `drone-circuit.sim1` - Esquema del circuito (SimulIDE)
- `1-circuit-test/` - Firmware de prueba de motores
