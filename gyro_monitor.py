
import smbus2
import time

MPU_ADDR = 0x68
PWR_MGMT_1 = 0x6B
GYRO_XOUT_H = 0x43

bus = smbus2.SMBus(1)
bus.write_byte_data(MPU_ADDR, PWR_MGMT_1, 0)

MOVE_THRESHOLD = 50.0
MOVE_DURATION = 2.0

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

try:
    motion_start = None
    alerted = False

    while True:
        gx, gy, gz = get_gyro()
        max_val = max(abs(gx), abs(gy), abs(gz))

        if max_val > MOVE_THRESHOLD:
            if motion_start is None:
                motion_start = time.time()
            elif (time.time() - motion_start > MOVE_DURATION) and not alerted:
                print("🚨 이동이 감지되었습니다.")
                alerted = True
        else:
            motion_start = None
            alerted = False

        time.sleep(0.2)

except KeyboardInterrupt:
    print("프로그램 종료됨.")
