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

def _gettable(server, channel):
    return db[server.id + "-" + channel.id]

def getChannelTable(channel):
    server = channel.server
    table = _gettable(server, channel)
    return table


def updatePlayerInfo(channel, info):
    table = getChannelTable(channel)
    table.upsert(info)

def addToStat(channel, player, stat, value):
    dict_ = {"name": player.name, "id_": player.id, stat: int(getStat(channel, player, stat)) + value }
    updatePlayerInfo(channel, dict_)

def setStat(channel, player, stat, value):
    dict_ = {"name": player.name, "id_": player.id, stat: value }
    updatePlayerInfo(channel, dict_)

def getStat(channel, player, stat):
    try:
        userDict = getChannelTable(channel).find_one(id_=player.id)
        return userDict[stat]
    except:
        return 0

