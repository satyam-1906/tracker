from fastapi import FastAPI, Request, HTTPException
import database
import threading
from pydantic import BaseModel

app = FastAPI()
data = []

class DataSchema(BaseModel):
    device_id: str
    latitude: float
    longitude: float
    accuracy: float
    speed: float 
    heading: int
    timestamp: int


def calling():
    global data
    if len(data) > 0:
        database.put_data(data)
    call_timer = threading.Timer(10.0, calling)
    call_timer.start()
    data = []


@app.post("/webhook")
async def handle_webhook(payload: DataSchema):
    global data
    try:
        print(f"Received Webhook Payload: {payload}")
        data.append(payload)
        
        return {"status": "success", "message": "Webhook received"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    

calling()