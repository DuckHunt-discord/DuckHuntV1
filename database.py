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
    table.upsert(info, ["id_"])

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
        if stat == "chargeurs" or stat == "balles":
            return 2
        else:
            return 0

def giveBack(logger):
    logger.debug("C'est l'heure de passer à l'armurerie.")
    for table in db.tables:
        logger.debug("|- " + str(table))
        table_ = db.load_table(table_name=table)
        for player in table_.all():
            logger.debug("   |- " + player["name"] )
            table_.upsert({"id_": player["id_"], "chargeurs": 2}, ['id_'])

