'''

KGB API Client

'''



import os
import requests

from dotenv import load_dotenv
load_dotenv()



###################################################################################################################################



API_TOKEN = os.getenv("API_TOKEN")
API_URL = os.getenv("API_URL")
BOT_ID = os.getenv("BOT_ID")



###################################################################################################################################



class KGBAPI:
    def __init__(self):
        
        self.headers = {
            "api-token": API_TOKEN,
        }
    
    
    
    def get_self(self) -> dict|None: return self.get_bot(bot_id = BOT_ID)


    
    def get_bot(self, bot_id: int) -> dict|None:
        '''
        Get a bot's information by its ID.
        '''
        url = f"{API_URL}/v1/bots/{bot_id}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200: return response.json()
        else: raise Exception(f"API Error: {response.status_code} - {response.text}")
    
    
    
    def get_user(self, user_id: int) -> dict|None:
        '''
        Get a user's information by their ID.
        '''
        url = f"{API_URL}/v1/users/{user_id}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200: return response.json()
        else: raise Exception(f"API Error: {response.status_code} - {response.text}")