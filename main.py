# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5
"""
Discord-duckhunt -- main.py
MODULE DESC 
"""
# Constants #
import random

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

planification = {} #{"channel":[time objects]}

def planifie():
    global planification

    planification_ = {}

    for server in client.servers:
        logger.debug("Serveur " + str(server))
        for channel in server.channels:
            if channel.type == discord.ChannelType.text:

                logger.debug(" |- Check channel : " + channel.id)
                permissions = channel.permissions_for(server.me)
                if permissions.read_messages and permissions.send_messages:
                    logger.debug("   |-Ajout channel : " + channel.id)
                    templist = []
                    now = time.time()
                    thisDay = now - (now % 3600)
                    for id in range(1, canardsJours + 1):
                        templist.append(int(thisDay + random.randint(0,3600)))
                    planification_[str(channel)] = templist

    logger.debug("Nouvelle planification : " + str(planification_))

    logger.debug("Supression de l'ancienne planification, et application de la nouvelle")
    planification = planification_ #{"channel":[time objects]}



@client.async_event
def on_ready():
    logger.info("Connecté comme " + str(client.user.name) + " | " + str(client.user.id))
    logger.info("Creation de la planification")
    planifie()
    logger.info("Lancers de canards planifiés")
    logger.info("Initialisation terminée :) Ce jeu, ca va faire un carton !")



@client.async_event
def on_message(message):
    if message.author == client.user:
        return



    if message.content.startswith('!bang'):
        tmp = yield from client.send_message(message.channel, 'BOUM')

        time.sleep(1)
        yield from client.edit_message(tmp, 'BOUM !')
        time.sleep(2)
        yield from client.edit_message(tmp, 'BANG !')


    elif message.content.startswith('!ping'):
        tmp = yield from client.send_message(message.channel, 'BOUM')
        time.sleep(1)
        yield from client.edit_message(tmp, '... Oups ! Pardon, pong !')

client.run(token)
