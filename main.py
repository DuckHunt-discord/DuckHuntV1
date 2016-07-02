# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5
"""
Discord-duckhunt -- main.py
MODULE DESC 
"""
# Constants #

__author__ = "Arthur — paris-ci"
__licence__ = "WTFPL — 2016"

print("Démarrage...")

import argparse

parser = argparse.ArgumentParser(description="DuckHunt, jeu pour tirer sur des canards, pour Discord")
parser.add_argument("-d", "--debug", help="Affiche les messages de débug", action="store_true")

args = parser.parse_args()

import logging
from logging.handlers import RotatingFileHandler

import sys
import discord
import asyncio
import random
import time
import json
import gettext
import database
from prettytable import PrettyTable

from config import *

## INIT ##
logger = logging.getLogger("duckhunt")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
file_handler = RotatingFileHandler('activity.log', 'a', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
steam_handler = logging.StreamHandler()
if args.debug:
    steam_handler.setLevel(logging.DEBUG)
else:
    steam_handler.setLevel(logging.INFO)
logger.addHandler(steam_handler)
steam_handler.setFormatter(formatter)
logger.debug("Logger Initialisé")


# t = gettext.translation('default', localedir='language', languages=[lang])#, fallback=True)
# _ = t.gettext

class Domain:  # gettext config | http://stackoverflow.com/a/38004947/3738545
    def __init__(self, domain):
        self._domain = domain
        self._translations = {}

    def _get_translation(self, language):
        try:
            return self._translations[language]
        except KeyError:
            # The fact that `fallback=True` is not the default is a serious design flaw.
            rv = self._translations[language] = gettext.translation(self._domain, languages=[language], localedir="language", fallback=True)
            return rv

    def get(self, msg, language=lang):
        # logger.debug("Language > " + str(language))
        return self._get_translation(language).gettext(msg)


_ = Domain("default").get
logger.debug("Suppport de la langue implémenté")
logger.info(_("Initialisation du programme, merci de patienter..."))
logger.debug("Version : " + str(sys.version))
client = discord.Client()

planification = {}  # {"channel":[time objects]}
canards = []  # [{"channel" : channel, "time" : time.time()}]

def getPref(server, pref):
    servers = JSONloadFromDisk("channels.json")

    return servers[server.id]["settings"].get(pref, defaultSettings[pref])

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

def allCanardsGo():
    for canard in canards:
        yield from client.send_message(canard["channel"], _(random.choice(canards_bye), language=getPref(canard["channel"].server, "lang")))


@asyncio.coroutine
def messageUser(message, toSend, forcePv=False):
    if getPref(message.server, "pmMostMessages") or forcePv == True:
        yield from client.send_message(message.author, toSend)
    else:
        yield from client.send_message(message.channel, str(message.author.mention) + " > " + toSend)


def representsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def representsFloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


@asyncio.coroutine
def newserver(server):
    servers = JSONloadFromDisk("channels.json", default="{}")
    logger.debug(_("Ajout du serveur {server_id} | {server_name} au fichier...").format(**{"server_id": server.id, "server_name": server.name}))
    servers[server.id] = {}
    JSONsaveToDisk(servers, "channels.json")
    yield from updateJSON()


@asyncio.coroutine
def updateJSON():
    logger.debug("Verfification du fichier channels.json")
    servers = JSONloadFromDisk("channels.json", default="{}")
    logger.debug("Version parsée de servers : " + str(servers))
    for server in servers:
        if not "admins" in servers[server]:
            logger.debug("Le parametre admins n'existait pas dans le serveur {server}, creation...".format(**{"server": server}))
            servers[server]["admins"] = []
        if not "channels" in servers[server]:
            logger.debug("Le parametre channels n'existait pas dans le serveur {server}, creation...".format(**{"server": server}))
            servers[server]["channels"] = []
        if not "settings" in servers[server]:
            logger.debug("Le parametre settings n'existait pas dans le serveur {server}, creation...".format(**{"server": server}))
            servers[server]["settings"] = {}
        if not "detecteur" in servers[server]:
            logger.debug("Le parametre detecteur n'existait pas dans le serveur {server}, creation...".format(**{"server": server}))
            servers[server]["detecteur"] = {}

    JSONsaveToDisk(servers, "channels.json")


@asyncio.coroutine
def planifie():
    global planification

    planification_ = {}

    logger.debug("Time now : " + str(time.time()))
    yield from asyncio.sleep(1)
    now = time.time()
    thisDay = now - (now % 86400)
    servers = JSONloadFromDisk("channels.json", default="{}")

    for server in client.servers:
        logger.debug("Serveur " + str(server) + " (" + str(server.id) + ")")
        if not server.id in servers:
            logger.debug(" |- Serveur inexistant dans channels.json")
        else:
            for channel in server.channels:
                if channel.type == discord.ChannelType.text:
                    logger.debug(" |- Check channel : " + channel.id + " | " + channel.name)
                    permissions = channel.permissions_for(server.me)
                    if permissions.read_messages and permissions.send_messages:
                        # if (channelWL and int(channel.id) in whitelist) or not channelWL:
                        if channel.id in servers[server.id]["channels"]:
                            logger.debug("   |-Ajout channel : {id} ({canardsjours} c/j)".format(**{
                                "id": channel.id, "canardsjours": getPref(server, "canardsJours")
                                }))
                            templist = []
                            for id_ in range(1, getPref(server, "canardsJours") + 1):
                                templist.append(int(thisDay + random.randint(0, 86400)))
                            planification_[channel] = sorted(templist)

    logger.debug("Nouvelle planification : {planification}".format(**{"planification": planification_}))

    logger.debug("Supression de l'ancienne planification, et application de la nouvelle")

    planification = planification_  # {"channel":[time objects]}


def nouveauCanard(canard):
    servers = JSONloadFromDisk("channels.json", default="{}")
    if servers[canard["channel"].server.id]["detecteur"].get(canard["channel"].id, False):
        for playerid in servers[canard["channel"].server.id]["detecteur"][canard["channel"].id]:
            player = discord.utils.get(canard["channel"].server.members, id=playerid)
            yield from client.send_message(player, _("Il y a un canard sur #{channel}",
                                                     getPref(canard["channel"].server, "lang")).format(
                **{"channel": canard["channel"].name}))

        servers[canard["channel"].server.id]["detecteur"].pop(canard["channel"].id)
        JSONsaveToDisk(servers, "channels.json")

    logger.debug("Nouveau canard : " + str(canard))
    if getPref(canard["channel"].server, "randomCanard"):
        canard_str = random.choice(canards_trace) + "  " + random.choice(canards_portrait) + "  " + random.choice(canards_cri)
    else:
        canard_str = "-,,.-'`'°-,,.-'`'° /_^<   QUAACK"
    yield from client.send_message(canard["channel"], canard_str)
    canards.append(canard)


@asyncio.coroutine
def deleteMessage(message):
    if getPref(message.server, "deleteCommands"):
        if message.channel.permissions_for(message.server.me).manage_messages:
            logger.debug("Supression du message : {author} | {content}".format(**{"author": message.author.name, "content": message.content}))
            yield from client.delete_message(message)
        else:
            logger.debug("Supression du message échouée [permission denied] : {author} | {content}".format(
                **{"author": message.author.name, "content": message.content}))


@asyncio.coroutine
def getprochaincanard():
    now = time.time()
    prochaincanard = {"time": 0, "channel": None}
    for channel in planification.keys():  # Determination du prochain canard
        for canard in planification[channel]:
            if canard > now:
                if canard < prochaincanard["time"] or prochaincanard["time"] == 0:
                    prochaincanard = {"time": canard, "channel": channel}
    timetonext = prochaincanard["time"] - time.time()

    if not prochaincanard["channel"]:
        thisDay = now - (now % 86400)
        logger.debug(
            "Plus de canards pour aujourd'hui !  Il faut attendre jusqu'a demain ({demain} sec)".format(**{"demain": thisDay + 86400 - time.time()}))
        # yield from asyncio.sleep(thisDay + 86401 - time.time())
        # prochaincanard = yield from  getprochaincanard()
        return {"time": 0, "channel": None}

    else:

        logger.debug("Prochain canard : {time} (dans {timetonext} sec) sur #{channel} | {server}".format(**{
            "server": prochaincanard["channel"].server.name, "channel": prochaincanard["channel"].name, "timetonext": timetonext,
            "time"  : prochaincanard["time"]
            }))

    return prochaincanard


@asyncio.coroutine
def mainloop():
    logger.debug("Entrée dans la boucle principale")
    exit_ = False
    prochaincanard = yield from getprochaincanard()
    while not exit_:
        now = time.time()

        if (int(now)) % 86400 == 0:
            database.giveBack(logger)
            yield from planifie()
            prochaincanard = yield from getprochaincanard()

        if int(now) % 60 == 0 and prochaincanard["time"] != 0:
            timetonext = prochaincanard["time"] - now
            logger.debug("Prochain canard : {time} (dans {timetonext} sec) sur #{channel} | {server}".format(**{
                "server": prochaincanard["channel"].server.name, "channel": prochaincanard["channel"].name, "timetonext": timetonext,
                "time"  : prochaincanard["time"]
                }))
            logger.debug("Canards en cours : {canards}".format(**{"canards": canards}))

        if prochaincanard["time"] < now and prochaincanard["time"] != 0:  # CANARD !
            yield from nouveauCanard(prochaincanard)
            prochaincanard = yield from getprochaincanard()

        if prochaincanard["time"] == 0:
            prochaincanard = yield from getprochaincanard()

        for canard in canards:
            if int(canard["time"]) + int(getPref(canard["channel"].server, "tempsAttente")) < int(now):  # Canard qui se barre
                logger.debug(
                    "Le canard de {time} est resté trop longtemps, il s'échappe. (il est {now}, et il aurait du rester jusqu'a {shouldwaitto}).".format(**{
                        "time": canard["time"], "now": now, "shouldwaitto": str(
                            int(canard["time"] + getPref(canard["channel"].server, "tempsAttente")))
                        }))
                yield from client.send_message(canard["channel"], _(random.choice(canards_bye),
                                                                    language=getPref(canard["channel"].server, "lang")))
                canards.remove(canard)
        yield from asyncio.sleep(1)


@client.async_event
def on_ready():
    logger.info("Connecté comme {name} | {id}".format(**{"name": client.user.name, "id": client.user.id}))
    yield from updateJSON()
    logger.info("Creation de la planification")
    yield from planifie()
    logger.info("Lancers de canards planifiés")
    logger.info("Initialisation terminée :) Ce jeu, ca va faire un carton !")
    yield from mainloop()


@client.async_event
def on_message(message):
    if message.author == client.user:
        return

    servers = JSONloadFromDisk("channels.json", default="{}")
    if message.channel.is_private:
        client.send_message(message.author,
                            _(":x: Merci de communiquer avec moi dans les channels ou je suis actif."))  # No server so no translation here :x
        return
    if not message.channel.server.id in servers:
        yield from newserver(message.channel.server)
        servers = JSONloadFromDisk("channels.json", default="{}")

    # Messages pour n'importe où
    language = getPref(message.server, "lang")

    if message.content.startswith("!claimserver"):
        logger.debug("> CLAIMSERVER (" + str(message.author) + ")")
        if not servers[message.channel.server.id]["admins"]:
            servers[message.channel.server.id]["admins"] = [message.author.id]
            logger.debug("Ajout de l'admin {admin_name} | {admin_id} au fichier de configuration pour le serveur {server_name} | {server_id}.".format(**{
                "admin_name": message.author.name, "admin_id": message.author.id, "server_name": message.channel.server.name,
                "server_id" : message.channel.server.id
                }))
            yield from messageUser(message, _(":robot: Vous etes maintenant le gestionnaire du serveur !", language))
        else:
            yield from messageUser(message, _(":x: Il y a déjà un admin sur ce serveur...", language))
        JSONsaveToDisk(servers, "channels.json")
        return

    elif message.content.startswith('!addchannel'):
        logger.debug("> ADDCHANNEL (" + str(message.author) + ")")
        if message.author.id in servers[message.channel.server.id]["admins"]:
            if not message.channel.id in servers[message.channel.server.id]["channels"]:
                logger.debug("Ajout de la channel {name} | {id} au fichier...".format(**{"id": message.channel.id, "name": message.channel.name}))
                servers[str(message.channel.server.id)]["channels"].append(message.channel.id)
                JSONsaveToDisk(servers, "channels.json")
                yield from messageUser(message, _(":robot: Channel ajoutée au jeu !", language))
                yield from planifie()

            else:
                yield from messageUser(message, _(":x: Cette channel existe déjà dans le jeu.", language))
        elif message.author.id in admins:
            if not message.channel.id in servers[message.channel.server.id]["channels"]:
                logger.debug("Ajout de la channel {name} | {id} au fichier...".format(**{"id": message.channel.id, "name": message.channel.name}))
                servers[str(message.channel.server.id)]["channels"].append(message.channel.id)
                JSONsaveToDisk(servers, "channels.json")
                yield from messageUser(message, _(":robot: Channel ajoutée au jeu ! :warning: Vous n'etes pas administrateur du serveur.", language))
                yield from planifie()

            else:
                yield from messageUser(message,
                                       _(":x: Cette channel existe déjà dans le jeu. :warning: Vous n'etes pas administrateur du serveur.", language))
        else:
            yield from messageUser(message, _(":x: Vous n'etes pas l'administrateur du serveur.", language))

        return

    if message.channel.id not in servers[message.channel.server.id]["channels"]:
        return

    if database.getStat(message.channel, message.author, "banni", default=False):
        return
    # Messages en whitelist sur les channels activées

    if message.content.startswith('!bang'):
        yield from deleteMessage(message)
        logger.debug("> BANG (" + str(message.author) + ")")
        now = time.time()
        if database.getStat(message.channel, message.author, "confisque", default=False):
            yield from messageUser(message, _("Vous n'etes pas armé", language))
            return

        if database.getStat(message.channel, message.author, "enrayee", default=False):
            yield from messageUser(message, _("Votre arme est enrayée, il faut la recharger pour la décoincer.", language))
            return
        if database.getStat(message.channel, message.author, "sabotee", default="-") is not "-":
            logger.debug("Arme sabotée par : " + database.getStat(message.channel, message.author, "sabotee", default="-"))

            yield from messageUser(message, _("Votre arme est sabotée, remerciez {assaillant} pour cette mauvaise blague.", language).format(
                **{"assaillant": database.getStat(message.channel, message.author, "sabotee", default="-")}))
            database.setStat(message.channel, message.author, "enrayee", True)
            database.setStat(message.channel, message.author, "sabotee", "-")
            return

        if database.getStat(message.channel, message.author, "balles", default=database.getPlayerLevel(message.channel, message.author)["balles"]) <= 0:
            yield from messageUser(message, _(
                "**CHARGEUR VIDE** | Munitions dans l'arme : {balles_actuelles}/{balles_max} | Chargeurs restants : {chargeurs_actuels}/{chargeurs_max}",
                language).format(**{
                "balles_actuelles" : database.getStat(message.channel, message.author, "balles",
                                                      default=database.getPlayerLevel(message.channel, message.author)["balles"]),
                "balles_max"       : database.getPlayerLevel(message.channel, message.author)["balles"],
                "chargeurs_actuels": database.getStat(message.channel, message.author, "chargeurs",
                                                      default=database.getPlayerLevel(message.channel, message.author)["chargeurs"]),
                "chargeurs_max"    : database.getPlayerLevel(message.channel, message.author)["chargeurs"]
                }))
            return
        else:
            if random.randint(1, 100) < database.getPlayerLevel(message.channel, message.author)["fiabilitee"]:
                database.addToStat(message.channel, message.author, "balles", -1)
            else:
                yield from messageUser(message, _("Ton arme s'est enrayée, recharge la pour la décoincer.", language))
                database.setStat(message.channel, message.author, "enrayee", True)
                return

        if canards:
            canardencours = None
            for canard in canards:
                if canard["channel"] == message.channel:
                    canardencours = canard
                    break

            if canardencours:
                if getPref(message.server, "duckLeaves"):
                    if random.randint(1, 100) < 5:
                        canards.remove(canardencours)
                        tmp = yield from client.send_message(message.channel, str(message.author.mention) + _(" > BANG", language))
                        yield from asyncio.sleep(getPref(message.server, "lagOnBang"))
                        yield from client.edit_message(tmp, str(message.author.mention) + _(
                            " > **FLAPP**\tEffrayé par tout ce bruit, le canard s'échappe ! AH BAH BRAVO ! [raté : -1 xp]", language))
                        database.addToStat(message.channel, message.author, "exp", -1)
                        return
                if random.randint(1, 100) < database.getPlayerLevel(message.channel, message.author)["precision"]:
                    canards.remove(canardencours)
                    tmp = yield from client.send_message(message.channel, str(message.author.mention) + _(" > BANG", language))
                    yield from asyncio.sleep(getPref(message.server, "lagOnBang"))
                    database.addToStat(message.channel, message.author, "canardsTues", 1)
                    database.addToStat(message.channel, message.author, "exp", getPref(message.server, "expParCanard"))
                    yield from client.edit_message(tmp, str(message.author.mention) + _(
                        " > :skull_crossbones: **BOUM**\tTu l'as eu en {time} secondes, ce qui te fait un total de {total} canards sur #{channel}.     \_X<   *COUAC*   [{exp} xp]",
                        language).format(**{
                        "time"   : int(now - canardencours["time"]), "total": database.getStat(message.channel, message.author, "canardsTues"),
                        "channel": message.channel, "exp": getPref(message.server, "expParCanard")
                        }))
                    if database.getStat(message.channel, message.author, "meilleurTemps",
                                        default=getPref(message.server, "tempsAttente")) > int(
                                    now - canardencours["time"]):
                        database.setStat(message.channel, message.author, "meilleurTemps", int(now - canardencours["time"]))
                    if getPref(message.server, "findObjects"):
                        if random.randint(0, 100) < 25:
                            yield from messageUser(message, _("En fouillant les buissons autour du canard, tu trouves {inutilitee}", language).format(
                                **{"inutilitee": _(random.choice(inutilite), language)}))

                else:
                    tmp = yield from client.send_message(message.channel, str(message.author.mention) + _(" > BANG", language))
                    yield from asyncio.sleep(getPref(message.server, "lagOnBang"))
                    if random.randint(0, 100) < 5:
                        yield from client.edit_message(tmp, str(message.author.mention) + _(" > **BANG**\tTu à raté le canard... Et tu à tiré sur {player}. ! [raté : -1 xp] [accident de chasse : -2 xp] [arme confisquée]", language).format(**{"player": random.choice(list(message.server.members)).mention}))
                        database.addToStat(message.channel, message.author, "tirsManques", 1)
                        database.addToStat(message.channel, message.author, "chasseursTues", 1)
                        database.addToStat(message.channel, message.author, "exp", -3)
                        database.setStat(message.channel, message.author, "confisque", True)
                        return
                    yield from client.edit_message(tmp, str(message.author.mention) + _(" > **PIEWW**\tTu à raté le canard ! [raté : -1 xp]", language))
                    database.addToStat(message.channel, message.author, "tirsManques", 1)
                    database.addToStat(message.channel, message.author, "exp", -1)
            else:
                yield from messageUser(message, _(
                    "Par chance tu as raté, mais tu visais qui au juste ? Il n'y a aucun canard dans le coin...   [raté : -1 xp] [tir sauvage : -1 xp]",
                    language))
                database.addToStat(message.channel, message.author, "tirsSansCanards", 1)
                database.addToStat(message.channel, message.author, "exp", -2)
        else:
            yield from messageUser(message, _(
                "Par chance tu as raté, mais tu visais qui au juste ? Il n'y a aucun canard dans le coin...   [raté : -1 xp] [tir sauvage : -1 xp]",
                language))
            database.addToStat(message.channel, message.author, "tirsSansCanards", 1)
            database.addToStat(message.channel, message.author, "exp", -2)

    elif message.content.startswith("!reload"):
        yield from deleteMessage(message)
        logger.debug("> RELOAD (" + str(message.author) + ")")
        if database.getStat(message.channel, message.author, "confisque", default=False):
            yield from messageUser(message, _("Vous n'etes pas armé", language))
            
            return
        if database.getStat(message.channel, message.author, "enrayee", default=False):
            yield from messageUser(message, _("Tu décoinces ton arme.", language))
            database.setStat(message.channel, message.author, "enrayee", False)
            if database.getStat(message.channel, message.author, "balles", default=database.getPlayerLevel(message.channel, message.author)["balles"]) > 0:
                
                return

        if database.getStat(message.channel, message.author, "balles", default=database.getPlayerLevel(message.channel, message.author)["balles"]) <= 0:
            if database.getStat(message.channel, message.author, "chargeurs",
                                default=database.getPlayerLevel(message.channel, message.author)["chargeurs"]) > 0:
                database.setStat(message.channel, message.author, "balles", database.getPlayerLevel(message.channel, message.author)["balles"])
                database.addToStat(message.channel, message.author, "chargeurs", -1)
                yield from messageUser(message, _(
                    "Tu recharges ton arme. | Munitions dans l'arme : {balles_actuelles}/{balles_max} | Chargeurs restants : {chargeurs_actuels}/{chargeurs_max}",
                    language).format(**{
                    "balles_actuelles" : database.getStat(message.channel, message.author, "balles",
                                                          default=database.getPlayerLevel(message.channel, message.author)["balles"]),
                    "balles_max"       : database.getPlayerLevel(message.channel, message.author)["balles"],
                    "chargeurs_actuels": database.getStat(message.channel, message.author, "chargeurs",
                                                          default=database.getPlayerLevel(message.channel, message.author)["chargeurs"]),
                    "chargeurs_max"    : database.getPlayerLevel(message.channel, message.author)["chargeurs"]
                    }))
            else:
                yield from messageUser(message, _(
                    "Tu es à court de munitions. | Munitions dans l'arme : {balles_actuelles}/{balles_max} | Chargeurs restants : {chargeurs_actuels}/{chargeurs_max}",
                    language).format(**{
                    "balles_actuelles" : database.getStat(message.channel, message.author, "balles",
                                                          default=database.getPlayerLevel(message.channel, message.author)["balles"]),
                    "balles_max"       : database.getPlayerLevel(message.channel, message.author)["balles"],
                    "chargeurs_actuels": database.getStat(message.channel, message.author, "chargeurs",
                                                          default=database.getPlayerLevel(message.channel, message.author)["chargeurs"]),
                    "chargeurs_max"    : database.getPlayerLevel(message.channel, message.author)["chargeurs"]
                    }))
                return
        else:
            yield from messageUser(message, _(
                "Ton arme n'a pas besoin d'etre rechargée | Munitions dans l'arme : {balles_actuelles}/{balles_max} | Chargeurs restants : {chargeurs_actuels}/{chargeurs_max}",
                language).format(**{
                "balles_actuelles" : database.getStat(message.channel, message.author, "balles",
                                                      default=database.getPlayerLevel(message.channel, message.author)["balles"]),
                "balles_max"       : database.getPlayerLevel(message.channel, message.author)["balles"],
                "chargeurs_actuels": database.getStat(message.channel, message.author, "chargeurs",
                                                      default=database.getPlayerLevel(message.channel, message.author)["chargeurs"]),
                "chargeurs_max"    : database.getPlayerLevel(message.channel, message.author)["chargeurs"]
                }))
            return

    elif message.content.startswith("!shop"):
        yield from deleteMessage(message)
        logger.debug("> SHOP (" + str(message.author) + ")")
        args_ = message.content.split(" ")
        if len(args_) == 1:
            yield from messageUser(message,
                                   _(":mortar_board: Tu dois préciser le numéro de l'item à acheter aprés cette commande. `!shop [N° item]`", language))
            
            return
        else:
            try:
                item = int(args_[1])
            except ValueError:
                yield from messageUser(message, str(
                    message.author.mention) + _(
                    ":mortar_board: Tu dois préciser le numéro de l'item à acheter aprés cette commande. Le numéro donné n'est pas valide. `!shop [N° item]`",
                    language))
                
                return

        if item == 1:
            if database.getStat(message.channel, message.author, "balles", default=database.getPlayerLevel(message.channel, message.author)["balles"]) < \
                    database.getPlayerLevel(message.channel, message.author)["balles"]:
                if database.getStat(message.channel, message.author, "exp") > 7:
                    yield from messageUser(message, _(":money_with_wings: Tu ajoutes une balle dans ton arme pour 7 points d'experience", language))
                    database.addToStat(message.channel, message.author, "balles", 1)
                    database.addToStat(message.channel, message.author, "exp", -7)
                else:
                    yield from messageUser(message, _(":x: Tu n'as pas assez d'experience pour effectuer cet achat !", language))

            else:
                yield from messageUser(message, _(":champagne: Ton chargeur est déjà plein !", language))

        elif item == 2:
            if database.getStat(message.channel, message.author, "chargeurs",
                                default=database.getPlayerLevel(message.channel, message.author)["chargeurs"]) < \
                    database.getPlayerLevel(message.channel, message.author)["chargeurs"]:
                if database.getStat(message.channel, message.author, "exp") > 13:
                    yield from messageUser(message, _(":money_with_wings: Tu ajoutes un chargeur à ta réserve pour 13 points d'experience", language))
                    database.addToStat(message.channel, message.author, "chargeurs", 1)
                    database.addToStat(message.channel, message.author, "exp", -13)
                else:
                    yield from messageUser(message, _(":x: Tu n'as pas assez d'experience pour effectuer cet achat !", language))

            else:
                yield from messageUser(message, _(":champagne: Ta réserve de chargeurs est déjà pleine !", language))

        elif item == 5:
            if database.getStat(message.channel, message.author, "confisque"):
                if database.getStat(message.channel, message.author, "exp") > 40:
                    yield from messageUser(message, _(":money_with_wings: Tu récupéres ton arme pour 40 points d'experience", language))
                    database.setStat(message.channel, message.author, "confisque", False)
                    database.addToStat(message.channel, message.author, "exp", -40)
                else:
                    yield from messageUser(message, _(":x: Tu n'as pas assez d'experience pour effectuer cet achat !", language))

            else:
                yield from messageUser(message, _(":champagne: Ton arme n'est pas confisquée!", language))

        elif item == 17:
            if len(args_) <= 2:
                yield from messageUser(message,  _("C'est pas exactement comme ca que l'on fait... Essaye de mettre le pseudo de la personne ? :p", language))
                
                return
            args_[2] = args_[2].replace("@", "").replace("<", "").replace(">", "")
            target = message.channel.server.get_member_named(args_[2])
            if target is None:
                target = message.channel.server.get_member(args_[2])
                if target is None:
                    yield from messageUser(message, _("Je ne reconnais pas cette personne : {target}", language).format(**{"target": args_[2]}))
                    
                    return

            if database.getStat(message.channel, message.author, "exp") > 14:
                if database.getStat(message.channel, target, "sabotee", "-") == "-":
                    yield from messageUser(message, _(":ok: Tu sabote l'arme de {target}! Elle est maintenant enrayée... Mais il ne le sais pas !",
                                                      language).format(**{"target": target.name}), forcePv=True)
                    database.addToStat(message.channel, message.author, "exp", -14)
                    database.setStat(message.channel, target, "sabotee", message.author.name)
                    
                    return
                else:
                    yield from messageUser(message, _(":ok: L'arme de {target} est déjà sabotée!", language).format(**{"target": target.name}), forcePv=True)
                    
                    return

            else:
                yield from messageUser(message, _(":x: Tu n'as pas assez d'experience pour effectuer cet achat !", language))
        elif item == 20:
            if database.getStat(message.channel, message.author, "exp") > 8:
                yield from messageUser(message, _(
                    ":money_with_wings: Un canard apparaitera dans les 10 prochaines minutes sur le channel, grâce à l'appeau de {mention}. Ca lui coûte 8 exp !",
                    language).format(**{"mention": message.author.mention}))
                database.addToStat(message.channel, message.author, "exp", -8)
                dans = random.randint(0, 60 * 10)
                logger.debug("Appeau lancé pour dans {dans} secondes, sur #{channel_name} | {server_name}.".format(
                    **{"dans": dans, "channel_name": message.channel.name, "server_name": message.channel.server.name}))
                yield from asyncio.sleep(dans)
                yield from nouveauCanard({"time": int(time.time()), "channel": message.channel})

            else:
                yield from messageUser(message, _(":x: Tu n'as pas assez d'experience pour effectuer cet achat !", language))

        elif item == 22:
            if database.getStat(message.channel, message.author, "exp") > 5:

                servers = JSONloadFromDisk("channels.json", default="{}")
                yield from messageUser(message, _(":money_with_wings: Vous serez averti lors du prochain canard sur #{channel_name}", language).format(
                    **{"channel_name": message.channel.name}), forcePv=True)
                if message.channel.id in servers[message.server.id]["detecteur"]:
                    servers[message.server.id]["detecteur"][message.channel.id].append(message.author.id)
                else:
                    servers[message.server.id]["detecteur"][message.channel.id] = [message.author.id]
                JSONsaveToDisk(servers, "channels.json")
                database.addToStat(message.channel, message.author, "exp", -5)

            else:
                yield from messageUser(message, _(":x: Tu n'as pas assez d'experience pour effectuer cet achat !", language))


        elif item == 23:
            if database.getStat(message.channel, message.author, "exp") > 50:
                yield from messageUser(message, _(
                    ":money_with_wings: Tu prépares un canard mécanique sur le chan pour 50 points d'experience. C'est méchant, mais tellement drôle !",
                    language), forcePv=True)
                database.addToStat(message.channel, message.author, "exp", -50)
                yield from asyncio.sleep(75)
                yield from client.send_message(message.channel, _("-_-'`'°-_-.-'`'° %__%   *BZAACK*", language))
            else:
                yield from messageUser(message, _(":x: Tu n'as pas assez d'experience pour effectuer cet achat !", language))

        else:
            yield from messageUser(message, _(":x: Objet non trouvé :'(", language))

    elif getPref(message.server, "malusFauxCanards") and (message.content.startswith("-,,.-") or "QUAACK" in message.content or "QUAAACK" in message.content or "/_^<" in message.content):
        yield from messageUser(message, _("Tu as tendu un drapeau de canard et tu t'es fait tirer dessus. Too bad ! [-1 exp]", language))
        database.addToStat(message.channel, message.author, "exp", -1)

    elif message.content.startswith("!top"):
        yield from deleteMessage(message)
        logger.debug("> TOPSCORES (" + str(message.author) + ")")
        args_ = message.content.split(" ")
        if len(args_) == 1:
            nombre = 15
        else:
            try:
                nombre = int(args_[1])
                if nombre not in range(1, 20 + 1):
                    yield from messageUser(message, _(":mortar_board: Le nombre maximum de joueurs pour le tableau des meilleurs scores est de 20", language))
                    
                    return

            except ValueError:
                yield from messageUser(message, _(":mortar_board: Tu dois préciser le nombre de joueurs à afficher. Le numéro donné n'est pas valide. `!top [nombre joueurs]`",
                    language))
                
                return
        x = PrettyTable()

        x._set_field_names([_("Position", language), _("Pseudo", language), _("Experience", language), _("Canards Tués", language)])
        i = 0
        for joueur in database.topScores(message.channel):
            i += 1
            if (joueur["canardsTues"] is None) or (joueur["canardsTues"] == 0) or ("canardTues" in joueur == False):
                joueur["canardsTues"] = "AUCUN !"
            if joueur["exp"] is None:
                joueur["exp"] = 0
            x.add_row([i, joueur["name"], joueur["exp"], joueur["canardsTues"]])

        yield from messageUser(message,
                               _(":cocktail: Meilleurs scores pour #{channel_name} : :cocktail:\n```{table}```", language).format(
                                   **{"channel_name": message.channel.name, "table": x.get_string(end=nombre, sortby=_("Position", language))}),
                               forcePv=True)

    elif message.content.startswith('!ping'):
        yield from deleteMessage(message)
        logger.debug("> PING (" + str(message.author) + ")")
        tmp = yield from client.send_message(message.channel, _('BOUM', language))
        yield from asyncio.sleep(4)
        yield from client.edit_message(tmp, _('... Oups ! Pardon, pong !', language))

    elif message.content.startswith("!duckstat"):
        yield from deleteMessage(message)
        logger.debug("> DUCKSTATS (" + str(message.author) + ")")

        args_ = message.content.split(" ")
        if len(args_) == 1:
            target = message.author
        else:
            args_[1] = args_[1].replace("@", "").replace("<", "").replace(">", "")
            target = message.channel.server.get_member_named(args_[1])
            if target is None:
                target = message.channel.server.get_member(args_[1])
                if target is None:
                    yield from messageUser(message, _("Je ne reconnais pas cette personne :x", language))
                    
                    return
        x = PrettyTable()

        x._set_field_names([_("Statistique", language), _("Valeur", language)])
        x.add_row([_("Canards tués", language), database.getStat(message.channel, target, "canardsTues")])
        x.add_row([_("Tirs manqués", language), database.getStat(message.channel, target, "tirsManques")])
        x.add_row([_("Tirs sans canards", language), database.getStat(message.channel, target, "tirsSansCanards")])
        x.add_row([_("Meilleur temps de tir", language), database.getStat(message.channel, target, "meilleurTemps",
                                                                          default=getPref(message.server, "tempsAttente"))])
        x.add_row([_("Balles dans le chargeur actuel", language), str(
            database.getStat(message.channel, target, "balles", default=database.getPlayerLevel(message.channel, target)["balles"])) + " / " + str(
            database.getPlayerLevel(message.channel, target)["balles"])])
        x.add_row([_("Chargeurs restants", language), str(
            database.getStat(message.channel, target, "chargeurs", default=database.getPlayerLevel(message.channel, target)["chargeurs"])) + " / " + str(
            database.getPlayerLevel(message.channel, target)["chargeurs"])])
        x.add_row([_("Experience", language), database.getStat(message.channel, target, "exp")])
        x.add_row([_("Niveau actuel", language),
                   str(database.getPlayerLevel(message.channel, target)["niveau"]) + " (" + _(database.getPlayerLevel(message.channel, target)["nom"],
                                                                                              language) + ")"])
        x.add_row([_("Précision des tirs", language), database.getPlayerLevel(message.channel, target)["precision"]])
        x.add_row([_("Fiabilitée de l'arme", language), database.getPlayerLevel(message.channel, target)["fiabilitee"]])

        yield from messageUser(message,
                               _("Statistiques du chasseur : \n```{table}```\nhttps://api-d.com/snaps/table_de_progression.html", language).format(
                                   **{"table": x.get_string()}))

    elif message.content.startswith("!aide") or message.content.startswith("!help") or message.content.startswith("!info"):
        yield from deleteMessage(message)
        yield from messageUser(message, aideMsg, forcePv=True)

    elif message.content.startswith("!giveback"):
        yield from deleteMessage(message)
        logger.debug("> GIVEBACK (" + str(message.author) + ")")

        if int(message.author.id) in admins:
            yield from messageUser(message, _("En cours...", language))
            database.giveBack(logger)
            yield from messageUser(message, _(":ok: Terminé. Voir les logs sur la console ! ", language))
        else:
            yield from messageUser(message, _(":x: Oupas (Permission Denied)", language))

    elif message.content.startswith("!coin"):
        yield from deleteMessage(message)
        logger.debug("> COIN (" + str(message.author) + ")")

        if message.author.id in servers[message.channel.server.id]["admins"] or int(message.author.id) in admins:
            yield from nouveauCanard({"channel": message.channel, "time": int(time.time())})
        else:
            yield from messageUser(message, _(":x: Oupas (Permission Denied)", language))

    elif message.content.startswith("!nextduck"):
        yield from deleteMessage(message)
        logger.debug("> NEXTDUCK (" + str(message.author) + ")")

        if int(message.author.id) in admins:
            prochaincanard = yield from getprochaincanard()
            timetonext = int(prochaincanard["time"] - time.time())
            yield from client.send_message(message.author,
                                           _("Prochain canard : {time} (dans {timetonext} sec) sur #{channel} | {server}", language).format(**{
                                               "server"    : prochaincanard["channel"].server.name, "channel": prochaincanard["channel"].name,
                                               "timetonext": timetonext, "time": prochaincanard["time"]
                                               }))
            deleteMessage(message)
        else:
            yield from messageUser(message, _("Oupas (Permission Denied)", language))

    elif message.content.startswith('!delchannel'):

        logger.debug("> DELCHANNEL (" + str(message.author) + ")")
        if message.author.id in servers[message.channel.server.id]["admins"]:
            if message.channel.id in servers[message.channel.server.id]["channels"]:
                logger.debug("Supression de la channel " + str(message.channel.id) + " | " + str(message.channel.name) + " du fichier...")
                servers[str(message.channel.server.id)]["channels"].remove(message.channel.id)
                JSONsaveToDisk(servers, "channels.json")
                yield from messageUser(message, _(":robot: Channel supprimée du jeu ! Les scores sont neanmoins conservés...", language))
                yield from planifie()

            else:
                yield from messageUser(message, _(":x: Cette channel n'existe pas dans le jeu.", language))
        elif int(message.author.id) in admins:
            if message.channel.id in servers[message.channel.server.id]["channels"]:
                logger.debug("Supression de la channel {channel_id} | {channel_name} du fichier...".format(
                    **{"channel_id": message.channel.id, "channel_name": message.channel.name}))
                servers[str(message.channel.server.id)]["channels"].remove(message.channel.id)
                JSONsaveToDisk(servers, "channels.json")
                yield from messageUser(message, _(
                    ":robot: Channel supprimée du jeu ! Les scores sont neanmoins conservés... :warning: Vous n'etes pas administrateur du serveur",
                    language))
                yield from planifie()

            else:
                yield from messageUser(message,
                                       _(":x: Cette channel n'existe pas dans le jeu. :warning: Vous n'etes pas administrateur du serveur", language))
        else:
            yield from messageUser(message, _(":x: Vous n'etes pas l'administrateur du serveur.", language))

        return

    elif message.content.startswith("!addadmin"):
        logger.debug("> ADDADMIN (" + str(message.author) + ")")

        args_ = message.content.split(" ")
        if len(args_) == 1:
            target = message.author
        else:
            args_[1] = args_[1].replace("@", "").replace("<", "").replace(">", "")
            target = message.channel.server.get_member_named(args_[1])
            if target is None:
                target = message.channel.server.get_member(args_[1])
                if target is None:
                    yield from messageUser(message, _("Je ne reconnais pas cette personne :x", language))
                    
                    return

        if message.author.id in servers[message.channel.server.id]["admins"] or int(message.author.id) in admins:
            servers[message.channel.server.id]["admins"].append(target.id)
            logger.debug("Ajout de l'admin {admin_name} | {admin_id} dans le serveur {server_name} | {server_id}".format(
                **{"admin_id": target.id, "admin_name": target.name, "server_id": message.channel.server.id, "server_name": message.channel.server.name}))
            yield from messageUser(message,
                                   _(":robot: Ajout de l'admin {admin_name} | {admin_id} sur le serveur : {server_name} | {server_id}", language).format(
                                       **{
                                           "admin_id"   : target.id, "admin_name": target.name, "server_id": message.channel.server.id,
                                           "server_name": message.channel.server.name
                                           }))
        else:
            yield from messageUser(message, _(":x: Oops, vous n'etes pas administrateur du serveur...", language))
        JSONsaveToDisk(servers, "channels.json")
        return

    elif message.content.startswith("!set"):
        logger.debug("> SET (" + str(message.author) + ")")
        args_ = message.content.split(" ")
        if len(args_) == 1 or len(args_) > 3:
            yield from messageUser(message, _(":x: Oops, mauvaise syntaxe. !set [paramètre] <valeur>", language))
            x = PrettyTable()

            x._set_field_names([_("Paramètre", language), _("Valeur actuelle", language), _("Valeur par défaut", language)])
            for param in defaultSettings.keys():
                x.add_row([param, getPref(message.server, param), defaultSettings[param]])

            yield from messageUser(message,
                                   _("Liste des paramètres disponibles : \n```{table}```", language).format(**{"table": x.get_string(sortby="Paramètre")}))
            
            return

        if not args_[1] in defaultSettings:
            yield from messageUser(message, _(":x: Oops, le paramètre n'as pas été reconnu. !set [paramètre] <valeur>", language))
            
            return

        if message.author.id in servers[message.channel.server.id]["admins"] or int(message.author.id) in admins:
            if len(args_) == 2:
                if args_[1] in servers[message.server.id]["settings"]: servers[message.server.id]["settings"].pop(args_[1])

                yield from messageUser(message, _(":ok: Valeur réinitialisée a la valeur par défaut !", language))
            else:
                if args_[2].lower() == "true":
                    logger.debug("Valeur passée > bool (True)")
                    args_[2] = True
                elif args_[2].lower() == "false":
                    logger.debug("Valeur passée > bool (False)")
                    args_[2] = False

                elif representsFloat(args_[2]):
                    if float(args_[2]).is_integer():
                        logger.debug("Valeur passée > int")
                        args_[2] = int(args_[2])
                    else:
                        logger.debug("Valeur passée > float")
                        args_[2] = float(args_[2])

                else:
                    logger.debug("Valeur passée > str")
                    args_[2] = str(args_[2])

                if args_[1] == "canardsJours":
                    if args_[2] > 250:
                        args_[2] = 250

                servers[message.server.id]["settings"][args_[1]] = args_[2]

            JSONsaveToDisk(servers, "channels.json")

            yield from messageUser(message,
                                   _(":ok: Valeur modifiée à {value} (type: {type})", language).format(**{"value": args_[2], "type": str(type(args_[2]))}))

            if args_[1] == "canardsJours":
                yield from planifie()



        else:
            yield from messageUser(message, _(":x: Oops, vous n'etes pas administrateur du serveur...", language))

        return

    elif message.content.startswith("!duckplanning"):
        yield from deleteMessage(message)
        logger.debug("> DUCKPLANNING (" + str(message.author) + ")")
        if message.author.id in servers[message.channel.server.id]["admins"] or int(message.author.id) in admins:
            table = ""
            for timestamp in planification[message.channel]:
                table += str(int((time.time() - timestamp) / 60)) + "\n"
            yield from client.send_message(message.author, _(":hammer: TimeDelta en minutes pour les canards sur le chan\n```{table}```", language).format(
                **{"table": table}))
            

        else:
            yield from messageUser(message, _(":x: Oops, vous n'etes pas administrateur du serveur...", language))

    elif message.content.startswith("!dearm"):
        logger.debug("> DEARM (" + str(message.author) + ")")
        if message.author.id in servers[message.channel.server.id]["admins"] or int(message.author.id) in admins:
            args_ = message.content.split(" ")

            if len(args_) == 1:
                yield from messageUser(message, _(":x: Joueur non spécifié", language))
                return
            else:
                args_[1] = args_[1].replace("@", "").replace("<", "").replace(">", "")
                target = message.channel.server.get_member_named(args_[1])
                if target is None:
                    target = message.channel.server.get_member(args_[1])
                    if target is None:
                        yield from messageUser(message, _(":x: Je ne reconnais pas cette personne :x", language))
                        
                        return

            if not database.getStat(message.channel, target, "banni", default=False):
                if target.id not in servers[message.channel.server.id]["admins"] and int(target.id) not in admins:
                    database.setStat(message.channel, target, "banni", True)
                    yield from messageUser(message, _(":ok: Ce joueur est maintenant banni du bot !", language))
                else:
                    yield from messageUser(message, _(":x: Il est admin ce mec, c'est mort !", language))
            else:
                yield from messageUser(message, _(":x: Il est déja banni, lui ^^", language))
        else:
            yield from messageUser(message, _(":x: Oops, vous n'etes pas administrateur du serveur...", language))

    elif message.content.startswith("!rearm"):
        logger.debug("> rearm (" + str(message.author) + ")")
        if message.author.id in servers[message.channel.server.id]["admins"] or int(message.author.id) in admins:
            args_ = message.content.split(" ")

            if len(args_) == 1:
                yield from messageUser(message, _(":x: Joueur non spécifié", language))
                return
            else:
                args_[1] = args_[1].replace("@", "").replace("<", "").replace(">", "")
                target = message.channel.server.get_member_named(args_[1])
                if target is None:
                    target = message.channel.server.get_member(args_[1])
                    if target is None:
                        yield from messageUser(message, _(":x: Je ne reconnais pas cette personne :x", language))
                        
                        return

            if database.getStat(message.channel, target, "banni", default=False):
                database.setStat(message.channel, target, "banni", False)
                yield from messageUser(message, _(":ok: Ce joueur est maintenant dé-banni du bot !", language))
            else:
                yield from messageUser(message, _(":x: Il est pas banni, lui ^^", language))
        else:
            yield from messageUser(message, _(":x: Oops, vous n'etes pas administrateur du serveur...", language))

    elif message.content.startswith("!giveexp"):
        logger.debug("> GIVEEXP (" + str(message.author) + ")")
        if message.author.id in servers[message.channel.server.id]["admins"] or int(message.author.id) in admins:
            args_ = message.content.split(" ")

            if len(args_) < 3:
                messageUser(message, _("Erreur de syntaxe : !giveexp <joueur> <exp>", language))
                return
            else:
                args_[1] = args_[1].replace("@", "").replace("<", "").replace(">", "")
                target = message.channel.server.get_member_named(args_[1])
                if target is None:
                    target = message.channel.server.get_member(args_[1])
                    if target is None:
                        yield from messageUser(message, _(":x: Je ne reconnais pas cette personne :x", language))
                        
                        return
            if not representsInt(args_[2]):
                yield from messageUser(message, _("Erreur de syntaxe : !giveexp <joueur> <exp>", language))
                return
            else:
                args_[2] = int(args_[2])

                database.addToStat(message.channel, target, "exp", args_[2])
                yield from messageUser(message, _(":ok:, il a maintenant {newexp} points d'experience !", language).format(
                    **{"newexp": database.getStat(message.channel, target, "exp")}))

        else:
            yield from messageUser(message, _(":x: Oops, vous n'etes pas administrateur du serveur...", language))

    elif message.content.startswith("!purgemessages"):
        logger.debug("> PURGE MESSAGES (" + str(message.author) + ")")

        if message.author.id in servers[message.channel.server.id]["admins"] or int(message.author.id) in admins:
            if message.channel.permissions_for(message.server.me).manage_messages:
                deleted = yield from client.purge_from(message.channel, limit=500)
                yield from messageUser(message, _("{deleted} message(s) supprimés", language).format(**{"deleted": len(deleted)}))
            else:
                yield from messageUser(message, _("0 message(s) supprimés : permission refusée", language))
        else:
            yield from messageUser(message, _(":x: Oops, vous n'etes pas administrateur du serveur...", language))

@client.async_event
def on_channel_delete(channel):
    logger.info(_("Channel supprimée... {channel_id} | {channel_name}").format(**{"channel_id": channel.id, "channel_name": channel.name}))
    servers = JSONloadFromDisk("channels.json", default="{}")
    if channel.id in servers[channel.server.id]["channels"]:
        for canard in canards:
            if channel in canard["channel"]:
                logger.debug("Canard supprimé : " + str(canard))
                canards.remove(canard)
        servers[channel.server.id]["channels"].remove(channel.id)
        JSONsaveToDisk(servers, "channels.json")


@client.async_event
def on_server_remove(server):
    logger.info(_("Serveur supprimé... {server_id} | {server_name}").format(**{"server_id": server.id, "server_name": server.name}))
    servers = JSONloadFromDisk("channels.json", default="{}")
    if server.id in servers:
        for canard in canards:
            for channel in server.channels:
                if channel == canard["channel"]:
                    logger.Debug("Canard supprimé : " + str(canard))
                    canards.remove(canard)
        servers.pop(server.id)
        JSONsaveToDisk(servers, "channels.json")


@client.async_event
def on_message_edit(old, new):
    if new.author == client.user:
        return

    servers = JSONloadFromDisk("channels.json", default="{}")
    if new.channel.is_private:
        return
    if not new.channel.server.id in servers:
        yield from newserver(new.channel.server)
        servers = JSONloadFromDisk("channels.json", default="{}")

    if new.channel.id not in servers[new.channel.server.id]["channels"]:
        return

    language = getPref(new.server, "lang")
    if getPref(new.server, "malusFauxCanards"):
        if new.content.startswith("-,,.-") or "QUAACK" in new.content or "/_^<" in new.content or "QUAAACK" in new.content:
            yield from messageUser(new, _("Tu as essayé de brain le bot sortant un drapeau de canard après coup! [-5 exp]", language))
            database.addToStat(new.channel, new.author, "exp", -5)



try:
    client.loop.run_until_complete(client.start(token))
except KeyboardInterrupt:
    logger.warn(_("Arret demandé"))
    client.loop.run_until_complete(allCanardsGo())

    client.loop.run_until_complete(client.logout())
    # cancel all tasks lingering
finally:
    client.loop.close()
