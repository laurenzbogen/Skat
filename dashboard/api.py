from grist_api import GristDocAPI
import os 

SERVER = os.environ["GRIST_URL"]
DOC_ID = os.environ["GRIST_DOC_ID"]
API_TOKEN = os.environ["GRIST_API_TOKEN"]

def get_api():
    api = GristDocAPI(DOC_ID, server=SERVER, api_key=API_TOKEN)
    return api

