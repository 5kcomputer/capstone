import smbus2
import time
import math

# MPU9250 I2C 설정
MPU_ADDR = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
ACCEL_ZOUT_H = 0x3F

bus = smbus2.SMBus(1)
bus.write_byte_data(MPU_ADDR, PWR_MGMT_1, 0)  # Wake up MPU9250

# 읽기 함수
def read_word(reg):
    high = bus.read_byte_data(MPU_ADDR, reg)
    low = bus.read_byte_data(MPU_ADDR, reg + 1)
    val = (high << 8) + low
    if val >= 0x8000:
        val = -((65535 - val) + 1)
    return val

# Z축 가속도 (금고 들림 감지)
def get_accel_z():
    z = read_word(ACCEL_ZOUT_H)
    accel_z_g = z / 16384.0
    return accel_z_g

# XYZ 가속도 (진동 감지용)
def get_accel():
    x = read_word(ACCEL_XOUT_H) / 16384.0
    y = read_word(ACCEL_XOUT_H + 2) / 16384.0
    z = read_word(ACCEL_XOUT_H + 4) / 16384.0
    return x, y, z

# 기준값
LIFT_THRESHOLD_G = 0.88          # 정지 시 1g, 0.88g 미만이면 들림으로 간주
SHAKE_THRESHOLD = 1.2            # 강한 진동 감지 기준 (주먹질 등)

try:
    while True:
        # 금고 들림 감지
        z_g = get_accel_z()
        if z_g < LIFT_THRESHOLD_G:
            print("🚨 금고가 위로 이동했습니다. (도난 시도 감지)")

        # 진동 감지
        ax, ay, az = get_accel()
        total_force = math.sqrt(ax**2 + ay**2 + az**2)
        deviation = abs(total_force - 1.0)
        if deviation > SHAKE_THRESHOLD:
            print("🚨 비정상적인 진동이 감지되었습니다. (강제 개봉 시도)")

        time.sleep(0.2)

except KeyboardInterrupt:
    print("종료됨.")
