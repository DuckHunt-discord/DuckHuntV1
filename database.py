# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5
"""
Discord-duckhunt -- database.py
Communication avec la base de données pour stocker les stats sur les canards"""
# Constants #

__author__ = "Arthur — paris-ci"
__licence__ = "WTFPL — 2016"

import dataset

db = dataset.connect('sqlite:///scores.db')

def _getservertable(server):
    return db[server.id]

def getchanneldict(channel):
    server = channel.server
    serverTable = _getservertable(server)
    return serverTable.find_one(channel=channel.id)

def createChannelTable(channel):
    server = channel.server
    serverTable = _getservertable(server)
    table = serverTable[channel.id]
    table.insert(dict(name='0000', canardsTues=0, tirsManques=0))

