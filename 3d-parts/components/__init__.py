"""
Electronic components for drone assembly visualization.

Components:
- Arduino R4 WiFi (main controller)
- MPU6050 / GY-521 (IMU)
- 2S LiPo Battery
- DRV8833 Motor Driver x2 (dual H-bridge each, 1.5A/channel, 4 motors total)
- LM2596 DC-DC Buck Converter with LED Display
"""

from .arduino_r4 import create_arduino_r4
from .mpu6050 import create_mpu6050
from .lipo_2s import create_lipo_2s
from .motor_driver import create_motor_driver
from .lm2596 import create_enclosure

__all__ = [
    'create_arduino_r4',
    'create_mpu6050',
    'create_lipo_2s',
    'create_motor_driver',
    'create_enclosure',
]
