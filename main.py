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
logger.info("Initialisation du programme, merci de patienter...")
logger.debug("Version : " + str(sys.version))
client = discord.Client()

planification = {}  # {"channel":[time objects]}
canards = []  # [{"channel" : channel, "time" : time.time()}]


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

@asyncio.coroutine
def messageUser(message, toSend, forcePv=False):
    servers = JSONloadFromDisk("channels.json", default="{}")
    if servers[message.server.id]["settings"].get("pmMostMessages", defaultSettings["pmMostMessages"]) or forcePv:
        yield from client.send_message(message.author, toSend)
    else:
        yield from client.send_message(message.channel, str(message.author.mention) + " > " + toSend)



@asyncio.coroutine
def representsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

@asyncio.coroutine
def newserver(server):
    servers = JSONloadFromDisk("channels.json", default="{}")
    logger.debug("Ajout du serveur " + str(server.id) + " | " + str(server.name) + " au fichier...")
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
            logger.debug("Le parametre admins n'existait pas dans le serveur " + str(server) + ", creation...")
            servers[server]["admins"] = []
        if not "channels" in servers[server]:
            logger.debug("Le parametre channels n'existait pas dans le serveur " + str(server) + ", creation...")
            servers[server]["channels"] = []
        if not "settings" in servers[server]:
            logger.debug("Le parametre settings n'existait pas dans le serveur " + str(server) + ", creation...")
            servers[server]["settings"] = {}
        if not "detecteur" in servers[server]:
            logger.debug("Le parametre detecteur n'existait pas dans le serveur " + str(server) + ", creation...")
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
                            logger.debug("   |-Ajout channel : " + channel.id + " (" + str(servers[server.id]["settings"].get("canardsJours", defaultSettings["canardsJours"])) + " c/j)")
                            templist = []
                            for id in range(1, servers[server.id]["settings"].get("canardsJours", defaultSettings["canardsJours"]) + 1):
                                templist.append(int(thisDay + random.randint(0, 86400)))
                            planification_[channel] = sorted(templist)

    logger.debug("Nouvelle planification : " + str(planification_))

    logger.debug("Supression de l'ancienne planification, et application de la nouvelle")

    planification = planification_  # {"channel":[time objects]}


def nouveauCanard(canard):
    servers = JSONloadFromDisk("channels.json", default = "{}")
    if servers[canard["channel"].server.id]["detecteur"].get(canard["channel"].id, False):
        for playerid in servers[canard["channel"].server.id]["detecteur"][canard["channel"].id]:
            player = discord.utils.get(canard["channel"].server.members, id=playerid)
            yield from client.send_message(player, "Il y a un canard sur #" + canard["channel"].name)

        servers[canard["channel"].server.id]["detecteur"].pop(canard["channel"].id)
        JSONsaveToDisk(servers, "channels.json")

    logger.debug("Nouveau canard : " + str(canard))

    yield from client.send_message(canard["channel"], "-,_,.-'`'°-,_,.-'`'° /_^<   QUAACK")
    canards.append(canard)


@asyncio.coroutine
def deleteMessage(message):
    servers = JSONloadFromDisk("channels.json", default="{}")
    if servers[message.channel.server.id]["settings"].get("deleteCommands", defaultSettings["deleteCommands"]):
        if message.channel.permissions_for(message.server.me).manage_messages:
            logger.debug("Supression du message : " + message.author.name + " | " + message.content)
            yield from client.delete_message(message)
        else:
            logger.debug("Supression du message échouée [permission denied] : " + message.author.name + " | " + message.content)


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
        logger.debug("Plus de canards pour aujourd'hui !  Il faut attendre jusqu'a demain (" + str(thisDay + 86400 - time.time()) + " sec)")
        # yield from asyncio.sleep(thisDay + 86401 - time.time())
        # prochaincanard = yield from  getprochaincanard()
        return {"time": 0, "channel": None}

    else:

        logger.debug(
            "Prochain canard : " + str(prochaincanard["time"]) + "(dans " + str(timetonext) + " sec) sur #" + prochaincanard["channel"].name + " - " +
            prochaincanard["channel"].server.name)

    return prochaincanard


@asyncio.coroutine
def mainloop():
    logger.debug("Entrée dans la boucle principale")
    exit_ = False
    prochaincanard = yield from getprochaincanard()
    while not exit_:
        now = time.time()
        servers = JSONloadFromDisk("channels.json", default="{}")

        if (int(now)) % 86400 == 0:
            database.giveBack(logger)
            yield from asyncio.sleep(1)
            yield from planifie()
            prochaincanard = yield from getprochaincanard()

        if int(now) % 60 == 0 and prochaincanard["time"] != 0:
            timetonext = prochaincanard["time"] - now
            logger.debug(
                "Prochain canard : " + str(prochaincanard["time"]) + "(dans " + str(timetonext) + " sec) sur #" + prochaincanard["channel"].name + " - " +
                prochaincanard["channel"].server.name)
            logger.debug("Canards en cours : " + str(canards))

        if prochaincanard["time"] < now and prochaincanard["time"] != 0:  # CANARD !
            yield from nouveauCanard(prochaincanard)
            prochaincanard = yield from getprochaincanard()

        if prochaincanard["time"] == 0:
            prochaincanard = yield from getprochaincanard()

        for canard in canards:
            if int(canard["time"] + servers[canard["channel"].server.id]["settings"].get("tempsAttente", defaultSettings["tempsAttente"])) < int(now):  # Canard qui se barre
                logger.debug("Le canard de " + str(canard["time"]) + " est resté trop longtemps, il s'échappe. (il est " + str(
                    int(now)) + ", et il aurait du rester jusqu'a " + str(int(canard["time"] + servers[canard["channel"].server.id]["settings"].get("tempsAttente", defaultSettings["tempsAttente"]))) + " )")
                yield from client.send_message(canard["channel"], "Le canard s'échappe.     ·°'\`'°-.,¸¸.·°'\`")
                canards.remove(canard)
        yield from asyncio.sleep(1)


@client.async_event
def on_ready():
    logger.info("Connecté comme " + str(client.user.name) + " | " + str(client.user.id))
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
        client.send_message(message.author, ":x: Merci de communiquer avec moi dans les channels ou je suis actif.")
        return
    if not message.channel.server.id in servers:
        yield from newserver(message.channel.server)
        servers = JSONloadFromDisk("channels.json", default="{}")

    # Messages pour n'importe où

    if message.content.startswith("!claimserver"):
        logger.debug("> CLAIMSERVER (" + str(message.author) + ")")
        if not servers[message.channel.server.id]["admins"]:
            servers[message.channel.server.id]["admins"] = [message.author.id]
            logger.debug("Ajout de l'admin " + str(message.author.id) + " | " + str(message.author.name) + " au fichier pour le serveur " + str(
                message.channel.server.id) + " | " + str(message.channel.server.name))
            yield from messageUser(message, ":robot: Vous etes maintenent le gestionnaire du serveur !")
        else:
            yield from messageUser(message, ":x: Il y a déjà un admin sur ce serveur...")
        JSONsaveToDisk(servers, "channels.json")
        return

    elif message.content.startswith('!addchannel'):
        logger.debug("> ADDCHANNEL (" + str(message.author) + ")")
        if message.author.id in servers[message.channel.server.id]["admins"]:
            if not message.channel.id in servers[message.channel.server.id]["channels"]:
                logger.debug("Ajout de la channel " + str(message.channel.id) + " | " + str(message.channel.name) + " au fichier...")
                servers[str(message.channel.server.id)]["channels"].append(message.channel.id)
                JSONsaveToDisk(servers, "channels.json")
                yield from messageUser(message, ":robot: Channel ajoutée au jeu !")
                yield from planifie()

            else:
                yield from messageUser(message, ":x: Cette channel existe déjà dans le jeu.")
        elif message.author.id in admins:
            if not message.channel.id in servers[message.channel.server.id]["channels"]:
                logger.debug("Ajout de la channel " + str(message.channel.id) + " | " + str(message.channel.name) + " au fichier...")
                servers[str(message.channel.server.id)]["channels"].append(message.channel.id)
                JSONsaveToDisk(servers, "channels.json")
                yield from messageUser(message, " > :robot: Channel ajoutée au jeu ! :warning: Vous n'etes pas administrateur du serveur.")
                yield from planifie()

            else:
                yield from messageUser(message, ":x: Cette channel existe déjà dans le jeu. :warning: Vous n'etes pas administrateur du serveur.")
        else:
            yield from messageUser(message, " > :x: Vous n'etes pas l'administrateur du serveur.")

        return

    if message.channel.id not in servers[message.channel.server.id]["channels"]:
        return

    if database.getStat(message.channel, message.author, "banni", default=False):
        return
    # Messages en whitelist sur les channels activées

    if message.content.startswith('!bang'):
        logger.debug("> BANG (" + str(message.author) + ")")
        now = time.time()
        if database.getStat(message.channel, message.author, "confisque", default=False):
            yield from messageUser(message, "Vous n'etes pas armé")
            return

        if database.getStat(message.channel, message.author, "enrayee", default=False):
            yield from messageUser(message, "Votre arme est enrayée, il faut la recharger pour la décoincer.")
            return
        if database.getStat(message.channel, message.author, "sabotee", default="-") is not "-":
            logger.debug("Arme sabotée par : " + database.getStat(message.channel, message.author, "sabotee", default="-"))

            yield from messageUser(message, "Votre arme est sabotée, remerciez " + database.getStat(message.channel,
                                                                                                                                    message.author,
                                                                                                                                    "sabotee",
                                                                                                                                    default="-") + " pour cette mauvaise blague.")
            database.setStat(message.channel, message.author, "enrayee", True)
            database.setStat(message.channel, message.author, "sabotee", "-")
            return

        if database.getStat(message.channel, message.author, "balles", default=database.getPlayerLevel(message.channel, message.author)["balles"]) <= 0:
            yield from messageUser(message, "**CHARGEUR VIDE** | Munitions dans l'arme : " + str(
                database.getStat(message.channel, message.author, "balles",
                                 default=database.getPlayerLevel(message.channel, message.author)["balles"])) + "/" + str(
                database.getPlayerLevel(message.channel, message.author)["balles"]) + " | Chargeurs restants : " + str(
                database.getStat(message.channel, message.author, "chargeurs",
                                 default=database.getPlayerLevel(message.channel, message.author)["chargeurs"])) + "/" + str(
                database.getPlayerLevel(message.channel, message.author)["chargeurs"]))
            return
        else:
            if random.randint(1, 100) < database.getPlayerLevel(message.channel, message.author)["fiabilitee"]:
                database.addToStat(message.channel, message.author, "balles", -1)
            else:
                yield from messageUser(message, "Ton arme s'est enrayée, recharge la pour la décoincer.")
                database.setStat(message.channel, message.author, "enrayee", True)
                return

        if canards:
            canardencours = None
            for canard in canards:
                if canard["channel"] == message.channel:
                    canardencours = canard
                    break

            if canardencours:
                if servers[message.server.id]["settings"].get("duckLeaves", defaultSettings["duckLeaves"]):
                    if random.randint(1, 100) < 5:
                        canards.remove(canardencours)
                        tmp = yield from client.send_message(message.channel, str(message.author.mention) + " > BANG")
                        yield from asyncio.sleep(1)
                        yield from client.edit_message(tmp, str(
                            message.author.mention) + " > **FLAPP**\tEffrayé par tout ce bruit, le canard s'échappe ! AH BAH BRAVO ! [raté : -1 xp]")
                        database.addToStat(message.channel, message.author, "exp", -1)
                        return
                if random.randint(1, 100) < database.getPlayerLevel(message.channel, message.author)["precision"]:
                    canards.remove(canardencours)
                    tmp = yield from client.send_message(message.channel, str(message.author.mention) + " > BANG")
                    yield from asyncio.sleep(1)
                    database.addToStat(message.channel, message.author, "canardsTues", 1)
                    database.addToStat(message.channel, message.author, "exp", 10)
                    yield from client.edit_message(tmp, str(message.author.mention) + " > :skull_crossbones: **BOUM**\tTu l'as eu en " + str(
                        int(now - canardencours["time"])) + " secondes, ce qui te fait un total de " + str(
                        database.getStat(message.channel, message.author, "canardsTues")) + " canards sur #" + str(
                        message.channel) + ".     \_X<   *COUAC*   [10 xp]")
                    if database.getStat(message.channel, message.author, "meilleurTemps", default=servers[message.server.id]["settings"].get("tempsAttente", defaultSettings["tempsAttente"])) > int(now - canardencours["time"]):
                        database.setStat(message.channel, message.author, "meilleurTemps", int(now - canardencours["time"]))
                    if servers[message.server.id]["settings"].get("findObjects", defaultSettings["findObjects"]):
                        if random.randint(0, 100) < 25:
                            yield from client.send_message(message.channel, str(
                                message.author.mention) + " > En fouillant les buissons autour du canard, tu trouves " + random.choice(inutilite))




                else:
                    tmp = yield from client.send_message(message.channel, str(message.author.mention) + " > BANG")
                    yield from asyncio.sleep(1)
                    yield from client.edit_message(tmp, str(message.author.mention) + " > **PIEWW**\tTu à raté le canard ! [raté : -1 xp]")
                    database.addToStat(message.channel, message.author, "tirsManques", 1)
                    database.addToStat(message.channel, message.author, "exp", -1)
            else:
                yield from messageUser(message, " > Par chance tu as raté, mais tu visais qui au juste ? Il n'y a aucun canard dans le coin...   [raté : -1 xp] [tir sauvage : -1 xp]")
                database.addToStat(message.channel, message.author, "tirsSansCanards", 1)
                database.addToStat(message.channel, message.author, "exp", -2)
        else:
            yield from messageUser(message, "Par chance tu as raté, mais tu visais qui au juste ? Il n'y a aucun canard dans le coin...   [raté : -1 xp] [tir sauvage : -1 xp]")
            database.addToStat(message.channel, message.author, "tirsSansCanards", 1)
            database.addToStat(message.channel, message.author, "exp", -2)

    elif message.content.startswith("!reload"):
        logger.debug("> RELOAD (" + str(message.author) + ")")
        if database.getStat(message.channel, message.author, "enrayee", default=False):
            yield from messageUser(message, "Tu décoinces ton arme.")
            database.setStat(message.channel, message.author, "enrayee", False)
            if database.getStat(message.channel, message.author, "balles", default=database.getPlayerLevel(message.channel, message.author)["balles"]) > 0:
                yield from deleteMessage(message)
                return

        if database.getStat(message.channel, message.author, "balles", default=database.getPlayerLevel(message.channel, message.author)["balles"]) <= 0:
            if database.getStat(message.channel, message.author, "chargeurs",
                                default=database.getPlayerLevel(message.channel, message.author)["chargeurs"]) > 0:
                database.setStat(message.channel, message.author, "balles", database.getPlayerLevel(message.channel, message.author)["balles"])
                database.addToStat(message.channel, message.author, "chargeurs", -1)
                yield from messageUser(message, "Tu recharges ton arme. | Munitions dans l'arme : " + str(
                    database.getStat(message.channel, message.author, "balles",
                                     default=database.getPlayerLevel(message.channel, message.author)["balles"])) + "/" + str(
                    database.getPlayerLevel(message.channel, message.author)["balles"]) + " | Chargeurs restants : " + str(
                    database.getStat(message.channel, message.author, "chargeurs",
                                     default=database.getPlayerLevel(message.channel, message.author)["chargeurs"])) + "/" + str(
                    database.getPlayerLevel(message.channel, message.author)["chargeurs"]))
            else:
                yield from messageUser(message,"Tu es à court de munitions. | Munitions dans l'arme : " + str(
                                                   database.getStat(message.channel, message.author, "balles",
                                                                    default=database.getPlayerLevel(message.channel, message.author)[
                                                                        "balles"])) + "/" + str(
                                                   database.getPlayerLevel(message.channel, message.author)["balles"]) + " | Chargeurs restants : " + str(
                                                   database.getStat(message.channel, message.author, "chargeurs",
                                                                    default=database.getPlayerLevel(message.channel, message.author)[
                                                                        "chargeurs"])) + "/" + str(
                                                   database.getPlayerLevel(message.channel, message.author)["chargeurs"]))
        else:
            yield from messageUser(message,"Ton arme n'a pas besoin d'etre rechargée | Munitions dans l'arme : " + str(
                                               database.getStat(message.channel, message.author, "balles",
                                                                default=database.getPlayerLevel(message.channel, message.author)["balles"])) + "/" + str(
                                               database.getPlayerLevel(message.channel, message.author)["balles"]) + " | Chargeurs restants : " + str(
                                               database.getStat(message.channel, message.author, "chargeurs",
                                                                default=database.getPlayerLevel(message.channel, message.author)[
                                                                    "chargeurs"])) + "/" + str(
                                               database.getPlayerLevel(message.channel, message.author)["chargeurs"]))
        yield from deleteMessage(message)

    elif message.content.startswith("!shop"):
        logger.debug("> SHOP (" + str(message.author) + ")")
        args_ = message.content.split(" ")
        if len(args_) == 1:
            yield from messageUser(message, ":mortar_board: Tu dois préciser le numéro de l'item à acheter aprés cette commande. `!shop [N° item]`")
            yield from deleteMessage(message)
            return
        else:
            try:
                item = int(args_[1])
            except ValueError:
                yield from messageUser(message, str(
                    message.author.mention) + ":mortar_board: Tu dois préciser le numéro de l'item à acheter aprés cette commande. Le numéro donné n'est pas valide. `!shop [N° item]`")
                yield from deleteMessage(message)
                return

        if item == 1:
            if database.getStat(message.channel, message.author, "balles", default=database.getPlayerLevel(message.channel, message.author)["balles"]) < \
                    database.getPlayerLevel(message.channel, message.author)["balles"]:
                if database.getStat(message.channel, message.author, "exp") > 7:
                    yield from messageUser(message, ":money_with_wings: Tu ajoutes une balle dans ton arme pour 7 points d'experience")
                    database.addToStat(message.channel, message.author, "balles", 1)
                    database.addToStat(message.channel, message.author, "exp", -7)
                else:
                    yield from messageUser(message,":x: Tu n'as pas assez d'experience pour effectuer cet achat !")

            else:
                yield from messageUser(message, ":champagne: Ton chargeur est déjà plein !")

        elif item == 2:
            if database.getStat(message.channel, message.author, "chargeurs",
                                default=database.getPlayerLevel(message.channel, message.author)["chargeurs"]) < \
                    database.getPlayerLevel(message.channel, message.author)["chargeurs"]:
                if database.getStat(message.channel, message.author, "exp") > 13:
                    yield from messageUser(message, ":money_with_wings: Tu ajoutes un chargeur à ta réserve pour 13 points d'experience")
                    database.addToStat(message.channel, message.author, "chargeurs", 1)
                    database.addToStat(message.channel, message.author, "exp", -13)
                else:
                    yield from messageUser(message, ":x: Tu n'as pas assez d'experience pour effectuer cet achat !")

            else:
                yield from messageUser(message, ":champagne: Ta réserve de chargeurs est déjà pleine !")

        elif item == 17:
            if len(args_) <= 2:
                yield from messageUser(message, str(
                    message.author.mention) + "C'est pas exactement comme ca que l'on fait... Essaye de mettre le pseudo de la personne ? :p")
                yield from deleteMessage(message)
                return
            args_[2] = args_[2].replace("@", "").replace("<", "").replace(">", "")
            target = message.channel.server.get_member_named(args_[2])
            if target is None:
                target = message.channel.server.get_member(args_[2])
                if target is None:
                    yield from messageUser(message, "Je ne reconnais pas cette personne : " + args_[2])
                    yield from deleteMessage(message)
                    return

            if database.getStat(message.channel, message.author, "exp") > 14:
                if database.getStat(message.channel, target, "sabotee", "-") == "-":
                    yield from messageUser(message, ":ok: Tu sabote l'arme de " + target.name + "! Elle est maintenent enrayée... Mais il ne le sais pas !")
                    database.addToStat(message.channel, message.author, "exp", -14)
                    database.setStat(message.channel, target, "sabotee", message.author.name)
                else:
                    yield from messageUser(message, ":ok: L'arme de " + target.name + " est déjà sabotée!")

            else:
                yield from messageUser(message,":x: Tu n'as pas assez d'experience pour effectuer cet achat !")
        elif item == 20:
            if database.getStat(message.channel, message.author, "exp") > 8:
                yield from messageUser(message, ":money_with_wings: Un canard apparaitera dans les 10 prochaines minutes sur le channel, grâce à l'appeau de " + message.author.mention + ". Ca lui coûte 8 exp !")
                database.addToStat(message.channel, message.author, "exp", -8)
                dans = random.randint(0, 60 * 10)
                logger.debug("Appeau lancé pour dans " + str(dans) + "sec sur " + message.channel.name + " | " + message.channel.server.name)
                yield from asyncio.sleep(dans)
                yield from nouveauCanard({"time": int(time.time()), "channel": message.channel})

            else:
                yield from messageUser(message,":x: Tu n'as pas assez d'experience pour effectuer cet achat !")

        elif item == 22:
            if database.getStat(message.channel, message.author, "exp") > 5:

                servers = JSONloadFromDisk("channels.json", default="{}")
                yield from messageUser(message, ":money_with_wings: Vous serez averti lors du prochain canard sur #" + message.channel.name, forcePv=True)
                if message.channel.id in servers[message.server.id]["detecteur"]: servers[message.server.id]["detecteur"][message.channel.id].append(message.author.id)
                else: servers[message.server.id]["detecteur"][message.channel.id] = [message.author.id]
                JSONsaveToDisk(servers, "channels.json")
                database.addToStat(message.channel, message.author, "exp", -5)

            else:
                yield from messageUser(message,":x: Tu n'as pas assez d'experience pour effectuer cet achat ! !")


        elif item == 23:
            if database.getStat(message.channel, message.author, "exp") > 50:
                yield from messageUser(message, ":money_with_wings: Tu prépares un canard mécanique sur le chan pour 50 points d'experience. C'est méchant, mais tellement drôle !")
                database.addToStat(message.channel, message.author, "exp", -50)
                yield from asyncio.sleep(75)
                yield from client.send_message(message.channel, "-,_,.-'`'°-,_,.-'`'° %__%   *KZZZZZ*")
            else:
                yield from messageUser(message, ":x: Tu n'as pas assez d'experience pour effectuer cet achat !")

        else:
            yield from messageUser(message, ":x: Objet non trouvé :'(")

        yield from deleteMessage(message)

    elif message.content.startswith("-,,.-") or "QUAACK" in message.content or "/_^<" in message.content:
        yield from messageUser(message, " Tu as tendu un drapeau de canard et tu t'es fait tirer dessus. Too bad ! [-1 exp]")
        database.addToStat(message.channel, message.author, "exp", -1)

    elif message.content.startswith("!top"):
        logger.debug("> TOPSCORES (" + str(message.author) + ")")
        args_ = message.content.split(" ")
        if len(args_) == 1:
            nombre = 15
        else:
            try:
                nombre = int(args_[1])
                if nombre not in range(1, 50 + 1):
                    yield from messageUser(message, ":mortar_board: Le nombre maximum de joueurs pour le tableau des meilleurs scores est de 50")
                    yield from deleteMessage(message)
                    return

            except ValueError:
                yield from messageUser(message, ":mortar_board: Tu dois préciser le nombre de joueurs à afficher. Le numéro donné n'est pas valide. `!top [nombre joueurs]`")
                yield from deleteMessage(message)
                return
        x = PrettyTable()

        x._set_field_names(["Position", "Pseudo", "Experience", "Canards Tués"])
        i = 0
        for joueur in database.topScores(message.channel):
            i += 1
            if (joueur["canardsTues"] is None) or (joueur["canardsTues"] == 0) or ("canardTues" in joueur == False):
                joueur["canardsTues"] = "AUCUN !"
            if joueur["exp"] is None:
                joueur["exp"] = 0
            x.add_row([i, joueur["name"], joueur["exp"], joueur["canardsTues"]])

        yield from messageUser(message,
                                       ":cocktail: Meilleurs scores pour #" + message.channel.name + " : :cocktail:\n```" + x.get_string(end=nombre,
                                                                                                                                         sortby="Position") + "```" ,forcePv = True)

        yield from deleteMessage(message)

    elif message.content.startswith('!ping'):

        logger.debug("> PING (" + str(message.author) + ")")
        tmp = yield from client.send_message(message.channel, 'BOUM')
        yield from asyncio.sleep(4)
        yield from client.edit_message(tmp, '... Oups ! Pardon, pong !')
        yield from deleteMessage(message)

    elif message.content.startswith("!duckstat"):
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
                    yield from messageUser(message, "Je ne reconnais pas cette personne :x")
                    yield from deleteMessage(message)
                    return
        x = PrettyTable()

        x._set_field_names(["Statistique", "Valeur"])
        x.add_row(["Canards tués", database.getStat(message.channel, target, "canardsTues")])
        x.add_row(["Tirs manqués", database.getStat(message.channel, target, "tirsManques")])
        x.add_row(["Tirs sans canards", database.getStat(message.channel, target, "tirsSansCanards")])
        x.add_row(["Meilleur temps de tir", database.getStat(message.channel, target, "meilleurTemps", default=servers[message.server.id]["settings"].get("tempsAttente", defaultSettings["tempsAttente"]))])
        x.add_row(["Balles dans le chargeur actuel", str(
            database.getStat(message.channel, target, "balles", default=database.getPlayerLevel(message.channel, target)["balles"])) + " / " + str(
            database.getPlayerLevel(message.channel, target)["balles"])])
        x.add_row(["Chargeurs restants", str(
            database.getStat(message.channel, target, "chargeurs", default=database.getPlayerLevel(message.channel, target)["chargeurs"])) + " / " + str(
            database.getPlayerLevel(message.channel, target)["chargeurs"])])
        x.add_row(["Experience", database.getStat(message.channel, target, "exp")])
        x.add_row(["Niveau actuel",
                   str(database.getPlayerLevel(message.channel, target)["niveau"]) + " (" + database.getPlayerLevel(message.channel, target)["nom"] + ")"])
        x.add_row(["Précision des tirs", database.getPlayerLevel(message.channel, target)["precision"]])
        x.add_row(["Fiabilitée de l'arme", database.getPlayerLevel(message.channel, target)["fiabilitee"]])

        yield from messageUser(message, "Statistiques du chasseur : \n```" + x.get_string() + "```\nhttps://api-d.com/snaps/table_de_progression.html")

        yield from deleteMessage(message)

    elif message.content.startswith("!aide") or message.content.startswith("!help") or message.content.startswith("!info"):
        yield from messageUser(message, aideMsg, forcePv=True)
        yield from deleteMessage(message)

    elif message.content.startswith("!giveback"):
        logger.debug("> GIVEBACK (" + str(message.author) + ")")

        if int(message.author.id) in admins:
            yield from messageUser(message, "En cours...")
            database.giveBack(logger)
            yield from messageUser(message, ":ok: Terminé. Voir les logs sur la console ! ")
        else:
            yield from messageUser(message, ":x: Oupas (Permission Denied)")
        yield from deleteMessage(message)

    elif message.content.startswith("!coin"):
        logger.debug("> COIN (" + str(message.author) + ")")

        if message.author.id in servers[message.channel.server.id]["admins"] or int(message.author.id) in admins:
            yield from nouveauCanard({"channel": message.channel, "time": int(time.time())})
        else:
            yield from messageUser(message, ":x: Oupas (Permission Denied)")
        yield from deleteMessage(message)

    elif message.content.startswith("!devinfo"):
        logger.debug("> DEVINFO (" + str(message.author) + ")")
        yield from messageUser(message, ":robot: Channel object " + str(
            message.channel) + " ID : " + message.channel.id + " | NAME : " + message.channel.name)
        yield from messageUser(message, ":robot: Author  object " + str(message.author) + " ID : " + message.author.id + " | NAME : " + message.author.name)
        yield from deleteMessage(message)

    elif message.content.startswith("!nextduck"):
        logger.debug("> NEXTDUCK (" + str(message.author) + ")")

        if int(message.author.id) in admins:
            prochaincanard = yield from getprochaincanard()
            timetonext = int(prochaincanard["time"] - time.time())
            yield from client.send_message(message.author,
                                           "Prochain canard : " + str(prochaincanard["time"]) + "(dans " + str(timetonext) + " sec) sur #" +
                                           prochaincanard["channel"].name + " - " +
                                           prochaincanard["channel"].server.name)
        else:
            yield from messageUser(message, "Oupas (Permission Denied)")
        yield from deleteMessage(message)

    elif message.content.startswith('!delchannel'):
        logger.debug("> DELCHANNEL (" + str(message.author) + ")")
        if message.author.id in servers[message.channel.server.id]["admins"]:
            if message.channel.id in servers[message.channel.server.id]["channels"]:
                logger.debug("Supression de la channel " + str(message.channel.id) + " | " + str(message.channel.name) + " du fichier...")
                servers[str(message.channel.server.id)]["channels"].remove(message.channel.id)
                JSONsaveToDisk(servers, "channels.json")
                yield from messageUser(message, ":robot: Channel supprimée du jeu ! Les scores sont neanmoins conservés...")
                yield from planifie()

            else:
                yield from messageUser(message, ":x: Cette channel n'existe pas dans le jeu.")
        elif int(message.author.id) in admins:
            if message.channel.id in servers[message.channel.server.id]["channels"]:
                logger.debug("Supression de la channel " + str(message.channel.id) + " | " + str(message.channel.name) + " du fichier...")
                servers[str(message.channel.server.id)]["channels"].remove(message.channel.id)
                JSONsaveToDisk(servers, "channels.json")
                yield from messageUser(message, ":robot: Channel supprimée du jeu ! Les scores sont neanmoins conservés... :warning: Vous n'etes pas administrateur du serveur")
                yield from planifie()

            else:
                yield from messageUser(message, ":x: Cette channel n'existe pas dans le jeu. :warning: Vous n'etes pas administrateur du serveur")
        else:
            yield from messageUser(message, ":x: Vous n'etes pas l'administrateur du serveur.")

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
                    yield from messageUser(message, "Je ne reconnais pas cette personne :x")
                    yield from deleteMessage(message)
                    return

        if message.author.id in servers[message.channel.server.id]["admins"] or int(message.author.id) in admins:
            servers[message.channel.server.id]["admins"].append(target.id)
            logger.debug("Ajout de l'admin " + str(target.id) + " | " + str(target.name) + " au fichier pour le serveur " + str(
                message.channel.server.id) + " | " + str(message.channel.server.name))
            yield from messageUser(message, ":robot: " + target.name + " est maintenent un gestionnaire du serveur !")
        else:
            yield from messageUser(message, ":x: Oops, vous n'etes pas administrateur du serveur...")
        JSONsaveToDisk(servers, "channels.json")
        return

    elif message.content.startswith("!set"):
        logger.debug("> SET (" + str(message.author) + ")")
        args_ = message.content.split(" ")
        if len(args_) == 1 or len(args_) > 3:
            yield from messageUser(message, ":x: Oops, mauvaise syntaxe. !set [parametre] <valeur>")
            x = PrettyTable()

            x._set_field_names(["Parametre", "Valeur actuelle", "Valeur par défaut"])
            for param in defaultSettings.keys():
                x.add_row([param, servers[message.server.id]["settings"].get(param, defaultSettings[param]), defaultSettings[param]])

            yield from messageUser(message, "Liste des paramétres disponibles : \n```" + x.get_string(sortby="Parametre") + "```")
            yield from deleteMessage(message)
            return

        if not args_[1] in defaultSettings:
            yield from messageUser(message, ":x: Oops, le parametre n'as pas été reconnu. !set [parametre] <valeur>")
            yield from deleteMessage(message)
            return

        if message.author.id in servers[message.channel.server.id]["admins"] or int(message.author.id) in admins:
            if len(args_) == 2:
                servers[message.server.id]["settings"].pop(args_[1])
                yield from messageUser(message, ":ok: Valeur réinitialisée a la valeur par défaut !")
            else:
                if args_[2].lower() == "true":
                    logger.debug("Valeur passée > bool (True)")
                    args_[2] = True
                elif args_[2].lower() == "false":
                    logger.debug("Valeur passée > bool (False)")
                    args_[2] = False
                elif representsInt(args_[2]):
                    logger.debug("Valeur passée > int")
                    args_[2] = int(args_[2])
                servers[message.server.id]["settings"][args_[1]] = args_[2]
                yield from messageUser(message, ":ok: Valeur modifiée à " + str(args_[2]) + " ( type : " + str(type(args_[2])) + ")")
            JSONsaveToDisk(servers, "channels.json")
            if args_[1] == "canardsJours":
                yield from planifie()


        else:
            yield from messageUser(message, ":x: Oops, vous n'etes pas administrateur du serveur...")

        return

    elif message.content.startswith("!duckplanning"):
        logger.debug("> DUCKPLANNING (" + str(message.author) + ")")
        if message.author.id in servers[message.channel.server.id]["admins"] or int(message.author.id) in admins:
            message_ = ":hammer: TimeDelta en minutes pour les canards sur le chan\n```"
            for timestamp in planification[message.channel]:
                message_ += str(int((time.time() - timestamp)/60)) + "\n"
            message_ += "```"
            yield from client.send_message(message.author, message_)
            yield from deleteMessage(message)

        else:
            yield from messageUser(message, ":x: Oops, vous n'etes pas administrateur du serveur...")

    elif message.content.startswith("!dearm"):
        logger.debug("> DEARM (" + str(message.author) + ")")
        if message.author.id in servers[message.channel.server.id]["admins"] or int(message.author.id) in admins:
            args_ = message.content.split(" ")

            if len(args_) == 1:
                yield from messageUser(message, ":x: Joueur non spécifié")
                return
            else:
                args_[1] = args_[1].replace("@", "").replace("<", "").replace(">", "")
                target = message.channel.server.get_member_named(args_[1])
                if target is None:
                    target = message.channel.server.get_member(args_[1])
                    if target is None:
                        yield from messageUser(message, ":x: Je ne reconnais pas cette personne :x")
                        yield from deleteMessage(message)
                        return

            if not database.getStat(message.channel, target, "banni", default=False):
                if not target.id in servers[message.channel.server.id]["admins"] or int(target.id) in admins:
                    database.setStat(message.channel, target, "banni", True)
                    yield from messageUser(message, " > :ok: Ce joueur est maintenent banni du bot !")
                else:
                    yield from messageUser(message, " > :x: Il est admin ce mec, c'est mort !")
            else:
                yield from messageUser(message, " > :x: Il est déja banni, lui ^^")
        else:
            yield from messageUser(message, " > :x: Oops, vous n'etes pas administrateur du serveur...")

    elif message.content.startswith("!rearm"):
        logger.debug("> rearm (" + str(message.author) + ")")
        if message.author.id in servers[message.channel.server.id]["admins"] or int(message.author.id) in admins:
            args_ = message.content.split(" ")

            if len(args_) == 1:
                yield from messageUser(message, ":x: Joueur non spécifié")
                return
            else:
                args_[1] = args_[1].replace("@", "").replace("<", "").replace(">", "")
                target = message.channel.server.get_member_named(args_[1])
                if target is None:
                    target = message.channel.server.get_member(args_[1])
                    if target is None:
                        yield from messageUser(message, ":x: Je ne reconnais pas cette personne :x")
                        yield from deleteMessage(message)
                        return

            if database.getStat(message.channel, target, "banni", default=False):
                database.setStat(message.channel, target, "banni", False)
                yield from messageUser(message, ":ok: Ce joueur est maintenent dé-banni du bot !")
            else:
                yield from messageUser(message, ":x: Il est pas banni, lui ^^")
        else:
            yield from messageUser(message, ":x: Oops, vous n'etes pas administrateur du serveur...")


@client.async_event
def on_channel_delete(channel):
    logger.info("Channel supprimée... " + channel.id + " | " + channel.name)
    servers = JSONloadFromDisk("channels.json", default="{}")
    if channel.id in servers[channel.server.id]["channels"]:
        for canard in canards:
            if channel in canard["channel"]:
                logger.Debug("Canard supprimé : " + str(canard))
                canards.remove(canard)
        servers[channel.server.id]["channels"].remove(channel.id)
        JSONsaveToDisk(servers, "channels.json")


@client.async_event
def on_server_remove(server):
    logger.info("Serveur supprimé... " + server.id + " | " + server.name)
    servers = JSONloadFromDisk("channels.json", default="{}")
    if server.id in servers:
        for canard in canards:
            for channel in server.channels:
                if channel in canard["channel"]:
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
        client.send_message(new.author, ":x: Merci de communiquer avec moi dans les channels ou je suis actif.")
        return
    if not new.channel.server.id in servers:
        yield from newserver(new.channel.server)
        servers = JSONloadFromDisk("channels.json", default="{}")

    if new.channel.id not in servers[new.channel.server.id]["channels"]:
        return
    if new.content.startswith("-,,.-") or "QUAACK" in new.content or "/_^<" in new.content:
        yield from messageUser(new, " Tu as essayé de brain le bot sortant un drapeau de canard après coup! [-5 exp]")
        database.addToStat(new.channel, new.author, "exp", -5)

client.run(token)
