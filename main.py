import os
from fastapi import FastAPI
from pydantic import BaseModel
import boto3
from botocore.exceptions import BotoCoreError
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

origins = [
    os.getenv('ML_ALLOWED_HOST_DEV'),
    os.getenv('ML_ALLOWED_HOST_PROD')
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ivsClient = boto3.client(
    'ivschat',
    region_name=os.environ.get('ML_AWS_REGION'),
    aws_access_key_id=os.environ.get('ML_AWS_USER_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('ML_AWS_USER_SECRET_ACCESS_KEY')
    )

class ChatUser(BaseModel):
    username: str
    role: str

@app.post("/chat/join")
async def create_token(body:ChatUser):
        if body.role=='admin':
            capabilities=['SEND_MESSAGE','DISCONNECT_USER','DELETE_MESSAGE']
        else:
            capabilities=['SEND_MESSAGE']
        try:
            response = ivsClient.create_chat_token(
                attributes={
                    'username': body.username
                },
                capabilities=capabilities,
                roomIdentifier=os.environ.get('ML_IVS_CHAT_ARN'),
                sessionDurationInMinutes=180, # can change the duration in the IVS console
                userId=body.username,
            )
            return response
        except BotoCoreError as e:
            return {'error':str(e)}