import pigpio
import time
import threading

# ======================
# CONFIG
# ======================
SERVO_PIN = 18

MIN_PW = 500
MAX_PW = 2500

# vùng
EDGE_1 = 60
EDGE_2 = 120

# tốc độ vùng chậm
DELAY_SLOW = 0.03
STEP_SLOW = 1

# ======================
# INIT
# ======================
pi = pigpio.pi()

if not pi.connected:
    raise RuntimeError("Không kết nối được pigpiod")

current_angle = 10
lock = threading.Lock()


# ======================
# UTILS
# ======================
def angle_to_pulse(angle):
    return int(MIN_PW + (angle / 180.0) * (MAX_PW - MIN_PW))


def _set_pwm(angle):
    pi.set_servo_pulsewidth(SERVO_PIN, angle_to_pulse(angle))


# ======================
# MOVE LOGIC
# ======================
def move_slow(from_angle, to_angle):
    if from_angle == to_angle:
        return

    step = STEP_SLOW if to_angle > from_angle else -STEP_SLOW

    for angle in range(int(from_angle), int(to_angle), step):
        _set_pwm(angle)
        time.sleep(DELAY_SLOW)

    _set_pwm(to_angle)
    time.sleep(DELAY_SLOW)


def move_fast(to_angle):
    _set_pwm(to_angle)
    time.sleep(0.5)


# ======================
# MAIN CONTROL
# ======================
def set_angle_smart(target_angle, log=False):
    global current_angle

    target_angle = max(0, min(180, target_angle))

    with lock:
        start = current_angle
        end = target_angle

        if log:
            print(f"\nMove {start}° → {end}°")

        going_up = end > start

        if going_up:
            # vùng 1
            if start < EDGE_1:
                seg_end = min(end, EDGE_1)
                move_slow(start, seg_end)

            # vùng 2
            if start < EDGE_2 and end > EDGE_1:
                seg_end = min(end, EDGE_2)
                move_fast(seg_end)

            # vùng 3
            if end > EDGE_2:
                seg_start = max(start, EDGE_2)
                move_slow(seg_start, end)

        else:
            # vùng 3
            if start > EDGE_2:
                seg_end = max(end, EDGE_2)
                move_slow(start, seg_end)

            # vùng 2
            if start > EDGE_1 and end < EDGE_2:
                seg_end = max(end, EDGE_1)
                move_fast(seg_end)

            # vùng 1
            if end < EDGE_1:
                seg_start = min(start, EDGE_1)
                move_slow(seg_start, end)

        # finalize
        _set_pwm(target_angle)
        current_angle = target_angle

        time.sleep(0.3)
        pi.set_servo_pulsewidth(SERVO_PIN, 0)


# ======================
# API HELPERS
# ======================
def get_angle():
    return current_angle


def stop():
    pi.set_servo_pulsewidth(SERVO_PIN, 0)


def center():
    set_angle_smart(90)