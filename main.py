# -*- coding: utf-8 -*-
"""
main.py

Description

@Developer        : David García
@Date			    : 12/01/2025
@Last mod. date     : 12/01/2025 - David García
@Project		    : adeco_fichajes_back
"""
import datetime
import hashlib
import uvicorn
from configparser import RawConfigParser
import fastapi
from pydantic import BaseModel


app = fastapi.FastAPI()

users = [
    {"id": 0, "name": "David", "sex": "m", "uids": ["ae:a9:5e:af", "ee:ff:b0:af"], "is_in": False},
    {"id": 3, "name": "Enrique", "sex": "m", "uids": ["5e:77:25:95", "5e:d8:2a:95"], "is_in": False},
    {"id": 4, "name": "Isabel", "sex": "f", "uids": ["9e:29:26:95", "1e:3d:24:95"], "is_in": False},
    {"id": 5, "name": "Angel", "sex": "m", "uids": ["de:62:2b:95", "be:a5:5f:95"], "is_in": False},
    {"id": 6, "name": "Loly", "sex": "f", "uids": ["de:4f:1f:95", "ce:43:01:95"], "is_in": False},
    {"id": 7, "name": "Luis", "sex": "m", "uids": ["0e:47:23:95", "8e:a9:24:95"], "is_in": False},
    {"id": 8, "name": "Choni", "sex": "f", "uids": ["0e:6a:f7:94", "2e:5c:63:95"], "is_in": False},
    {"id": 9, "name": "Manuel", "sex": "m", "uids": ["6e:81:24:95", "9e:73:60:95"], "is_in": False},
    {"id": 11, "name": "Gabriel", "sex": "m", "uids": ["de:9d:26:95", "9e:01:27:95"], "is_in": False},
    {"id": 12, "name": "Pastor", "sex": "m", "uids": ["de:b7:26:95", "fe:28:26:95"], "is_in": False},
    {"id": 14, "name": "Elena", "sex": "f", "uids": ["ee:73:63:95", "7e:75:fd:94"], "is_in": False},
]


@app.get("/")
def read_root():
    return {"Hello": "World"}


class RfidData(BaseModel):
    uid: str
    hash: str


@app.get("/fichajes/datetime.php")
def get_datetime():
    now = datetime.datetime.now()
    res = {"day": now.day, "month": now.month, "year": now.year,
           "hour": now.hour, "minute": now.minute, "second": now.second}
    return res


@app.post("/fichajes/rfid.php")
def read_rfid(uid_data: RfidData):
    # Devolver error 403
    # return fastapi.Response(status_code=403)
    # color y bkg -> 0xRRGGBB
    for user in users:
        if uid_data.uid in user["uids"]:
            is_in = user["is_in"]
            user_id = user["id"]
            sex = user["sex"]

            user["is_in"] = not is_in

            saludo = ("Bienvenida" if sex == "f" else "Bienvenido") if not is_in else "Adios"
            hora = datetime.datetime.now().strftime("%H:%M")

            res = {"txt": f"{saludo}\n{user['name']}\n{hora}",
                   "color": 0x000000, "bkg": 0x00FF00 if not is_in else 0x0000FF,
                   "snd": f"/{'bienvenido' if not is_in else 'adios'}_{user_id}.wav",
                   "vol": 128}
            break
        else:
            res = {"txt": f"Desconocido\n{uid_data.uid}",
                   "color": 0x000000, "bkg": 0xFF0000,
                   "snd": "/error.wav", "vol": 128,
                   "time": 10000}
            print(f"***\n\"{uid_data.uid}\"\n***no está en la lista de usuarios")

    print(uid_data)
    md5 = hashlib.md5()
    md5.update(uid_data.uid.encode())
    print(md5.hexdigest())
    print(res)
    return res


@app.get("/get")
def get_data():
    return "Se ha hecho un GET"


@app.get("/time")
def get_time():
    return datetime.datetime.now().strftime("%Y-%m-%d\n%H:%M:%S")


@app.post("/post")
def post_data(uid_data: RfidData):
    print(uid_data)
    return "Se ha hecho un POST"


if __name__ == "__main__":
    config = RawConfigParser()
    config.read("config.ini")
    port = config.getint("server", "port")
    uvicorn.run(app, host="", port=port)
