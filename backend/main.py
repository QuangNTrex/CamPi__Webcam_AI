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

def stream_mjpeg():
    cmd = [
        "ffmpeg",
        "-f", "v4l2",
        "-input_format", "mjpeg",
        "-video_size", "640x480",
        "-framerate", "15",
        "-i", "/dev/video0",
        "-c", "copy",
        "-f", "mjpeg",
        "-"
    ]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        bufsize=0
    )

    while True:
        data = process.stdout.read(4096)
        if not data:
            break
        yield data


@app.get("/video")
def video_feed():
    return StreamingResponse(
        stream_mjpeg(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

# include router
app.include_router(servo.router)