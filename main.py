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
from contextlib import asynccontextmanager

import uvicorn
from configparser import RawConfigParser
import fastapi
from pydantic import BaseModel
import fichajes_manager as fm

_version = "1.0.1"

config = RawConfigParser()
config.read("config.ini")
port = config.getint("server", "port")
endpoints_prefix = config.get("server", "endpoints_prefix")


@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    fm.load_users()
    yield


app = fastapi.FastAPI(lifespan=lifespan)


# users = [
#     {"id": 0, "name": "David", "sex": "m", "uids": ["ae:a9:5e:af", "ee:ff:b0:af"]},
#     {"id": 3, "name": "Enrique", "sex": "m", "uids": ["5e:77:25:95", "5e:d8:2a:95"]},
#     {"id": 4, "name": "Isabel", "sex": "f", "uids": ["9e:29:26:95", "1e:3d:24:95"]},
#     {"id": 5, "name": "Angel", "sex": "m", "uids": ["de:62:2b:95", "be:a5:5f:95"]},
#     {"id": 6, "name": "Loly", "sex": "f", "uids": ["de:4f:1f:95", "ce:43:01:95"]},
#     {"id": 7, "name": "Luis", "sex": "m", "uids": ["0e:47:23:95", "8e:a9:24:95"]},
#     {"id": 8, "name": "Choni", "sex": "f", "uids": ["0e:6a:f7:94", "2e:5c:63:95"]},
#     {"id": 9, "name": "Manuel", "sex": "m", "uids": ["6e:81:24:95", "9e:73:60:95"]},
#     {"id": 11, "name": "Gabriel", "sex": "m", "uids": ["de:9d:26:95", "9e:01:27:95"]},
#     {"id": 12, "name": "Pastor", "sex": "m", "uids": ["de:b7:26:95", "fe:28:26:95"]},
#     {"id": 14, "name": "Elena", "sex": "f", "uids": ["ee:73:63:95", "7e:75:fd:94"]},
# ]


@app.get(f"{endpoints_prefix}/")
def read_root():
    return {"Hello": "World"}


class RfidData(BaseModel):
    uid: str
    hash: str
    date_time: str
    msg_id: int


@app.get(f"{endpoints_prefix}/datetime.php")
def get_datetime():
    now = datetime.datetime.now()
    res = {"day": now.day, "month": now.month, "year": now.year,
           "hour": now.hour, "minute": now.minute, "second": now.second,
           "str": now.strftime("%Y-%m-%d %H:%M:%S")}  # El str es para que el dispositivo haga el hash
    print(res)
    return res


@app.post(f"{endpoints_prefix}/rfid.php")
def rfid_post(uid_data: RfidData):
    # color y bkg -> 0xRRGGBB
    if not _validate_hash(uid_data):
        raise fastapi.HTTPException(status_code=403)

    user, local_now = fm.add_fichaje(uid_data.uid)
    if user is not None:
        saludo = ("Bienvenida" if user.sex == "f" else "Bienvenido") if user.is_in else "Adios"
        hora = local_now.strftime("%H:%M")
        user_audio = user.audio if user.audio else user.id
        res = {"txt": f"{saludo}\n{user.name}\n{hora}",
               "color": 0x000000, "bkg": 0x00FF00 if user.is_in else 0x0000FF,
               "snd": f"/{'bienvenido' if user.is_in else 'adios'}_{user_audio}.wav",
               "vol": 200}
    else:
        res = {"txt": f"Desconocido\n{uid_data.uid}",
               "color": 0x000000, "bkg": 0xFF0000,
               "snd": "/error.wav", "vol": 128,
               "time": 10000}

    return res


def _validate_hash(uid_data: RfidData):
    md5 = hashlib.md5()
    md5.update("dj6Fdkafic4jesdKf8y43ulsf".encode())
    md5.update(uid_data.uid.encode())
    md5.update(str(uid_data.msg_id).encode())
    md5.update(uid_data.date_time.encode())
    return md5.hexdigest() == uid_data.hash


if __name__ == "__main__":
    print(f"Iniciando versión {_version}")
    uvicorn.run(app, host="", port=port)
