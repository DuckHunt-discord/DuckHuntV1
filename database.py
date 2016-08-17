# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5
"""
Discord-duckhunt -- database.py
Communication avec la base de données pour stocker les stats sur les canards"""
# Constants #
import json

from config import defaultSettings

__author__ = "Arthur — paris-ci"

import dataset

import config

db = dataset.connect('sqlite:///scores.db')


def _gettable(server, channel):
    if getPref(server, "global"):
        return db[server.id]
    else:
        return db[server.id + "-" + channel.id]


def getChannelTable(channel):
    server = channel.server
    table = _gettable(server, channel)
    return table


def updatePlayerInfo(channel, info):
    table = getChannelTable(channel)
    table.upsert(info, ["id_"])


def addToStat(channel, player, stat, value):
    dict_ = {"name": player.name, "id_": player.id, stat: int(getStat(channel, player, stat)) + value}
    updatePlayerInfo(channel, dict_)


def setStat(channel, player, stat, value):
    dict_ = {"name": player.name, "id_": player.id,  stat: value}
    updatePlayerInfo(channel, dict_)


def getStat(channel, player, stat, default=0):
    try:
        userDict = getChannelTable(channel).find_one(id_=player.id)
        if userDict[stat] is not None:
            return userDict[stat]
        else:
            setStat(channel, player, stat, default)
            return default

    except:
        setStat(channel, player, stat, default)
        return default


def topScores(channel):
    table = getChannelTable(channel)
    def defaultInt(s):
        try:
            int(s)
            return s
        except ValueError:
            return 0

        except TypeError:
            return 0
    return sorted(table.all(), key=lambda k: defaultInt(k["exp"]), reverse=True)  # Retourne l'ensemble des joueurs dans une liste par exp


def giveBack(logger, player=None, channel = None):
    logger.debug("C'est l'heure de passer à l'armurerie.")
    if player:
        table = _gettable(channel.server, channel)

        user = getChannelTable(channel).find_one(id_=player.id)
        if not "exp" in user or not user["exp"]:
            user["exp"] = 0
        logger.debug("GIVEBACK SUR " + user["name"])

        table.upsert({"id_": user["id_"], "chargeurs": getPlayerLevelWithExp(user["exp"])["chargeurs"], "confisque": False}, ['id_'])
    else:
        for table in db.tables:
            logger.debug("|- " + str(table))
            table_ = db.load_table(table_name=table)
            for player in table_.all():
                if not "exp" in player or not player["exp"]:
                    player["exp"] = 0
                logger.debug("   |- " + player["name"])
                table_.upsert({"id_": player["id_"], "chargeurs": getPlayerLevelWithExp(player["exp"])["chargeurs"], "confisque": False}, ['id_'])

def getPlayerLevel(channel, player):
    plexp = getStat(channel, player, "exp")
    lvexp = -9999
    numero = 0
    while lvexp < plexp:
        level = config.levels[numero]
        if len(config.levels) > numero +1:

            lvexp = config.levels[numero + 1]["expMin"]
            numero += 1
        else:
            return level

    return level


def getPlayerLevelWithExp(exp):
    lvexp = -9999
    numero = 0
    while lvexp < exp:
        level = config.levels[numero]
        if len(config.levels) > numero+1:

            lvexp = config.levels[numero + 1]["expMin"]
            numero += 1
        else:
            return level

    return level

def delServerTables(server):
    for table_name in db.tables:
        table_name.split("-")
        if str(table_name[0]) == str(server.id):
            table_ = db.load_table(table_name=table_name)
            table_.drop()

def delChannelTable(channel):
        table = _gettable(channel.server, channel.id)
        table.drop()


def getPref(server, pref):
    servers = JSONloadFromDisk("channels.json")
    try:
        return servers[server.id]["settings"].get(pref, defaultSettings[pref])
    except KeyError:
        return None


def JSONsaveToDisk(data, filename):
    with open(filename, 'w') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=4, ensure_ascii=False)


def JSONloadFromDisk(filename, default="{}", error=False):
    try:
        file = open(filename, 'r')
        data = json.load(file)
        return data
    except IOError:
        if not error:
            file = open(filename, 'w')
            file.write(default)
            file.close()
            file = open(filename, 'r')
            data = json.load(file)
            return data
        else:
            raise