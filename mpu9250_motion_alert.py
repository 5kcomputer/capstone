
import smbus2
import time

# MPU9250 I2C 설정
MPU_ADDR = 0x68
PWR_MGMT_1 = 0x6B
GYRO_XOUT_H = 0x43
ACCEL_XOUT_H = 0x3B  # 가속도 시작 주소

bus = smbus2.SMBus(1)
bus.write_byte_data(MPU_ADDR, PWR_MGMT_1, 0)  # 장치 깨우기

# 감지 기준
GYRO_THRESHOLD = 15.0        # deg/s 이상
ACCEL_THRESHOLD = 0.1        # g 단위
MOVE_DURATION = 0.3          # 감지 시간 기준

def read_word(reg):
    high = bus.read_byte_data(MPU_ADDR, reg)
    low = bus.read_byte_data(MPU_ADDR, reg + 1)
    val = (high << 8) + low
    if val >= 0x8000:
        val = -((65535 - val) + 1)
    return val

def get_gyro():
    x = read_word(GYRO_XOUT_H) / 131.0
    y = read_word(GYRO_XOUT_H + 2) / 131.0
    z = read_word(GYRO_XOUT_H + 4) / 131.0
    return x, y, z

def get_accel():
    x = read_word(ACCEL_XOUT_H) / 16384.0
    y = read_word(ACCEL_XOUT_H + 2) / 16384.0
    z = read_word(ACCEL_XOUT_H + 4) / 16384.0
    return x, y, z

# 메인 루프
try:
    motion_start = None
    alerted = False

    while True:
        gx, gy, gz = get_gyro()
        ax, ay, az = get_accel()

        gyro_movement = max(abs(gx), abs(gy), abs(gz)) > GYRO_THRESHOLD
        accel_movement = (
            abs(ax - 0) > ACCEL_THRESHOLD or
            abs(ay - 0) > ACCEL_THRESHOLD or
            abs(az - 1.0) > ACCEL_THRESHOLD
        )

        if gyro_movement or accel_movement:
            if motion_start is None:
                motion_start = time.time()
            elif (time.time() - motion_start > MOVE_DURATION) and not alerted:
                print("🚨 살짝 움직임 감지됨 (도난 가능성 있음)")
                alerted = True
        else:
            motion_start = None
            alerted = False

        time.sleep(0.2)

except KeyboardInterrupt:
    print("종료됨.")
