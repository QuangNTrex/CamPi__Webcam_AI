from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import servo
import cv2
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import subprocess


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import threading
import subprocess

ffmpeg_process = None
latest_frame = None
camera_running = False

lock = threading.Lock()

def start_camera():
    global ffmpeg_process, camera_running

    with lock:
        if camera_running:
            return

        ffmpeg_process = subprocess.Popen(
            [
                "ffmpeg",
                "-fflags", "nobuffer",
                "-flags", "low_delay",
                "-f", "v4l2",
                "-input_format", "mjpeg",
                "-video_size", "640x480",  # ⚠️ giảm cho ổn định
                "-framerate", "25",
                "-i", "/dev/video0",
                "-f", "image2pipe",
                "-vcodec", "mjpeg",
                "-q:v", "5",
                "-"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=0
        )

        camera_running = True

        threading.Thread(target=read_frames, daemon=True).start()

def stop_camera():
    global ffmpeg_process, camera_running, latest_frame

    with lock:
        if ffmpeg_process:
            ffmpeg_process.kill()
            ffmpeg_process = None

        latest_frame = None
        camera_running = False

def read_frames():
    global latest_frame, ffmpeg_process, camera_running

    buffer = b""

    while camera_running and ffmpeg_process:
        chunk = ffmpeg_process.stdout.read(4096)

        if not chunk:
            continue

        buffer += chunk

        while True:
            start = buffer.find(b'\xff\xd8')
            end = buffer.find(b'\xff\xd9')

            if start != -1 and end != -1 and end > start:
                frame = buffer[start:end+2]
                buffer = buffer[end+2:]
                latest_frame = frame
            else:
                break
@app.post("/camera/start")
def api_start_camera():
    start_camera()
    return {"status": "camera started"}


@app.post("/camera/stop")
def api_stop_camera():
    stop_camera()
    return {"status": "camera stopped"}

def mjpeg_stream():
    while True:
        if latest_frame:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" +
                latest_frame +
                b"\r\n"
            )

@app.get("/video")
def video_feed():
    return StreamingResponse(
        mjpeg_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

# include router
app.include_router(servo.router)