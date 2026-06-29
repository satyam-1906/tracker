from supabase import create_client, Client
from postgrest import ReturnMethod
from typing import Any
import json
import webhook


SUPABASE_URL = 'https://nlhuatireoklugxsyjvv.supabase.co'
SUPABASE_KEY = 'sb_publishable_x-OQLavDzat71hf1n7Oyww_quo62Cp2'

def put_data(data):
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    if len(data) > 0:
        response = supabase.table('tracking_data').insert(data, returning=ReturnMethod.minimal).execute()
        query = list(set([f'"device_id": {element.deviceId}, "last_coords": {[element.latitude, element.longitude]}' for element in data]))
        query = [json.loads(i) for i in query]
        print(query)
        response = supabase.table('Users').upsert(query, returning=ReturnMethod.minimal).execute()

def add_user():
    device_list: list[Any] = []
    user_id_list: list[Any] = []
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    response = supabase.table('tracking_data').select('deviceId').execute()
    device_list = response.data
    response = supabase.table('Users').select('device_id').execute()
    user_id_list = response.data
    device_list = list(set(user['deviceId'] for user in device_list))
    user_id_list = [user['device_id'] for user in user_id_list]
    for user in device_list:
        if user not in user_id_list:
            user_id_list.append(user)
            data = {
                "device_id": user,
                "last_coords": [0.0, 0.0]
                }
            response = supabase.table('Users').insert(data, returning=ReturnMethod.minimal).execute()

def last_known_coords():
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    response = supabase.table('Users').select('device_id, last_coords').execute()
    return response.data
