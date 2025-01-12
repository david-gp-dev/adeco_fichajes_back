# -*- coding: utf-8 -*-
"""
FichajesManager.py

Description

@Developer        : David García
@Date			    : 12/01/2025
@Last mod. date     : 12/01/2025 - David García
@Project		    : adeco_fichajes_back
"""

import datetime
import json
import os
from models import User, Fichaje
import threading

_current_file_path = None
_users: dict[int, User] = {}
_lock = threading.Lock()

_folder = "data"
_users_file = "users.jsonl"


def add_fichaje(uid: str) -> tuple[User, datetime.datetime]:
    now_utc, now_local = _get_now()
    file_name = _get_file_path(now_utc)

    if file_name != _current_file_path:
        _load_fichajes(file_name)

    for user in _users.values():
        if uid in user.uids:
            fichaje = Fichaje(user_id=user.id, date_time=now_utc, uid=uid)
            user.add_fichaje(fichaje)
            break
    else:
        fichaje = Fichaje(user_id=None, date_time=now_utc, uid=uid)

    with _lock:
        with open(file_name, "a") as file:
            file.write(json.dumps(fichaje.model_dump_json()) + "\n")

    print(f"Fichaje added: {fichaje}")

    return _users.get(fichaje.user_id) if fichaje.user_id is not None else None, now_local


def load_users():
    global _users
    _users = {}

    if not os.path.exists(_folder):
        os.makedirs(_folder)
    users_path = os.path.join(_folder, _users_file)

    if os.path.exists(users_path):
        with open(users_path) as file:
            for line in file:
                user = json.loads(line)
                _users[user["id"]] = User.model_validate(user)

    print(f"{len(_users)} users loaded.")

    now_utc, now_local = _get_now()
    fichajes_path = _get_file_path(now_utc)
    _load_fichajes(fichajes_path)


def _load_fichajes(file_name: str):
    global _current_file_path
    _current_file_path = file_name

    for user in _users.values():
        user.fichajes = []

    num_fichajes_user = 0
    num_fichajes_desconocidos = 0

    if os.path.exists(file_name):
        with open(file_name) as file:
            for line in file:
                data = json.loads(line)
                fichaje = Fichaje.model_validate_json(data)
                for user in _users.values():
                    if user.id == fichaje.user_id:
                        user.add_fichaje(fichaje)
                        num_fichajes_user += 1
                        break
                else:
                    num_fichajes_desconocidos += 1

    print(f"{num_fichajes_user} fichajes loaded for users.")
    print(f"{num_fichajes_desconocidos} fichajes loaded for unknown users.")


def _get_now() -> tuple[datetime.datetime, datetime.datetime]:
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    now_local = now_utc.astimezone()
    return now_utc, now_local


def _get_file_path(now_utc: datetime.datetime) -> str:
    name = f"{now_utc.year:04}_{now_utc.month:02}_{now_utc.day:02}.jsonl"
    return os.path.join(_folder, name)
