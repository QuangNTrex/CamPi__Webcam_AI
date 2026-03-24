# 📷 Smart Camera Control System (Raspberry Pi)

Hệ thống camera realtime sử dụng Raspberry Pi, cho phép:

- 🎥 Xem video trực tiếp với độ trễ thấp (WebRTC)
- 🎮 Điều khiển camera (servo) từ xa qua web
- 🔐 Bảo mật bằng API (FastAPI)
- ⚛️ Giao diện web React

---

## 🚀 Kiến trúc hệ thống

```
📷 Webcam
   ↓
🎥 FFmpeg (encode H264)
   ↓
🟣 WebRTC Server (Janus)
   ↓
⚛️ React (frontend)

-----------------------------

⚛️ React (control)
   ↓
🐍 FastAPI (backend API)
   ↓
GPIO → Servo Motor
```

---

## 🧱 Công nghệ sử dụng

### Backend
- Python (FastAPI)
- pigpio (điều khiển servo)
- FFmpeg (xử lý video)

### Frontend
- ReactJS

### Streaming
- WebRTC (low-latency streaming)
- Janus Gateway (media server)

---

## 📦 Cấu trúc project

```
project/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│
├── frontend/
│   ├── package.json
│   ├── src/
│
└── README.md
```

---

## ⚙️ Cài đặt

### 1. Clone project

```bash
git clone https://github.com/your-username/your-project.git
cd project
```

---

## 🐍 Backend (FastAPI)

### Cài đặt

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Chạy server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## ⚛️ Frontend (React)

### Cài đặt

```bash
cd frontend
npm install
```

### Chạy dev

```bash
npm start
```

### Build production

```bash
npm run build
```

---

## 🎥 Streaming (FFmpeg)

Ví dụ lệnh chạy:

```bash
ffmpeg -f v4l2 -framerate 15 -video_size 640x480 -i /dev/video0 -vcodec h264_v4l2m2m -f mpegts http://127.0.0.1:8001/stream
```

---

## ⚙️ Điều khiển Servo

API endpoint:

### POST `/servo`

```json
{
  "angle": 90
}
```

---

### GET `/status`

```json
{
  "angle": 90
}
```

---

## 🔐 Bảo mật (định hướng)

- JWT Authentication
- HTTPS (Nginx + Let's Encrypt)
- Rate limiting (tránh spam servo)
- Role-based access (user / admin)

---

## 🎯 Tính năng hiện tại

- [x] Stream video từ webcam
- [x] Điều khiển servo qua API
- [x] Frontend React cơ bản
- [x] FFmpeg hoạt động ổn định

---

## 🚀 Hướng phát triển

- [ ] WebRTC (Janus) hoàn chỉnh
- [ ] Authentication (JWT)
- [ ] HTTPS + Nginx
- [ ] Điều khiển realtime (WebSocket)
- [ ] AI (object detection, tracking)

---

## ⚠️ Lưu ý

- Raspberry Pi có tài nguyên hạn chế
- Nên dùng hardware encoding (`h264_v4l2m2m`)
- Không chạy AI nặng trực tiếp trên Pi

---

## 🧠 Tác giả

Developed by: *Your Name*

---

## 📄 License

MIT License
