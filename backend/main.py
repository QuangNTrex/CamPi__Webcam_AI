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

ffmpeg_process = None

cmd = [
    "ffmpeg",
    "-fflags", "nobuffer",
    "-flags", "low_delay",
    "-f", "v4l2",
    "-input_format", "mjpeg",
    "-video_size", "640x480",
    "-framerate", "30",
    "-i", "/dev/video0",
    "-f", "image2pipe",
    "-vcodec", "mjpeg",
    "-q:v", "5",   # tăng nhẹ compression → giảm delay
    "-"
]

def start_ffmpeg():
    global ffmpeg_process
    if ffmpeg_process is None or ffmpeg_process.poll() is not None:
        ffmpeg_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=0
        )
import threading

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
threading.Thread(target=read_frames, daemon=True).start()

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