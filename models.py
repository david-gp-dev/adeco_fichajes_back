# -*- coding: utf-8 -*-
"""
models.py

Description

@Developer        : David García
@Date			    : 12/01/2025
@Last mod. date     : 12/01/2025 - David García
@Project		    : adeco_fichajes_back
"""

import datetime
from pydantic import BaseModel


class Fichaje(BaseModel):
    id: int | None = None
    user_id: int | None
    date_time: datetime.datetime
    uid: str


class User(BaseModel):
    id: int
    name: str
    sex: str
    uids: list[str]
    fichajes: list[Fichaje] = []

    def add_fichaje(self, fichaje: Fichaje):
        self.fichajes.append(fichaje)

    @property
    def is_in(self):
        return len(self.fichajes) % 2 == 1
