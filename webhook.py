from fastapi import FastAPI, Request, HTTPException
import database
import threading

app = FastAPI()
data = []

def calling():
    global data
    if len(data) > 0:
        database.put_data(data)
    call_timer = threading.Timer(3.0, calling)
    call_timer.start()
    data = []


@app.post("/webhook")
async def handle_webhook(request: Request):
    global data
    try:
        payload = await request.json()
        print(f"Received Webhook Payload: {payload}")
        data.append(payload)
        
        return {"status": "success", "message": "Webhook received"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    

calling()