from fastapi import FastAPI, Request, HTTPException
import database
import threading

app = FastAPI()
data = []

def calling():
    global data
    data = []
    call_timer = threading.Timer(3.0, database.put_data, args=(data))
    call_timer.start()

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