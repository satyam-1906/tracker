from supabase import create_client, Client
from postgrest import ReturnMethod
from typing import Any
import json
import webhook


SUPABASE_URL = 'https://nlhuatireoklugxsyjvv.supabase.co'
SUPABASE_KEY = 'sb_publishable_x-OQLavDzat71hf1n7Oyww_quo62Cp2'

def put_data(data):
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    query = []
    if len(data) > 0:
        response = supabase.table('tracking_data').insert(data, returning=ReturnMethod.minimal).execute()
        user_list = list(set([f'{element['deviceId']}' for element in data]))
        for user in user_list:
            for element in data[::-1]:
                if user == element['deviceId']:
                    query += [{
                        "device_id": user,
                        "last_coords": [element['latitude'], element['longitude']]
                        }]
                    break
        response = supabase.table('Users').upsert(query, on_conflict='device_id', returning=ReturnMethod.minimal).execute()

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

def get_alarms():
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    response = supabase.table('Alarms').select('device_id, distance').execute()
    return response.data

def set_alarm(data):
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    response = supabase.table('Alarms').insert(data, returning=ReturnMethod.minimal).execute()

def get_users():
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    response = supabase.table('Users').select('device_id').execute()
    return response.data

def delete_alarm(data):
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    response = supabase.table('Alarms').delete().eq("device_id", data['device_id']).eq("distance", data['distance']).execute()

def my_location():
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    response = supabase.table('Users').select('last_coords').eq("device_id", "user_c7c898ad").execute()
    return response.data