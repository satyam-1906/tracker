from fastapi import FastAPI, Request, HTTPException
import database
import threading
from fastapi.middleware.cors import CORSMiddleware
import math
from typing import Any, List
import requests

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

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0 # Earth radius in kilometers
    
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    
    a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

async def warn(payload):
    my_location: List[Any]
    alarm: Any
    alarm_activation_state: Any
    alarms = database.get_alarms()
    for alarm in alarms:
        if alarm['device_id'] == payload['deviceId']:
            alarm_activation_state = database.alarm_activation_state(alarm['device_id'])
            if alarm_activation_state[0]['active'] == True:
                my_location = database.my_location()
                curr_dist = haversine(float(my_location[0]['last_coords'][0]), float(my_location[0]['last_coords'][1]), float(payload['latitude']), float(payload['longitude']))
                if curr_dist <= alarm['distance']:
                    response = requests.get(f'https://api.callmebot.com/text.php?user=@asf1906&text=Alarm+for+{alarm['device_id']}')
                    database.set_alarm_activation_state(alarm['device_id'], alarm['distance'], False)
                    threading.Timer(30.0, database.set_alarm_activation_state, args=[alarm['device_id'], alarm['distance'], True]).start()


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
        result = await warn(payload)
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
        return {"status": f'{e}'}
    
@app.get("/getUsers")
async def get_users():
    try:
        users = database.get_users()
        return users
    
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
@app.post("/deleteAlarm")
async def delete_alarm(request: Request):
    try:
        data = await request.json()
        print(data)
        database.delete_alarm(data)
        return {"status": "successful"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'{e}')