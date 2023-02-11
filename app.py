from bson import ObjectId
from fastapi import FastAPI, Request
import motor.motor_asyncio
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import pydantic


app = FastAPI()

origins = [
    "https://ecse3038-lab3-tester.netlify.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


pydantic.json.ENCODERS_BY_TYPE[ObjectId] = str

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://IOT_CLASS:iotclass@cluster0.irzkjxq.mongodb.net/?retryWrites=true&w=majority")
db = client.tank_system

@app.get("/")
async def home():
    return {"message": "ECSE3038 - Lab 3"}



@app.get("/profile")
async def get_profile(request: Request):
    dictionary = await  db["profiles"].find().to_list(20)
    if len(dictionary) < 1:
        return
    return dictionary(0)

