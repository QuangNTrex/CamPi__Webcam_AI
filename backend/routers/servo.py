from fastapi import APIRouter
from models.servo import ServoRequest
import threading
from core import servo

router = APIRouter(prefix="/servo", tags=["Servo"])

@router.post("/")
def set_angle(data: ServoRequest):
    threading.Thread(
        target=servo.set_angle_smart,
        args=(data.angle,)
    ).start()
    return {"status": "moving"}


@router.get("/status")
def status():
    return {"angle": servo.get_angle()}


@router.post("/center")
def center():
    servo.center()
    return {"status": "ok"}


@router.post("/stop")
def stop():
    servo.stop()
    return {"status": "stopped"}