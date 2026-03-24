

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import servo
import cv2
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import subprocess

import threading


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


ffmpeg_process = None
current_client = None

lock = threading.Lock()
condition = threading.Condition(lock)

cmd = [
    "ffmpeg",
    "-fflags", "nobuffer",
    "-flags", "low_delay",
    "-f", "v4l2",
    "-input_format", "mjpeg",
    "-video_size", "1920x1080",
    "-framerate", "30",
    "-i", "/dev/video0",
    "-f", "image2pipe",
    "-vcodec", "mjpeg",
    "-q:v", "5",   # tăng nhẹ compression → giảm delay
    "-"
]

def start_ffmpeg():
    return subprocess.Popen(
        [
            "ffmpeg",
            "-fflags", "nobuffer",
            "-flags", "low_delay",
            "-f", "v4l2",
            "-input_format", "mjpeg",
            "-video_size", "640x480",
            "-framerate", "25",
            "-i", "/dev/video0",
            "-f", "image2pipe",
            "-vcodec", "mjpeg",
            "-"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        bufsize=0
    )


def stop_ffmpeg():
    global ffmpeg_process
    if ffmpeg_process:
        ffmpeg_process.kill()
        ffmpeg_process = None


latest_frame = None

def read_frames():
    global latest_frame
    start_ffmpeg()

    buffer = b""
    while True:
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

# chạy thread nền
import uuid

def generate_stream(client_id):
    global current_client, ffmpeg_process

    with condition:
        # 🔴 nếu có người đang xem → chờ
        while current_client is not None:
            condition.wait()

        # 👉 chiếm quyền
        current_client = client_id
        ffmpeg_process = start_ffmpeg()

    try:
        while True:
            chunk = ffmpeg_process.stdout.read(4096)
            if not chunk:
                break

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" +
                chunk +
                b"\r\n"
            )

    except GeneratorExit:
        # client đóng tab
        pass

    finally:
        # 🔥 QUAN TRỌNG
        with condition:
            if current_client == client_id:
                stop_ffmpeg()
                current_client = None

                # 👉 đánh thức client đang chờ
                condition.notify_all()

@app.get("/video")
def video_feed():
    client_id = str(uuid.uuid4())

    return StreamingResponse(
        generate_stream(client_id),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

# include router
app.include_router(servo.router)