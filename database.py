from supabase import create_client, Client
from postgrest import ReturnMethod
import json
import webhook


SUPABASE_URL = 'https://nlhuatireoklugxsyjvv.supabase.co'
SUPABASE_KEY = 'sb_publishable_x-OQLavDzat71hf1n7Oyww_quo62Cp2'

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def put_data(data):
    if len(data) > 0:
        response = supabase.table('tracking_data').insert(data, returning=ReturnMethod.minimal).execute()
    webhook.calling()

