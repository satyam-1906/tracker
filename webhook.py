from fastapi import FastAPI, Request, HTTPException
import database
import threading

app = FastAPI()
data = []

def calling():
    global data
    if len(data) > 0:
        database.put_data(data)
    call_timer = threading.Timer(5.0, calling)
    call_timer.start()
    data = []

calling()

@app.post("/webhook")
async def handle_webhook(request: Request):
    global data, payload
    try:
        payload = await request.json()
        print(f"Received Webhook Payload: {payload}")
        data.append(payload)
        
        return {"status": "success", "message": "Webhook received"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
app.get('/getMarker')
async def sendMarker():
    return payload