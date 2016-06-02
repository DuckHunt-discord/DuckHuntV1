# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5
"""
Discord-duckhunt -- main.py
MODULE DESC 
"""
# Constants #
import random
import database
import time

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


@asyncio.coroutine
def planifie():
    global planification

    planification_ = {}

    logger.debug("Time now : " + str(time.time()))

    for server in client.servers:
        logger.debug("Serveur " + str(server))
        for channel in server.channels:
            if channel.type == discord.ChannelType.text:

                logger.debug(" |- Check channel : " + channel.id + " | " + channel.name)
                permissions = channel.permissions_for(server.me)
                if permissions.read_messages and permissions.send_messages:
                    if (channelWL and int(channel.id) in whitelist) or not channelWL:

                        logger.debug("   |-Ajout channel : " + channel.id)
                        templist = []
                        now = time.time()
                        thisDay = now - (now % 86400)
                        for id in range(1, canardsJours + 1):
                            templist.append(int(thisDay + random.randint(0, 86400)))
                        planification_[channel] = sorted(templist)

    logger.debug("Nouvelle planification : " + str(planification_))

    logger.debug("Supression de l'ancienne planification, et application de la nouvelle")

    planification = planification_  # {"channel":[time objects]}


def nouveauCanard(canard):
    logger.debug("Nouveau canard : " + str(canard))
    yield from client.send_message(canard["channel"], "-,_,.-'`'°-,_,.-'`'° /_^<   QUAACK")
    canards.append(canard)


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
        logger.debug("Plus de canards pour aujourd'hui ! Attente jusqu'a demain (" + str(
            thisDay + 86400 - time.time()) + " sec)")
        yield from asyncio.sleep(thisDay + 86400 - time.time())
        prochaincanard = yield from  getprochaincanard()
    else:

        logger.debug("Prochain canard : " + str(prochaincanard["time"]) + "(dans " + str(timetonext) + " sec) sur #" +
                     prochaincanard["channel"].name)

    return prochaincanard


@asyncio.coroutine
def mainloop():
    logger.debug("Entrée dans la boucle principale")
    exit_ = False
    prochaincanard = yield from getprochaincanard()
    while not exit_:
        now = time.time()

        if int(time.time()) % 60 == 0:
            timetonext = prochaincanard["time"] - time.time()
            logger.debug(
                "Prochain canard : " + str(prochaincanard["time"]) + "(dans " + str(timetonext) + " sec) sur #" +
                prochaincanard["channel"].name)
            logger.debug("Canards en cours : " + str(canards))

        if prochaincanard["time"] < time.time():  # CANARD !
            nouveauCanard(prochaincanard)
            prochaincanard = yield from getprochaincanard()

        for canard in canards:
            if int(canard["time"] + tempsAttente) < int(time.time()):  # Canard qui se barre
                logger.debug(
                    "Le canard de " + str(canard["time"]) + " est resté trop longtemps, il s'échappe. (il est " + str(
                        int(time.time())) + ", et il aurait du rester jusqu'a " + str(
                        int(canard["time"] + tempsAttente)) + " )")
                yield from client.send_message(canard["channel"], "Le canard s'échappe.     ·°'\`'°-.,¸¸.·°'\`")
                canards.remove(canard)
        yield from asyncio.sleep(2)


@client.async_event
def on_ready():
    logger.info("Connecté comme " + str(client.user.name) + " | " + str(client.user.id))
    logger.info("Creation de la planification")
    yield from planifie()
    logger.info("Lancers de canards planifiés")
    logger.info("Initialisation terminée :) Ce jeu, ca va faire un carton !")
    yield from mainloop()


@client.async_event
def on_message(message):
    if message.author == client.user:
        return

    if int(message.channel.id) not in whitelist:
        logger.debug("Message trouvé mais pas en WL : " + str(message.channel) + " | " + str(message.content))
        return

    if message.content.startswith('!bang'):
        logger.debug("> BANG (" + str(message.author) + ")")
        if canards:
            canardencours = None
            for canard in canards:
                if canard["channel"] == message.channel:
                    canardencours = canard
                    break

            if canardencours:

                if random.randint(1, 100) < 75:
                    canards.remove(canardencours)
                    tmp = yield from client.send_message(message.channel, 'BANG')
                    yield from asyncio.sleep(1)
                    database.addToStat(message.channel, message.author, "canardsTues", 1)
                    database.addToStat(message.channel, message.author, "exp", 10)
                    yield from client.edit_message(tmp,
                                                   str(message.author.mention) + " > **BOUM**\tTu l'as eu en " + str(
                                                       int(time.time() - canardencours[
                                                           "time"])) + " secondes, ce qui te fait un total de" + "X" + " canards sur #" + str(
                                                       message.channel) + ".     \_X<   *COUAC*   [10 xp]")



                else:
                    tmp = yield from client.send_message(message.channel, 'BANG')
                    yield from asyncio.sleep(1)
                    yield from client.edit_message(tmp,
                                                   str(message.author.mention) + " > **PIEWW**\tTu à raté le canard ! [raté : -1 xp]")
                    database.addToStat(message.channel, message.author, "tirsManques", 1)
                    database.addToStat(message.channel, message.author, "exp", -1)
            else:
                yield from client.send_message(message.channel, str(message.author.mention) + " > Par chance tu as raté, mais tu visais qui au juste ? Il n'y a aucun canard dans le coin...   [raté : -1 xp] [tir sauvage : -1 xp]")
                database.addToStat(message.channel, message.author, "tirsSansCanards", 1)
                database.addToStat(message.channel, message.author, "exp", -2)
        else:
            yield from client.send_message(message.channel, str(message.author.mention) + " > Par chance tu as raté, mais tu visais qui au juste ? Il n'y a aucun canard dans le coin...   [raté : -1 xp] [tir sauvage : -1 xp]")
            database.addToStat(message.channel, message.author, "tirsSansCanards", 1)
            database.addToStat(message.channel, message.author, "exp", -2)



    elif message.content.startswith('!ping'):
        logger.debug("> PING (" + str(message.author) + ")")
        tmp = yield from client.send_message(message.channel, 'BOUM')
        yield from asyncio.sleep(4)
        yield from client.edit_message(tmp, '... Oups ! Pardon, pong !')

    elif message.content.startswith("!coin"):
        logger.debug("> COIN (" + str(message.author) + ")")

        if message.author.id in admins:
            yield from nouveauCanard({"channel": message.channel, "time": int(time.time())})
        else:
            yield from client.send_message(message.channel, str(message.author.mention) + " > Oupas (Permission Denied)")

    elif message.content.startswith("!aide") or message.content.startswith("!help"):
        yield from client.send_message(message.channel, aideMsg)

    elif message.content.startswith("!info"):
        logger.debug("INFO (" + str(message.author) + ")")
        yield from client.send_message(message.channel, ":robot: Channel object " + str(
            message.channel) + " ID : " + message.channel.id + " | NAME : " + message.channel.name)
        yield from client.send_message(message.channel, ":robot: Author  object " + str(message.author) + " ID : " + message.author.id + " | NAME : " + message.author.name)

    elif message.content.startswith("-,,.-"):
        yield from client.send_message(message.channel, str(
            message.author.mention) + " > Tu as tendu un drapeau de canard et tu t'es fait tirer dessus. Too bad ! [-1 exp]")
        database.addToStat(message.channel, message.author, "exp", -1)



client.run(token)
