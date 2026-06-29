from fastapi import FastAPI, Request, HTTPException
import database
import threading
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
data = []

origins = ['http://127.0.0.1:5500']
app.add_middleware(CORSMiddleware,
                    allow_origins=origins,
                    allow_credentials=True,
                    allow_methods=['*'],
                    allow_headers=['*']
                    )

def calling():
    global data
    if len(data) > 0:
        database.put_data(data)
    call_timer = threading.Timer(5.0, calling)
    call_timer.start()
    data = []

calling()

@app.get("/")
@app.head("/")
def read_root():
    return {"status": "healthy"}

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
    
@app.get('/getMarker')
async def sendMarker():
    try:
        return database.last_known_coords()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
@app.post("/newUser")
async def new_user():
    try:
        database.add_user()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
@app.get("/getAlarms")
async def get_alarms():
    try:
        alarms = database.get_alarms()
        return alarms
    except Exception as e:
        raise HTTPException(status_code=400)
    
@app.post("/setAlarm")
async def set_alarm(request: Request):
    try:
        data = await request.json()
        database.set_alarm(data)
        return {"status": "successful"}

    except Exception as e:
        raise HTTPException(status_code=402, detail="Invalid JSON payload")
    
@app.get("/getUsers")
async def get_users():
    try:
        users = database.get_users()
        return users
    
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")