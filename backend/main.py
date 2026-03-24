from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import servo

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include router
app.include_router(servo.router)