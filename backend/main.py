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


def mjpeg_stream():
    # FFmpeg đọc camera USB MJPEG, pipe ra image2pipe
    cmd = [
        "ffmpeg",
        "-f", "v4l2",
        "-input_format", "mjpeg",
        "-video_size", "640x480",
        "-framerate", "15",
        "-i", "/dev/video0",
        "-f", "image2pipe",
        "-vcodec", "mjpeg",
        "-"
    ]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=0)

    buffer = b""
    while True:
        chunk = process.stdout.read(1024)
        if not chunk:
            break
        buffer += chunk
        while True:
            # tìm start và end marker của JPEG
            start = buffer.find(b'\xff\xd8')
            end = buffer.find(b'\xff\xd9')
            if start != -1 and end != -1 and end > start:
                frame = buffer[start:end+2]
                buffer = buffer[end+2:]
                yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            else:
                break

@app.get("/video")
def video_feed():
    return StreamingResponse(
        mjpeg_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


# include router
app.include_router(servo.router)