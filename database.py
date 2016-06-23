# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5
"""
Discord-duckhunt -- database.py
Communication avec la base de données pour stocker les stats sur les canards"""
# Constants #

__author__ = "Arthur — paris-ci"
__licence__ = "WTFPL — 2016"

import dataset

import config

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


def giveBack(logger):
    logger.debug("C'est l'heure de passer à l'armurerie.")
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
        if numero + 1 > len(config.levels):
            level = config.levels[numero]
            return level
        lvexp = config.levels[numero + 1]["expMin"]
        level = config.levels[numero]
        numero += 1

    return level


def getPlayerLevelWithExp(exp):
    lvexp = -9999
    numero = 0
    while lvexp < exp:
        if numero + 1 > len(config.levels):
            level = config.levels[numero]
            return level
        lvexp = config.levels[numero]["expMin"]
        level = config.levels[numero]
        numero += 1

    return level
