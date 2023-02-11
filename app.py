from bson import ObjectId
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError
from pymongo import ReturnDocument
import datetime
import motor.motor_asyncio
import pydantic
from pydantic import BaseModel
import asyncio
import motor.motor_asyncio
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
profiles = db["profile"]
tanks = db["tanks"]


@app.get("/")
async def home():
    return {"message": "ECSE3038 - Lab 3"}

@app.post("/profile")
async def create_new_profile(request: Request):
    profile = await request.json()
    profile["last_updated"] = str(datetime.datetime.now()) # Add the current time
    try:
        result = await profiles.insert_one(profile) # Insert the profile into the collection
        return {"last_updated": profile["last_updated"], "id": str(result.inserted_id), **profile}
    except DuplicateKeyError as e:
        raise HTTPException(status_code=400, detail="A profile with this username already exists")



@app.get("/profile")
async def get_profile():
    profile = await  profiles.find().to_list(20)# Find the profile
    if len(profile) < 1:
        return
    if profile:
        return profile
    else:
        raise HTTPException(status_code=404, detail="Profile not found")
    

@app.delete("/profile/{id}")
async def delete_data(request: Request, id:str):
    delete_profile = await profiles.delete_one({"_id":ObjectId(id)})
    if delete_profile.deleted_count == 1:
        return Response(status_code=status.HTTP_202_ACCEPTED)

    raise HTTPException(status_code=404, detail=f"{id} not found")


    




@app.get("/data")
async def get_data():
    data = await tanks.find().to_list(20)
    if not data:
        raise HTTPException(status_code=204, detail="No data found")
    return data




@app.post("/data")
async def post_data(request: Request):
    dictionary = await request.json()
    new_profile = await tanks.insert_one(dictionary)
    created_profile = await tanks.find_one({"_id":new_profile.inserted_id})
    return created_profile



@app.delete("/data/{id}")
async def delete_data(request: Request, id:str):
    delete_tank = await tanks.delete_one({"_id":ObjectId(id)})
    if delete_tank.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"{id} not found")



@app.patch("/data/{id}")
async def update_data(id: str, request: Request):
    data = await request.json()
    update = {}
    for key in data:
        if key in ['location', 'lat', 'long', 'percentage_full']:
            update[key] = data[key]

    try:
        result = await tanks.update_one({"_id": ObjectId(id)}, {"$set": update})
        if result.modified_count == 0:
            return JSONResponse(content={"error": "Data not found"}, status_code=status.HTTP_404_NOT_FOUND)
        return JSONResponse(content={"message": "Data updated successfully"}, status_code=status.HTTP_200_OK)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=status.HTTP_400_BAD_REQUEST)

