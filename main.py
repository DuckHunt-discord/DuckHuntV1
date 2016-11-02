# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5
"""
Discord-duckhunt -- main.py
Ce module permet l'interaction du robot avec les serveurs discord. Il gere ausssi le démarrage et les commandes.
"""
# Constants #

__author__ = "Arthur — paris-ci"

# Licence
#
#		Cette création est mise à disposition selon le Contrat
#		Attribution-NonCommercial-ShareAlike 3.0 Unported disponible en ligne
#		http://creativecommons.org/licenses/by-nc-sa/3.0/ ou par courrier postal à
#		Creative Commons, 171 Second Street, Suite 300, San Francisco, California
#		94105, USA.
#		Vous pouvez également consulter la version française ici :
#		http://creativecommons.org/licenses/by-nc-sa/3.0/deed.fr
#
#       Travail original par MenzAgitat : http://scripts.eggdrop.fr/details-Duck+Hunt-s228.html

print("Démarrage...")

import argparse

parser = argparse.ArgumentParser(description="DuckHunt, jeu pour tirer sur des canards, pour Discord")
parser.add_argument("-d", "--debug", help="Affiche les messages de débug", action="store_true")
parser.add_argument("--quietstartup", help="N'affiche pas les messages de débug au démarrage", action="store_true")

args = parser.parse_args()

import logging
from logging.handlers import RotatingFileHandler

## INIT ##
logger = logging.getLogger("duckhunt")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
file_handler = RotatingFileHandler('activity.log', 'a', 10000000, 10)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
steam_handler = logging.StreamHandler()
if args.debug and not args.quietstartup:
    steam_handler.setLevel(logging.DEBUG)
else:
    steam_handler.setLevel(logging.INFO)
logger.addHandler(steam_handler)
steam_handler.setFormatter(formatter)
logger.debug("Logger Initialisé")

logger.debug("Import sys")
import sys

logger.debug("Import requests")
import requests

logger.debug("Import discord")
import discord

logger.debug("Import asyncio")
import asyncio

logger.debug("Import random")
import random

logger.debug("Import time")
import time

logger.debug("Import psutil")
import psutil

logger.debug("Import os")
import os

logger.debug("Import datetime")
import datetime

logger.debug("Import getext")
import gettext

logger.debug("Import database.py")
from database import getPref, JSONsaveToDisk, JSONloadFromDisk
import database

logger.debug("Import PrettyTable")
from prettytable import PrettyTable

logger.debug("Import *config")
from config import *

logger.debug("Import raven.Client pour sentry")

from raven import Client as Sentry

sentry = Sentry('https://cc82bca5d88649fc91897d47a54d7828:9d0a9e0af53941839413e711d0f84500@app.getsentry.com/90073')

logger.debug("Récupération de starttime")
startTime = time.time()


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
logger.debug("Creation client")
client = discord.Client()
logger.debug("Génération variables de base")

planification = {}  # {"channel":[time objects]}
canards = []  # [{"channel" : channel, "time" : time.time()}]
CompteurMessages = 0


def allCanardsGo():
    for canard in canards:
        try:
            yield from client.send_message(canard["channel"], _(random.choice(canards_bye), language=getPref(canard["channel"].server, "lang")))
            logwithinfos(canard["channel"], None, "Départ forcé du canard " + str(canard))
        except:
            logwithinfos(canard["channel"], None, "Départ forcé du canard ECHOUE" + str(canard))
            pass


def paste(data, ext):
    HASTEBIN_SERVER = 'http://api-d.com:7777'
    r = requests.post(HASTEBIN_SERVER + '/documents', data=data.encode("UTF-8"))
    j = r.json()
    if r.status_code is requests.codes.ok:
        return '{}/{}.{}'.format(HASTEBIN_SERVER, j['key'], ext)
    else:
        raise ResourceWarning(j['message'], r)


@asyncio.coroutine
def tableCleanup():
    db = database.db
    keep_channels = []
    keep_servers = []
    dropped = 0
    popped = 0
    table_nbre = 0
    server_nbre = 0
    logger.debug("TableCleanup")
    servers = JSONloadFromDisk("channels.json", default="{}")
    for server in client.servers:
        keep_servers.append(server.id)
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
                            keep_channels.append(str(server.id) + "-" + str(channel.id))

    logger.debug("Liste des tables a conserver : " + str(keep_channels))
    logger.debug("Liste des serveurs a conserver : " + str(keep_servers))
    for table_name in db.tables:
        table_nbre += 1
        logger.debug("Check " + str(table_name))
        if table_name not in keep_channels and table_name not in keep_servers:
            logger.debug(" |- DROPPING " + table_name)
            dropped += 1
            db[table_name].drop()
        else:
            try:
                keep_channels.remove(table_name)
            except ValueError:  # La table est globale
                pass

    logger.debug("Tables not seen : " + str(keep_channels))
    servers_ = dict(servers)
    for server in servers:
        server_nbre += 1
        logger.debug("Check " + str(server))
        if server not in keep_servers:
            logger.debug(" |- POPPING " + server)
            servers_.pop(server)
            popped += 1
    JSONsaveToDisk(servers_, "channels.json")

    logger.debug("Tables  Cleanup Done " + str(dropped) + "/" + str(table_nbre) + " table(s) dropped")
    logger.debug("Servers Cleanup Done " + str(popped) + "/" + str(server_nbre) + " server(s) popped")


@asyncio.coroutine
def giveBackIfNeeded(channel, player):
    lastGB = int(database.getStat(channel, player, "lastGiveback", default=int(time.time())))
    if int(lastGB / 86400) != int(int(time.time()) / 86400):
        logwithinfos(channel, player,"GiveBack  > LastGB :" + str(lastGB) + " / 86400 = " + str(int(lastGB / 86400)))
        logwithinfos(channel, player,"GiveBack  > Now : " + str(int(time.time())) + " / 86400 = " + str(int(int(time.time()) / 86400)))
        logwithinfos(channel, player, "Giveback des armes et chargeurs")
        database.giveBack(logger, player=player, channel=channel)
        database.setStat(channel, player, "lastGiveback", int(time.time()))
    else:
        #logger.debug("Pas besoin de passer à l'armurerie")
        return

@asyncio.coroutine
def findUser(message, user):
    target = message.mentions[0]
    if target is None:
        user = user.replace("@", "").replace("<", "").replace(">", "").replace("!","")
        target = message.server.get_member_named(user)
        if target is None:
            target = message.server.get_member(user)
            if target is None:

                logwithinfos_message(message, "Personne non reconnue : " + str(user))
                return

@asyncio.coroutine
def messageUser(message, toSend, forcePv=False):
    if len(toSend) > 1950:
        logwithinfos_message(message, "Creation d'un paste...")
        toSend = paste(toSend.replace("```", ""), "py")
        #logger.info(_("Message trop long, envoi sur hastebin avec le lien : ") + toSend)
        logwithinfos_message(message, "Lien : " + toSend)
    if getPref(message.server, "pmMostMessages") or forcePv == True:
        try:
            yield from client.send_message(message.author, toSend)
        except discord.errors.Forbidden:
            try:
                yield from client.send_message(message.channel,
                                               str(message.author.mention) + "403 Permission denied (can't send private messages to this user)")
                logwithinfos_message(message, "Impossible d'envoyer des messages en privé à cet utilisateur")
            except:
                logwithinfos_message(message, "Impossible d'envoyer des messages dans le channel")
                pass
    else:
        try:
            yield from client.send_message(message.channel, str(message.author.mention) + " > " + toSend)
        except:
            logwithinfos_message(message, "Impossible d'envoyer des messages dans ce channel.")
            pass

def logwithinfos_message(message_obj, log_str):
    logwithinfos(message_obj.channel, message_obj.author, log_str)

def logwithinfos(channel, author, log_str):
    logger.debug(((channel.server.name.center(16, " ") if len(channel.server.name) < 16 else channel.server.name[:16]) if channel else "XX") + " :: " + ((("#" + channel.name).center(16, " ") if len(channel.name) < 16 else channel.name[:16]) if channel else "XX") + " :: " + ("<" + author.name + "> " if author else "") + log_str)

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

def fixserver(servers, server_obj):
    server = server_obj.id
    if not server in servers.keys():
        servers[server] = {}
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
        #logger.debug("Mise à jour de name dans le serveur {server}...".format(**{"server": server}))

    names = {"server": server_obj.name}
    ids = []
    for channel in server_obj.channels:
        names[channel.id] = channel.name
        ids += [channel.id]

    for channel in servers[server]["channels"]:
        if channel not in ids:
            servers[server]["channels"].remove(channel)
            logger.debug("Supression de " + str(channel) + " du channels.json")

    servers[server]["name"] = names
    return servers

@asyncio.coroutine
def updateJSON():
    logger.debug("Verification du fichier channels.json")
    servers = JSONloadFromDisk("channels.json", default="{}")
    #logger.debug("Version parsée de servers : " + str(servers))
    serversnonvus = list(client.servers)

    for server in list(servers.keys()):
        server_obj = client.get_server(server)
        if server_obj:
            serversnonvus.remove(server_obj)
            servers = fixserver(servers, server_obj)
        else:
            logger.warning("Le serveur " + server + " n'existe pas dans la liste des serveurs du bot...")
            servers.pop(server)
    for server in serversnonvus:
        logger.debug("Le serveur " + str(server.name) + " | " + str(server.id) + " n'existe pas dans la configuration du bot!")
        servers = fixserver(servers, server)

    JSONsaveToDisk(servers, "channels.json")


@asyncio.coroutine
def planifie(channel=None):
    global planification

    planification_ = {}

    logger.debug("Time now : " + str(time.time()))
    yield from asyncio.sleep(1)
    now = time.time()
    thisDay = now - (now % 86400)
    servers = JSONloadFromDisk("channels.json", default="{}")
    if not channel:
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
        #logger.debug("Nouvelle planification : {planification}".format(**{"planification": planification_}))
        logger.debug("Supression de l'ancienne planification, et application de la nouvelle")

        planification = planification_  # {"channel":[time objects]}

    else:
        if channel.type == discord.ChannelType.text:
            logger.debug(" |- Check channel : " + channel.id + " | " + channel.name)
            permissions = channel.permissions_for(channel.server.me)
            if permissions.read_messages and permissions.send_messages:
                # if (channelWL and int(channel.id) in whitelist) or not channelWL:
                if channel.id in servers[channel.server.id]["channels"]:
                    logger.debug("   |-Ajout channel : {id} ({canardsjours} c/j)".format(**{
                        "id": channel.id, "canardsjours": getPref(channel.server, "canardsJours")
                    }))
                    templist = []
                    for id_ in range(1, getPref(channel.server, "canardsJours") + 1):
                        templist.append(int(thisDay + random.randint(0, 86400)))
                    planification[channel] = sorted(templist)

        #logger.debug("Nouvelle planification : {planification}".format(**{"planification": planification}))


def nouveauCanard(canard:dict, canBeSC=True) :
    servers = JSONloadFromDisk("channels.json", default="{}")
    if servers[canard["channel"].server.id]["detecteur"].get(canard["channel"].id, False):
        for playerid in servers[canard["channel"].server.id]["detecteur"][canard["channel"].id]:
            player = discord.utils.get(canard["channel"].server.members, id=playerid)
            try:
                yield from client.send_message(player, _("Il y a un canard sur #{channel}",
                                                         getPref(canard["channel"].server, "lang")).format(
                    **{"channel": canard["channel"].name}))
                logwithinfos(canard["channel"], player, "Envoi d'une notification de canard")
            except:
                logwithinfos(canard["channel"], player, "Erreur lors de l'envoi d'une notification de canard")
                pass

        servers[canard["channel"].server.id]["detecteur"].pop(canard["channel"].id)
        JSONsaveToDisk(servers, "channels.json")

    if canBeSC and getPref(canard["channel"].server, "SCactif"):
        chance = random.randint(0, 100)
        if chance < getPref(canard["channel"].server, "SCchance"):
            vie = random.randint(getPref(canard["channel"].server, "SCviemin"), getPref(canard["channel"].server, "SCviemax"))
            canard["isSC"] = True
            canard["SCvie"] = vie
            canard["level"] = vie
        else:
            canard["isSC"] = False
    else:
        canard["isSC"] = True

    logwithinfos(canard["channel"], None, "Nouveau canard : " + str(canard))
    if getPref(canard["channel"].server, "randomCanard"):
        canard_str = random.choice(canards_trace) + "  " + random.choice(canards_portrait) + "  " + _(random.choice(canards_cri),
                                                                                                      language=getPref(canard["channel"].server, "lang"))
    else:
        canard_str = "-,,.-'`'°-,,.-'`'° /_^<   QUAACK"
    try:
        yield from client.send_message(canard["channel"], canard_str)
    except:
        pass
    canards.append(canard)


@asyncio.coroutine
def deleteMessage(message, force=False):
    if getPref(message.server, "deleteCommands") or force:
        if message.channel.permissions_for(message.server.me).manage_messages:
            logwithinfos_message(message, "Supression du message : {author} | {content}".format(**{"author": message.author.name, "content": message.content}))
            try:
                yield from client.delete_message(message)
            except:
                logwithinfos_message(message, "Supression du message échouée [permission allowed but forbidden >> Need 2FA ?] : {author} | {content}".format(
                    **{"author": message.author.name, "content": message.content}))

        else:
            logwithinfos_message(message, "Supression du message échouée [permission denied] : {author} | {content}".format(
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

        logwithinfos(prochaincanard["channel"], None, "Prochain canard : {time} (dans {timetonext} sec)".format(**{
            "timetonext": timetonext,
            "time"  : prochaincanard["time"]
        }))

    return prochaincanard


@asyncio.coroutine
def mainloop():
    logger.debug("Entrée dans la boucle principale")
    exit_ = False
    prochaincanard = yield from getprochaincanard()
    planday = int(int(time.time()) / 86400)
    while not exit_:
        now = time.time()

        if int((int(now)) / 86400) != planday:
            # database.giveBack(logger)
            planday = int(int(now) / 86400)
            logger.debug("Il est l'heure de replanifier")
            yield from planifie()
            prochaincanard = yield from getprochaincanard()

        if int(now) % 60 == 0 and prochaincanard["time"] != 0:
            timetonext = prochaincanard["time"] - now
            logwithinfos(prochaincanard["channel"], None, "Prochain canard : {time} (dans {timetonext} sec) ".format(**{
                "timetonext": timetonext,
                "time"  : prochaincanard["time"]
            }))
            logger.debug("Canards en cours : {canards}".format(**{"canards": len(canards)}))

        if prochaincanard["time"] < now and prochaincanard["time"] != 0:  # CANARD !
            yield from nouveauCanard(prochaincanard)
            prochaincanard = yield from getprochaincanard()

        if prochaincanard["time"] == 0:
            prochaincanard = yield from getprochaincanard()

        for canard in canards:
            if int(canard["time"]) + int(getPref(canard["channel"].server, "tempsAttente")) < int(now):  # Canard qui se barre
                logwithinfos(canard["channel"], None, "Le canard de {time} est resté trop longtemps, il s'échappe. (il est {now}, et il aurait du rester jusqu'a {shouldwaitto}).".format(**{
                        "time": canard["time"], "now": now, "shouldwaitto": str(
                            int(canard["time"] + getPref(canard["channel"].server, "tempsAttente")))
                    }))
                try:
                    yield from client.send_message(canard["channel"], _(random.choice(canards_bye), language=getPref(canard["channel"].server, "lang")))
                except:
                    pass
                canards.remove(canard)
        yield from asyncio.sleep(1)


@client.async_event
def on_ready():
    try:
        logger.info("Connecté comme {name} | {id}".format(**{"name": client.user.name, "id": client.user.id}))
        yield from updateJSON()
        yield from tableCleanup()
        logger.info("Creation de la planification")
        yield from planifie()
        logger.info("Lancers de canards planifiés")
        logger.debug("Changement du jeu discord")
        yield from client.change_presence(game=discord.Game(name="Killing ducks | !help"))

        if args.debug:
            steam_handler.setLevel(logging.DEBUG)
        logger.info("Initialisation terminée :) Ce jeu, ca va faire un carton !")
        yield from mainloop()
    except Exception as e:
        logger.critical("Exception dans On_Ready... Redémarrage")
        logger.exception("Exception : ")
        try:
            allCanardsGo()
        except:
            pass
        # sentry.captureException()
        client.loop.run_until_complete(client.logout())
        client.loop.close()
        sys.exit(1)


def objectTD(channel, target, language, object):
    date_expiration = datetime.datetime.fromtimestamp(database.getStat(channel, target, object, default=0))
    td = date_expiration - datetime.datetime.now()
    return _("{date} (dans {dans_jours}{dans_heures} et {dans_minutes})", language).format(**{
        "date"        : date_expiration.strftime(_('%H:%M:%S le %d/%m', language)),
        "dans_jours"  : _("{dans} jours ").format(**{"dans": td.days}) if td.days else "",
        "dans_heures" : _("{dans} heures").format(**{"dans": td.seconds // 3600}),
        "dans_minutes": _("{dans} minutes").format(**{"dans": (td.seconds // 60) % 60})
    })


@client.async_event
def on_message(message):
    global CompteurMessages
    if message.author == client.user:
        return

    CompteurMessages += 1
    if message.author.bot:
        return

    servers = JSONloadFromDisk("channels.json", default="{}")
    if message.channel.is_private:
        try:
            client.send_message(message.author,
                                _(":x: Merci de communiquer avec moi dans les channels ou je suis actif."))  # No server so no translation here :x
        except:
            pass
        return
    if not message.channel.server.id in servers:
        yield from newserver(message.channel.server)
        servers = JSONloadFromDisk("channels.json", default="{}")

    # Messages pour n'importe où
    language = getPref(message.server, "lang")
    prefix = getPref(message.server, "prefix")

    if message.content.startswith(prefix + "claimserver"):
        logwithinfos_message(message, "CLAIMSERVER")
        if not servers[message.channel.server.id]["admins"]:
            servers[message.channel.server.id]["admins"] = [message.author.id]
            logwithinfos_message(message, "Ajout de l'admin {admin_name} | {admin_id} au fichier de configuration pour le serveur {server_name} | {server_id}.".format(**{
                "admin_name": message.author.name, "admin_id": message.author.id, "server_name": message.channel.server.name,
                "server_id" : message.channel.server.id
            }))
            yield from messageUser(message, _(":robot: Vous etes maintenant le gestionnaire du serveur !", language))
        else:
            logwithinfos_message(message, "il y a déjà un admin")
            yield from messageUser(message, _(":x: Il y a déjà un admin sur ce serveur...", language))
        JSONsaveToDisk(servers, "channels.json")
        return

    elif message.content.startswith(prefix + "addchannel"):
        logwithinfos_message(message, "ADDCHANNEL")
        if message.author.id in servers[message.channel.server.id]["admins"]:
            if not message.channel.id in servers[message.channel.server.id]["channels"]:
                logwithinfos_message(message, "Ajout de la channel {name} | {id} au fichier...".format(**{"id": message.channel.id, "name": message.channel.name}))
                servers[str(message.channel.server.id)]["channels"].append(message.channel.id)
                JSONsaveToDisk(servers, "channels.json")
                yield from updateJSON()
                yield from messageUser(message, _(":robot: Channel ajoutée au jeu !", language))
                yield from planifie(channel=message.channel)

            else:
                logwithinfos_message(message, "Channel déja existante")
                yield from messageUser(message, _(":x: Cette channel existe déjà dans le jeu.", language))
        elif int(message.author.id) in admins:
            if not message.channel.id in servers[message.channel.server.id]["channels"]:
                logwithinfos_message(message, "(GA) Ajout de la channel {name} | {id} au fichier...".format(**{"id": message.channel.id, "name": message.channel.name}))
                servers[str(message.channel.server.id)]["channels"].append(message.channel.id)
                JSONsaveToDisk(servers, "channels.json")
                yield from updateJSON()
                yield from messageUser(message, _(":robot: Channel ajoutée au jeu ! :warning: Vous n'etes pas administrateur du serveur.", language))
                yield from planifie(channel=message.channel)

            else:
                logwithinfos_message(message, "(GA) channel déjà existante")
                yield from messageUser(message,
                                       _(":x: Cette channel existe déjà dans le jeu. :warning: Vous n'etes pas administrateur du serveur.", language))
        else:
            yield from messageUser(message, _(":x: Vous n'etes pas l'administrateur du serveur.", language))
            logwithinfos_message(message, "Non autorisé à ajouter une channel")

        return
    elif message.content.startswith(prefix + "broadcast"):
        logwithinfos_message(message, "BROADCAST")
        bc = message.content.replace("!broadcast", "", 1)
        if int(message.author.id) in admins:
            yield from messageUser(message, _("Démarrage du broadcast...", language))
            logwithinfos_message(message, "Brodcast démarré")
            for channel in planification.keys():
                try:
                    yield from client.send_message(channel, bc)
                except:
                    pass
            logwithinfos_message(message, "Broadcast terminé")
            yield from messageUser(message, _("Broadcast terminé :)", language))


        else:
            yield from messageUser(message, _("Oupas (Permission Denied)", language))
            logwithinfos_message(message, "Cet utilisateur ne peut pas utiliser le broadcast")

    elif message.content.startswith(prefix + "addadmin"):
        logwithinfos_message(message, "ADDADMIN")

        args_ = message.content.split(" ")
        if len(args_) == 1:
            target = message.author
        else:
            target = yield from findUser(message, args_[1])
            if target is None:
                yield from messageUser(message, _("Je ne reconnais pas cette personne :x", language))

        logwithinfos_message(message, "La personne visée est : " + target.name + " | " + target.id)
        if message.author.id in servers[message.channel.server.id]["admins"] or int(message.author.id) in admins:
            if not target.id in servers[message.channel.server.id]["admins"]:
                servers[message.channel.server.id]["admins"].append(target.id)
                logwithinfos_message(message, "Ajout de l'admin {admin_name} | {admin_id} dans le serveur {server_name} | {server_id}".format(
                    **{
                        "admin_id"   : target.id, "admin_name": target.name, "server_id": message.channel.server.id,
                        "server_name": message.channel.server.name
                    }))
                yield from messageUser(message,
                                       _(":robot: Ajout de l'admin {admin_name} | {admin_id} sur le serveur : {server_name} | {server_id}",
                                         language).format(
                                           **{
                                               "admin_id"   : target.id, "admin_name": target.name, "server_id": message.channel.server.id,
                                               "server_name": message.channel.server.name
                                           }))
            else:
                yield from messageUser(message, _(":x: Oops, cette personne est déjà administrateur du serveur...", language))
                logwithinfos_message(message, "Personne déjà admin")
        else:
            yield from messageUser(message, _(":x: Oops, vous n'etes pas administrateur du serveur...", language))
            logwithinfos_message(message, "Non autorisé à ajouter un admin")
        JSONsaveToDisk(servers, "channels.json")
        return

    if message.channel.id not in servers[message.channel.server.id]["channels"]:
        return

    if database.getStat(message.channel, message.author, "banni", default=False):
        logwithinfos_message(message, "Message ignoré car personne bannie")
        return
    # Messages en whitelist sur les channels activées

    if message.content.startswith(prefix + "bang"):

        yield from deleteMessage(message)
        logwithinfos_message(message, "BANG")
        now = time.time()
        yield from giveBackIfNeeded(message.channel, message.author)
        if database.getStat(message.channel, message.author, "mouille", default=0) > int(time.time()):
            yield from messageUser(message, _(
                "Tu es trempé ! Tu ne peux pas aller chasser ! Il faut attendre encore {temps_restant} minutes pour que tes vétement séchent !",
                language).format(
                **{"temps_restant": int((database.getStat(message.channel, message.author, "mouille", default=0) - int(time.time())) / 60)}))
            logwithinfos_message(message, "[bang] Fail : personne mouillée ")
            return
        if database.getStat(message.channel, message.author, "confisque", default=False):
            yield from messageUser(message, _("Vous n'etes pas armé", language))
            logwithinfos_message(message, "[bang] Fail : non armé (arme confisquée)")
            return

        if database.getStat(message.channel, message.author, "enrayee", default=False):
            yield from messageUser(message, _("Votre arme est enrayée, il faut la recharger pour la décoincer.", language))
            logwithinfos_message(message, "[bang] Fail : arme (déjà) entayée")
            return
        if database.getStat(message.channel, message.author, "sabotee", default="-") is not "-":
            logwithinfos_message(message, "[bang] Fail : arme sabotée par " + database.getStat(message.channel, message.author, "sabotee", default="-"))
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
            logwithinfos_message(message, "[bang] Fail : chargeur vide")
            return
        else:
            if random.randint(1, 100) < database.getPlayerLevel(message.channel, message.author)["fiabilitee"]:
                database.addToStat(message.channel, message.author, "balles", -1)
            else:
                if not (database.getStat(message.channel, message.author, "graisse", default=0) > int(time.time()) and random.randint(1, 100) < 50):

                    yield from messageUser(message, _("Ton arme s'est enrayée, recharge la pour la décoincer.", language))
                    logwithinfos_message(message, "[bang] Fail : arme enrayée")
                    database.setStat(message.channel, message.author, "enrayee", True)
                    return
                else:
                    database.addToStat(message.channel, message.author, "balles", -1)

        if canards:
            canardencours = None
            for canard in canards:
                if canard["channel"] == message.channel:
                    canardencours = canard
                    break

            if canardencours:
                if getPref(message.server, "duckLeaves"):
                    if random.randint(1, 100) < getPref(message.server, "duckChanceLeave") and database.getStat(message.channel, message.author,
                                                                                                                "silencieux", default=0) < int(
                            time.time()):
                        try:
                            tmp = yield from client.send_message(message.channel, str(message.author.mention) + _(" > BANG", language))
                        except:
                            pass
                        try:
                            canards.remove(canardencours)
                        except ValueError:
                            yield from client.edit_message(tmp, str(message.author.mention) + _(
                                " > La balle n'est pas partie de l'arme, peut-etre est elle defectueuse ? :x", language))
                            database.addToStat(message.channel, message.author, "balles", 1)
                            logwithinfos_message(message, "[bang] Fail : balle défectueuse")
                            return

                        yield from asyncio.sleep(getPref(message.server, "lagOnBang"))
                        yield from client.edit_message(tmp, str(message.author.mention) + _(
                            " > **FLAPP**\tEffrayé par tout ce bruit, le canard s'échappe ! AH BAH BRAVO ! [raté : -1 xp]", language))
                        logwithinfos_message(message, "[bang] Fail : le canard s'échappe")
                        database.addToStat(message.channel, message.author, "exp", -1)
                        return
                if random.randint(1, 100) < database.getPlayerLevel(message.channel, message.author)["precision"]:
                    try:
                        tmp = yield from client.send_message(message.channel, str(message.author.mention) + _(" > BANG", language))
                    except:
                        pass
                    if canardencours["isSC"]:
                        if database.getStat(message.channel, message.author, "munExplo", default=0) > int(time.time()):
                            logwithinfos_message(message, "[bang] canard vie -3")
                            canardencours["SCvie"] -= 3
                            vieenmoins = 3
                        elif database.getStat(message.channel, message.author, "munAp_", default=0) > int(time.time()):
                            logwithinfos_message(message, "[bang] canard vie -2")
                            canardencours["SCvie"] -= 2
                            vieenmoins = 2
                        else:
                            logwithinfos_message(message, "[bang] canard vie -1")
                            canardencours["SCvie"] -= 1
                            vieenmoins = 1

                        if canardencours["SCvie"] <= 0:
                            try:
                                canards.remove(canardencours)
                            except ValueError:
                                yield from client.edit_message(tmp, str(message.author.mention) + _(
                                    " > La balle n'est pas partie de l'arme, peut-etre est elle defectueuse ? :x", language))
                                database.addToStat(message.channel, message.author, "balles", 1)# Canare déjà tué de toute facon :x
                                logwithinfos_message(message, "[bang] Fail : balle défectueuse")
                                return

                            gain = int(getPref(message.server, "expParCanard") * (getPref(message.server, "SClevelmultiplier") * canardencours["level"]))
                            if database.getStat(message.channel, message.author, "trefle", default=0) > time.time():
                                gain += database.getStat(message.channel, message.author, "trefle_exp", default=0)

                            database.addToStat(message.channel, message.author, "canardsTues", 1)
                            database.addToStat(message.channel, message.author, "superCanardsTues", 1)
                            database.addToStat(message.channel, message.author, "exp", gain)
                            yield from asyncio.sleep(getPref(message.server, "lagOnBang"))
                            yield from client.edit_message(tmp, str(message.author.mention) + _(
                                " > :skull_crossbones: **BOUM**\tTu l'as eu en {time} secondes, ce qui te fait un total de {total} canards (dont {supercanards} supercanards) sur #{channel}.     \_X<   *COUAC*   [{exp} xp]",
                                language).format(**{
                                "time"        : int(now - canardencours["time"]),
                                "total"       : database.getStat(message.channel, message.author, "canardsTues"),
                                "channel"     : message.channel, "exp": int(
                                    getPref(message.server, "expParCanard") * (getPref(message.server, "SClevelmultiplier") * canardencours["level"])),
                                "supercanards": database.getStat(message.channel, message.author, "superCanardsTues")
                            }))
                            logwithinfos_message(message, "[bang] OK : canard tué")
                            if database.getStat(message.channel, message.author, "meilleurTemps",
                                                default=getPref(message.server, "tempsAttente")) > int(
                                        now - canardencours["time"]):
                                database.setStat(message.channel, message.author, "meilleurTemps", int(now - canardencours["time"]))
                            if getPref(message.server, "findObjects"):
                                if random.randint(0, 100) < 25:
                                    logwithinfos_message(message, "[bang] Inutilitée trouvée")
                                    yield from messageUser(message,
                                                           _("En fouillant les buissons autour du canard, tu trouves {inutilitee}", language).format(
                                                               **{"inutilitee": _(random.choice(inutilite), language)}))

                        else:
                            yield from asyncio.sleep(getPref(message.server, "lagOnBang"))
                            yield from client.edit_message(tmp, str(message.author.mention) + _(
                                " > :gun:  Le canard a survécu ! Essaie encore.  /_O<  [vie -{vie}]  *Super canard détécté*", language).format(
                                **{"vie": vieenmoins}))
                            logwithinfos_message(message, "[bang] OK : canard survécu")


                    else:
                        try:
                            canards.remove(canardencours)
                        except ValueError:
                            yield from client.edit_message(tmp, str(message.author.mention) + _(
                                " > La balle n'est pas partie de l'arme, peut-etre est elle defectueuse ? :x", language))
                            database.addToStat(message.channel, message.author, "balles", 1)
                            logwithinfos_message(message, "[bang] Fail : balle défectueuse")
                            return

                        gain = int(getPref(message.server, "expParCanard"))
                        if database.getStat(message.channel, message.author, "trefle", default=0) > time.time():
                            gain += database.getStat(message.channel, message.author, "trefle_exp", default=0)

                        database.addToStat(message.channel, message.author, "canardsTues", 1)
                        database.addToStat(message.channel, message.author, "exp", gain)

                        yield from asyncio.sleep(getPref(message.server, "lagOnBang"))
                        yield from client.edit_message(tmp, str(message.author.mention) + _(
                            " > :skull_crossbones: **BOUM**\tTu l'as eu en {time} secondes, ce qui te fait un total de {total} canards sur #{channel}.     \_X<   *COUAC*   [{exp} xp]",
                            language).format(**{
                            "time"   : int(now - canardencours["time"]), "total": database.getStat(message.channel, message.author, "canardsTues"),
                            "channel": message.channel, "exp": gain
                        }))
                        logwithinfos_message(message, "[bang] OK : canard tué")
                        if database.getStat(message.channel, message.author, "meilleurTemps",
                                            default=getPref(message.server, "tempsAttente")) > int(
                                    now - canardencours["time"]):
                            database.setStat(message.channel, message.author, "meilleurTemps", int(now - canardencours["time"]))
                        if getPref(message.server, "findObjects"):
                            if random.randint(0, 100) < 25:
                                logwithinfos_message(message, "[bang] Inutilitée trouvée")
                                yield from messageUser(message, _("En fouillant les buissons autour du canard, tu trouves {inutilitee}", language).format(
                                    **{"inutilitee": _(random.choice(inutilite), language)}))

                else:
                    try:
                        tmp = yield from client.send_message(message.channel, str(message.author.mention) + _(" > BANG", language))
                    except:
                        pass
                    yield from asyncio.sleep(getPref(message.server, "lagOnBang"))
                    if random.randint(0, 100) < 5:
                        victime = random.choice(list(message.server.members))
                        if not victime == message.author:
                            logwithinfos_message(message, "[bang] Fail : raté, accident de chasse")
                            yield from client.edit_message(tmp, str(message.author.mention) + _(
                                " > **BANG**\tTu as raté le canard... Et tu as tiré sur {player}. ! [raté : -1 xp] [accident de chasse : -2 xp] [arme confisquée]",
                                language).format(**{"player": victime.mention}))
                        else:
                            logwithinfos_message(message, "[bang] Fail : raté, accident de chasse, mort")
                            yield from client.edit_message(tmp, str(message.author.mention) + _(
                                " > **BANG**\tTu as raté le canard... Et tu t'es tiré dessus. Apprends à tenir ton fusil à l'endroit la prochaine fois, boulet ! [raté : -1 xp] [accident de chasse : -2 xp] [arme confisquée]",
                                language))
                        if database.getStat(message.channel, victime, "AssuranceVie", default=0) > int(time.time()):
                            exp = int(database.getPlayerLevel(message.channel, message.author)["niveau"] / 2)
                            logwithinfos_message(message, "[bang] Assurance vie de " + victime.name + " ajout de " + str(exp) + "exp.")
                            database.addToStat(message.channel, victime, "exp", exp)
                            yield from client.send_message(message.channel, str(victime.mention) + _(" > Tu gagnes {exp} avec ton assurance vie".format(**{"exp": exp})))

                        database.addToStat(message.channel, message.author, "tirsManques", 1)
                        database.addToStat(message.channel, message.author, "chasseursTues", 1)
                        database.addToStat(message.channel, message.author, "exp", -3)
                        database.setStat(message.channel, message.author, "confisque", True)
                        return
                    logwithinfos_message(message, "[bang] Fail : raté")
                    yield from client.edit_message(tmp, str(message.author.mention) + _(" > **PIEWW**\tTu as raté le canard ! [raté : -1 xp]", language))
                    database.addToStat(message.channel, message.author, "tirsManques", 1)
                    database.addToStat(message.channel, message.author, "exp", -1)
            else:
                if database.getStat(message.channel, message.author, "detecteurInfra", default=0) > int(time.time()):
                    logwithinfos_message(message, "[bang] Fail : pas de canard, détecteur infrarouge")
                    yield from messageUser(message, _(
                        "Il n'y a aucun canard dans le coin... Mais grace à ton detecteur infrarouge, la balle n'est pas partie :D",
                        language))
                    database.addToStat(message.channel, message.author, "balles", 1)
                    return
                logwithinfos_message(message, "[bang] Fail : pas de canard")
                yield from messageUser(message, _(
                    "Par chance tu as raté, mais tu visais qui au juste ? Il n'y a aucun canard dans le coin...   [raté : -1 xp] [tir sauvage : -1 xp]",
                    language))
                database.addToStat(message.channel, message.author, "tirsSansCanards", 1)
                database.addToStat(message.channel, message.author, "exp", -2)
        else:
            if database.getStat(message.channel, message.author, "detecteurInfra", default=0) > int(time.time()):
                logwithinfos_message(message, "[bang] Fail : pas de canard, détecteur infrarouge")
                yield from messageUser(message, _(
                    "Il n'y a aucun canard dans le coin... Mais grace à ton detecteur infrarouge, la balle n'est pas partie :D",
                    language))
                database.addToStat(message.channel, message.author, "balles", 1)

                return
            logwithinfos_message(message, "[bang] Fail : pas de canard")
            yield from messageUser(message, _(
                "Par chance tu as raté, mais tu visais qui au juste ? Il n'y a aucun canard dans le coin...   [raté : -1 xp] [tir sauvage : -1 xp]",
                language))
            database.addToStat(message.channel, message.author, "tirsSansCanards", 1)
            database.addToStat(message.channel, message.author, "exp", -2)

    elif message.content.startswith(prefix + "reload"):
        yield from deleteMessage(message)
        logwithinfos_message(message, "RELOAD")
        yield from giveBackIfNeeded(message.channel, message.author)
        if database.getStat(message.channel, message.author, "confisque", default=False):
            logwithinfos_message(message, "[reload] Fail : arme confisquée")
            yield from messageUser(message, _("Vous n'etes pas armé", language))
            return
        if database.getStat(message.channel, message.author, "enrayee", default=False):
            logwithinfos_message(message, "[reload] Arme décoincée")
            yield from messageUser(message, _("Tu décoinces ton arme.", language))
            database.setStat(message.channel, message.author, "enrayee", False)
            if database.getStat(message.channel, message.author, "balles", default=database.getPlayerLevel(message.channel, message.author)["balles"]) > 0:
                return

        if database.getStat(message.channel, message.author, "balles", default=database.getPlayerLevel(message.channel, message.author)["balles"]) <= 0:
            if database.getStat(message.channel, message.author, "chargeurs",
                                default=database.getPlayerLevel(message.channel, message.author)["chargeurs"]) > 0:
                database.setStat(message.channel, message.author, "balles", database.getPlayerLevel(message.channel, message.author)["balles"])
                database.addToStat(message.channel, message.author, "chargeurs", -1)
                logwithinfos_message(message, "[reload] arme rechargée")
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
                logwithinfos_message(message, "[reload] Fail : plus de munitions")
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
            logwithinfos_message(message, "[reload] Fail : l'arme n'a pas besoin d'etre rechargée")
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

    elif message.content.startswith(prefix + "shop"):
        logwithinfos_message(message, "SHOP")
        yield from giveBackIfNeeded(message.channel, message.author)

        args_ = message.content.split(" ")
        x = PrettyTable()

        x._set_field_names([_("Numéro", language), _("Fonctionnement", language), _("Coût", language)])
        x.add_row(["1", _("Ajoute une balle à votre arme", language), "7"])
        x.add_row(["2", _("Ajoute un chargeur à votre réserve", language), "13"])
        x.add_row(["3", _("Munitions AP qui doublent vos dégâts pour 1 journée", language), "15"])
        x.add_row(["4", _("Munitions Explosives qui triplent vos dégâts pour 1 journée", language), "25"])
        x.add_row(["5", _("Vous permet de récupérer une arme confisquée.", language), "40"])
        x.add_row(["6", _("Réduit de 50 pourcents le risque d'enrayement de l'arme pendant 24h et protège (une seule fois) contre une poignée de sable.",
                          language), "8"])
        # x.add_row(["7", _("Améliore la précision du prochain tir de (100 - précision actuelle) / 3", language), "6"])
        x.add_row(["8", _(
            "Bloque la gâchette de l'arme quand il n'y a pas de canard dans les environs dans le but d'éviter le gaspillage de munitions pendant 24h",
            language), "15"])
        x.add_row(["9", _("Réduit considérablement le bruit des tirs pendant 24h afin de ne pas effrayer les canards", language), "5"])
        x.add_row(["10", _(
            "Vous fait gagner un bonus aléatoire d'xp sur tous les canards que vous tuez pendant 24h. Ce bonus est déterminé lors de l'achat et peut valoir de 1 à 10.",
            language), "13"])
        # x.add_row(["11", _("Protège contre l'effet éblouissant du miroir pendant 24h", language), "5"])
        x.add_row(["12", _("Annule l'effet du seau d'eau.", language), "7"])
        # x.add_row(["13", _("Annule l'effet de la poignée de sable et du sabotage.", language), "7"])
        # x.add_row(["14", _("Éblouit un chasseur de votre choix pour lui faire perdre 50% de précision lors de son prochain tir.", language), "7"])
        # x.add_row(["15", _("Poignée de sable Jetez du sable sur l'arme d'un chasseur de votre choix pour lui faire perdre 50% de fiabilité lors de son prochain tir. Supprime l'effet de la graisse.", language), "7"])
        x.add_row(["16", _(
            "Videz un seau d'eau sur un chasseur de votre choix, l'obligeant ainsi à attendre pendant 1h que ses vêtements sèchent avant de pouvoir retourner chasser",
            language), "10"])
        x.add_row(
            ["17", _("Sabotez l'arme d'un chasseur de votre choix. Celle-ci s'enrayera et lui explosera à la figure lors de son prochain tir.", language),
             "14"])
        x.add_row(["18", _(
            "Assurance à usage unique permettant de gagner un bonus d'xp équivalent à 2x le niveau du tireur si vous êtes victime d'un accident de chasse pendant 1 semaine.",
            language), "10"])
        # x.add_row(["19", _("Divise par 3 la pénalité d'xp encourue en cas d'accident de chasse pendant 2 jours.", language), "5"])
        x.add_row(["20", _("Attire un canard dans les 10 prochaines minutes.", language), "8"])
        # x.add_row(["21", _("Jetez des morceaux de pain pour augmenter la probabilité qu'un canard apparaisse pendant 1h. Le pain augmente aussi de 20s le temps pendant lequel les canards restent avant de partir. Plusieurs morceaux de pain peuvent être achetés pour en cumuler l'effet. ", language), "2"])
        x.add_row(["22", _("Appareil à usage unique permettant d'être averti quand le prochain canard s'envolera", language), "5"])
        x.add_row(["23", _(
            "Faites une bonne blague aux autres chasseurs en lançant un faux canard ne rapportant pas d'xp. Il sera lancé automatiquement 75 secondes après l'achat.",
            language), "50"])

        shopitems = x.get_string()
        if len(args_) == 1:
            yield from deleteMessage(message)
            yield from messageUser(message,
                                   _(":mortar_board: Tu dois préciser le numéro de l'item à acheter aprés cette commande. `!shop [N° item]`", language))
            yield from messageUser(message, shopitems)
            logwithinfos_message(message, "[shop] Fail : pas d'argument")
            return

        else:
            try:
                item = int(args_[1])
            except ValueError:
                yield from deleteMessage(message)

                yield from messageUser(message, _(
                    ":mortar_board: Tu dois préciser le numéro de l'item à acheter aprés cette commande. Le numéro donné n'est pas valide. `!shop [N° item]`",
                    language))
                yield from messageUser(message, shopitems)
                logwithinfos_message(message, "[shop] Fail : argument non int")
                return
        if item == 17 or item == 23:
            yield from deleteMessage(message, force=True)
        else:
            yield from deleteMessage(message)

        if item == 1:
            if database.getStat(message.channel, message.author, "balles", default=database.getPlayerLevel(message.channel, message.author)["balles"]) < \
                    database.getPlayerLevel(message.channel, message.author)["balles"]:
                if database.getStat(message.channel, message.author, "exp") > 7:
                    logwithinfos_message(message, "[shop] 1 | OK")
                    yield from messageUser(message, _(":money_with_wings: Tu ajoutes une balle dans ton arme pour 7 points d'expérience.", language))
                    database.addToStat(message.channel, message.author, "balles", 1)
                    database.addToStat(message.channel, message.author, "exp", -7)
                else:
                    logwithinfos_message(message, "[shop] 1 | Pas d'exp")
                    yield from messageUser(message, _(":x: Tu n'as pas assez d'experience pour effectuer cet achat !", language))

            else:
                logwithinfos_message(message, "[shop] 1 | Pas besoin")
                yield from messageUser(message, _(":champagne: Ton chargeur est déjà plein !", language))

        elif item == 2:
            if database.getStat(message.channel, message.author, "chargeurs",
                                default=database.getPlayerLevel(message.channel, message.author)["chargeurs"]) < \
                    database.getPlayerLevel(message.channel, message.author)["chargeurs"]:
                if database.getStat(message.channel, message.author, "exp") > 13:
                    logwithinfos_message(message, "[shop] 2 | OK")
                    yield from messageUser(message, _(":money_with_wings: Tu ajoutes un chargeur à ta réserve pour 13 points d'expérience.", language))
                    database.addToStat(message.channel, message.author, "chargeurs", 1)
                    database.addToStat(message.channel, message.author, "exp", -13)
                else:
                    logwithinfos_message(message, "[shop] 2 | Pas d'exp")
                    yield from messageUser(message, _(":x: Tu n'as pas assez d'experience pour effectuer cet achat !", language))

            else:
                logwithinfos_message(message, "[shop] 2 | Pas besoin")
                yield from messageUser(message, _(":champagne: Ta réserve de chargeurs est déjà pleine !", language))

        elif item == 3: # TODO : Check pas besoin
            if database.getStat(message.channel, message.author, "exp") > 15:
                yield from messageUser(message,
                                       _(":money_with_wings: Tu achetes des munitions AP, qui doubleront tes dégats pendant une journée", language))
                database.setStat(message.channel, message.author, "munAP_", int(time.time()) + 86400)
                database.addToStat(message.channel, message.author, "exp", -15)
                logwithinfos_message(message, "[shop] 3 | OK")

            else:
                yield from messageUser(message, _(":x: Tu n'as pas assez d'experience pour effectuer cet achat !", language))
                logwithinfos_message(message, "[shop] 3 | Pas d'exp")

        elif item == 4: # TODO : Check pas besoin
            if database.getStat(message.channel, message.author, "exp") > 25:
                logwithinfos_message(message, "[shop] 4 | OK")
                yield from messageUser(message, _(":money_with_wings: Tu achetes des munitions explosives, qui tripleront tes dégats pendant une journée",
                                                  language))
                database.setStat(message.channel, message.author, "munExplo", int(time.time()) + 86400)
                database.addToStat(message.channel, message.author, "exp", -25)

            else:
                logwithinfos_message(message, "[shop] 4 | Pas d'exp")
                yield from messageUser(message, _(":x: Tu n'as pas assez d'experience pour effectuer cet achat !", language))


        elif item == 5:
            if database.getStat(message.channel, message.author, "confisque"):
                if database.getStat(message.channel, message.author, "exp") > 40:
                    yield from messageUser(message, _(":money_with_wings: Tu récupéres ton arme pour 40 points d'experience", language))
                    database.setStat(message.channel, message.author, "confisque", False)
                    database.addToStat(message.channel, message.author, "exp", -40)
                    logwithinfos_message(message, "[shop] 5 | OK")
                else:
                    yield from messageUser(message, _(":x: Tu n'as pas assez d'experience pour effectuer cet achat !", language))
                    logwithinfos_message(message, "[shop] 5 | Pas d'exp")

            else:
                yield from messageUser(message, _(":champagne: Ton arme n'est pas confisquée!", language))
                logwithinfos_message(message, "[shop] 5 | Pas besoin")

        elif item == 6:
            if database.getStat(message.channel, message.author, "graisse", default=0) < int(time.time()):
                if database.getStat(message.channel, message.author, "exp") > 8:
                    yield from messageUser(message, _(
                        ":money_with_wings: Tu mets de la graisse dans ton arme, ce qui réduit ses chances d'enrayement de 50% pendant 24h ! Cela te coûte 8 points d'expérience",
                        language))
                    database.setStat(message.channel, message.author, "graisse", int(time.time()) + 86400)
                    database.addToStat(message.channel, message.author, "exp", -8)
                    logwithinfos_message(message, "[shop] 6 | OK")
                else:
                    yield from messageUser(message, _(":x: Tu n'as pas assez d'experience pour effectuer cet achat !", language))
                    logwithinfos_message(message, "[shop] 6 | Pas d'exp")

            else:
                yield from messageUser(message, _(":champagne: Ton arme est déjà bien lubrifiée!", language))
                logwithinfos_message(message, "[shop] 6 | Pas besoin")

        elif item == 8:
            if database.getStat(message.channel, message.author, "detecteurInfra", default=0) < int(time.time()):
                if database.getStat(message.channel, message.author, "exp") > 15:
                    yield from messageUser(message, _(
                        ":money_with_wings: Tu ajoutes un détécteur infrarouge à ton arme pour 15 exp. Tu ne peux plus tirer lorsque aucun canard n'est présent.",
                        language))
                    database.setStat(message.channel, message.author, "detecteurInfra", int(time.time()) + 86400)
                    database.addToStat(message.channel, message.author, "exp", -15)
                    logwithinfos_message(message, "[shop] 8 | OK")
                else:
                    yield from messageUser(message, _(":x: Tu n'as pas assez d'experience pour effectuer cet achat !", language))
                    logwithinfos_message(message, "[shop] 8 | Pas d'exp")

            else:
                yield from messageUser(message, _(":champagne: Tu ne peux pas mettre deux détecteurs infrarouges sur ton arme!", language))
                logwithinfos_message(message, "[shop] 8 | Pas besoin")

        elif item == 9:
            if database.getStat(message.channel, message.author, "silencieux", default=0) < int(time.time()):
                if database.getStat(message.channel, message.author, "exp") > 5:
                    yield from messageUser(message, _(
                        ":money_with_wings: Tu ajoutes un silencieux à ton arme pour 5 exp. Tes tirs n'effrayent plus les canards.",
                        language))
                    database.setStat(message.channel, message.author, "silencieux", int(time.time()) + 86400)
                    database.addToStat(message.channel, message.author, "exp", -5)
                    logwithinfos_message(message, "[shop] 9 | OK")
                else:
                    yield from messageUser(message, _(":x: Tu n'as pas assez d'experience pour effectuer cet achat !", language))
                    logwithinfos_message(message, "[shop] 9 | Pas d'exp")

            else:
                yield from messageUser(message, _(":champagne: Ton arme est déjà équipée d'un silencieux!", language))
                logwithinfos_message(message, "[shop] 9 | Pas besoin")


        elif item == 10:
            if database.getStat(message.channel, message.author, "trefle", default=0) < int(time.time()):
                if database.getStat(message.channel, message.author, "exp") > 13:
                    exp = random.randint(getPref(message.server, "trefleMin"), getPref(message.server, "trefleMax"))

                    yield from messageUser(message, _(
                        ":money_with_wings: Tu achetes un trefle à 4 feuilles, qui te donnera {exp} points d'exp supplémentaires à chaque canard tué pendant 24 heures!",
                        language).format(**{"exp": exp}))
                    database.setStat(message.channel, message.author, "trefle", int(time.time()) + 86400)
                    database.setStat(message.channel, message.author, "trefle_exp", exp)
                    database.addToStat(message.channel, message.author, "exp", -13)
                    logwithinfos_message(message, "[shop] 10 | OK exp : " + str(exp))
                else:
                    yield from messageUser(message, _(":x: Tu n'as pas assez d'experience pour effectuer cet achat !", language))
                    logwithinfos_message(message, "[shop] 10 | Pas d'exp")

            else:
                yield from messageUser(message, _("Trop de chance tue la chance, c'est mort, je ne te donnerais pas un 2eme trefle!", language))
                logwithinfos_message(message, "[shop] 10 | Pas besoin")

        elif item == 12:

            if database.getStat(message.channel, message.author, "exp") > 7:
                if database.getStat(message.channel, message.author, "mouille", default=0) > int(time.time()):

                    yield from messageUser(message,
                                           _(":money_with_wings: Tu te changes et repart chasser avec des vêtements secs, pour seulement 7 exp", language))
                    database.setStat(message.channel, message.author, "mouille", 0)
                    database.addToStat(message.channel, message.author, "exp", -10)
                    logwithinfos_message(message, "[shop] 12 | OK")

                else:
                    yield from messageUser(message, _(":money_with_wings: Tu perds 7 experience, mais au moins, tu as du style !", language))
                    logwithinfos_message(message, "[shop] 12 | Pas besoin (-7 exp)")
                database.addToStat(message.channel, message.author, "exp", -7)
            else:
                yield from messageUser(message, _(":x: Tu n'as pas assez d'experience pour effectuer cet achat !", language))
                logwithinfos_message(message, "[shop] 12 | Pas d'exp")


        elif item == 16:
            if len(args_) <= 2:
                yield from messageUser(message,
                                       _("C'est pas exactement comme ca que l'on fait... Essaye de mettre le pseudo de la personne ? :p", language))
                logwithinfos_message(message, "[shop] 16 | Manque pseudo")
                return

            target = findUser(message, args_[2])
            if target is None:
                yield from messageUser(message, _("Je ne reconnais pas cette personne : {target}", language).format(**{"target": args_[2]}))
                logwithinfos_message(message, "[shop] 16 | Personne non reconnue : " + str(args_[2]))
                return


            if database.getStat(message.channel, message.author, "exp") > 10:
                logwithinfos_message(message, "[shop] 16 | OK")
                yield from messageUser(message, _(
                    ":money_with_wings: Tu jettes un seau d'eau sur {target}, l'obligeant ainsi à attendre 1 heure avant de retourner chasser",
                    language).format(**{"target": target.name}))
                database.setStat(message.channel, target, "mouille", int(time.time()) + 3600)
                database.addToStat(message.channel, message.author, "exp", -10)

            else:
                logwithinfos_message(message, "[shop] 16 | Pas d'exp")
                yield from messageUser(message, _(":x: Tu n'as pas assez d'experience pour effectuer cet achat !", language))


        elif item == 17:
            if len(args_) <= 2:
                yield from messageUser(message,
                                       _("C'est pas exactement comme ca que l'on fait... Essaye de mettre le pseudo de la personne ? :p", language))
                logwithinfos_message(message, "[shop] 17 | Manque pseudo")
                return
            target = findUser(message, args_[2])

            if target is None:
                yield from messageUser(message, _("Je ne reconnais pas cette personne : {target}", language).format(**{"target": args_[2]}))
                logwithinfos_message(message, "[shop] 17 | Personne non reconnue : " + str(args_[2]))
                return

            if database.getStat(message.channel, message.author, "exp") > 14:
                if database.getStat(message.channel, target, "sabotee", "-") == "-":
                    yield from messageUser(message, _(":ok: Tu sabote l'arme de {target}! Elle est maintenant enrayée... Mais il ne le sais pas !",
                                                      language).format(**{"target": target.name}), forcePv=True)
                    database.addToStat(message.channel, message.author, "exp", -14)
                    database.setStat(message.channel, target, "sabotee", message.author.name)
                    logwithinfos_message(message, "[shop] 17 | OK")
                    return
                else:
                    yield from messageUser(message, _(":ok: L'arme de {target} est déjà sabotée!", language).format(**{"target": target.name}),
                                           forcePv=True)
                    logwithinfos_message(message, "[shop] 17 | Pas besoin")

                    return
            else:
                logwithinfos_message(message, "[shop] 17 | Pas d'exp")
                yield from messageUser(message, _(":x: Tu n'as pas assez d'experience pour effectuer cet achat !", language))

        elif item == 18:
            if database.getStat(message.channel, message.author, "exp") > 10:
                if database.getStat(message.channel, message.author, "AssuranceVie", default=0) < int(time.time()):
                    yield from messageUser(message, _(":money_with_wings: Tu souscris à une assurance vie, qui dure une semaine", language))
                    database.setStat(message.channel, message.author, "AssuranceVie", int(time.time()) + 604800)
                    database.addToStat(message.channel, message.author, "exp", -10)
                    logwithinfos_message(message, "[shop] 18 | OK")

                else:
                    yield from messageUser(message, _(":money_with_wings: Tu es déjà assuré !", language))
                    logwithinfos_message(message, "[shop] 18 | Pas besoin")
            else:
                yield from messageUser(message, _(":x: Tu n'as pas assez d'experience pour effectuer cet achat !", language))
                logwithinfos_message(message, "[shop] 18 | Pas d'exp")

        elif item == 20:
            if database.getStat(message.channel, message.author, "exp") > 8:
                yield from messageUser(message, _(
                    ":money_with_wings: Un canard apparaitera dans les 10 prochaines minutes sur le channel, grâce à l'appeau de {mention}. Ca lui coûte 8 exp !",
                    language).format(**{"mention": message.author.mention}))
                database.addToStat(message.channel, message.author, "exp", -8)
                dans = random.randint(0, 60 * 10)
                logwithinfos_message(message, "[shop] 20 | OK : Appeau lancé pour dans {dans} secondes, sur #{channel_name} | {server_name}.".format(
                    **{"dans": dans, "channel_name": message.channel.name, "server_name": message.channel.server.name}))
                yield from asyncio.sleep(dans)
                yield from nouveauCanard({"time": int(time.time()), "channel": message.channel})

            else:
                yield from messageUser(message, _(":x: Tu n'as pas assez d'experience pour effectuer cet achat !", language))
                logwithinfos_message(message, "[shop] 20 | Pas d'exp")

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
                logwithinfos_message(message, "[shop] 22 | OK")

            else:
                yield from messageUser(message, _(":x: Tu n'as pas assez d'experience pour effectuer cet achat !", language))
                logwithinfos_message(message, "[shop] 22 | Pas d'exp")


        elif item == 23:
            if database.getStat(message.channel, message.author, "exp") > 50:
                yield from messageUser(message, _(
                    ":money_with_wings: Tu prépares un canard mécanique sur le chan pour 50 points d'experience. C'est méchant, mais tellement drôle !",
                    language), forcePv=True)
                database.addToStat(message.channel, message.author, "exp", -50)
                logwithinfos_message(message, "[shop] 23 | OK : Attente spawn")
                yield from asyncio.sleep(75)
                try:
                    if getPref(message.server, "mecaRandom") == 0:
                        yield from client.send_message(message.channel, _("-_-'`'°-_-.-'`'° %__%   *BZAACK*", language))
                    elif getPref(message.server, "mecaRandom") == 1:
                        yield from client.send_message(message.channel, "-_-'`'°-_-.-'`'° %__%    " + _(random.choice(canards_cri),
                                                                                                        language=getPref(message.server, "lang")))
                    else:
                        yield from client.send_message(message.channel, random.choice(canards_trace) + "  " + random.choice(canards_portrait) + "  " + _(
                            random.choice(canards_cri), language=getPref(message.server, "lang")))
                    logwithinfos_message(message, "[shop] 23 | Canard envoyé")

                except:
                    logwithinfos_message(message, "[shop] 23 | Erreur")
                    pass
            else:
                yield from messageUser(message, _(":x: Tu n'as pas assez d'experience pour effectuer cet achat !", language))
                logwithinfos_message(message, "[shop] 23 | Pas d'exp")

        else:
            yield from messageUser(message, _(":x: Objet non trouvé :'(", language))
            logwithinfos_message(message, "[shop] Objet non trouvé")

    elif getPref(message.server, "malusFauxCanards") and any(word in message.content for word in canards_trace_tocheck):
        yield from messageUser(message, _("Tu as tendu un drapeau de canard et tu t'es fait tirer dessus. Too bad ! [-1 exp]", language))
        database.addToStat(message.channel, message.author, "exp", -1)
        logwithinfos_message(message, "FAUX CANARD")

    elif message.content.startswith(prefix + "top"):
        yield from deleteMessage(message)
        logwithinfos_message(message, "TOPSCORES")
        args_ = message.content.split(" ")
        if len(args_) == 1:
            nombre = 10
        else:
            try:
                nombre = int(args_[1])
                if nombre not in range(1, 100 + 1):
                    yield from messageUser(message,
                                           _(":mortar_board: Le nombre maximum de joueurs pour le tableau des meilleurs scores est de 100", language))
                    logwithinfos_message(message, "Nombre trop grand")
                    return

            except ValueError:
                yield from messageUser(message, _(
                    ":mortar_board: Tu dois préciser le nombre de joueurs à afficher. Le numéro donné n'est pas valide. `!top [nombre joueurs]`",
                    language))
                logwithinfos_message(message, "Nombre invalide")

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
            x.add_row([i, joueur["name"].replace("`", ""), joueur["exp"], joueur["canardsTues"]])

        yield from messageUser(message,
                               _(":cocktail: Meilleurs scores pour #{channel_name} : :cocktail:\n```{table}```", language).format(
                                   **{"channel_name": message.channel.name, "table": x.get_string(end=nombre, sortby=_("Position", language))}),
                               )
        logwithinfos_message(message, "Tableau affiché")

    elif message.content.startswith(prefix + "ping"):
        yield from deleteMessage(message)
        logwithinfos_message(message, "PING")
        try:
            tmp = yield from client.send_message(message.channel, _('BOUM', language))
            logwithinfos_message(message, "Pong")
        except:
            pass
        yield from asyncio.sleep(4)
        try:
            yield from client.edit_message(tmp, _('... Oups ! Pardon, pong !', language))
        except:
            pass

    elif message.content.startswith(prefix + "duckstat"):
        yield from deleteMessage(message)
        logwithinfos_message(message, "DUCKSTATS")

        args_ = message.content.split(" ")
        if len(args_) == 1:
            target = message.author
        else:
            target = findUser(message, args_[1])

            if target is None:
                yield from messageUser(message, _("Je ne reconnais pas cette personne : {target}", language).format(**{"target": args_[2]}))
                return
        x = PrettyTable()
        if database.getStat(message.channel, target, "canardsTues") > 0:
            ratio = round(database.getStat(message.channel, target, "exp") / database.getStat(message.channel, target, "canardsTues"), 4)
        else:
            ratio = _("Huh, pas de canard tué :x !", language)
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
        x.add_row([_("Ratio (exp/canard tué)", language), ratio])

        x.add_row([_("Niveau actuel", language),
                   str(database.getPlayerLevel(message.channel, target)["niveau"]) + " (" + _(database.getPlayerLevel(message.channel, target)["nom"],
                                                                                              language) + ")"])
        x.add_row([_("Précision des tirs", language), database.getPlayerLevel(message.channel, target)["precision"]])
        x.add_row([_("Fiabilité de l'arme", language), database.getPlayerLevel(message.channel, target)["fiabilitee"]])
        if database.getStat(message.channel, target, "graisse", default=0) > int(time.time()):
            x.add_row([_("Objet : graisse", language), objectTD(message.channel, target, language, "graisse")])
        if database.getStat(message.channel, target, "detecteurInfra", default=0) > int(time.time()):
            x.add_row([_("Objet : détecteur infrarouge", language), objectTD(message.channel, target, language, "detecteurInfra")])
        if database.getStat(message.channel, target, "silencieux", default=0) > int(time.time()):
            x.add_row([_("Objet : silencieux", language), objectTD(message.channel, target, language, "silencieux")])
        if database.getStat(message.channel, target, "trefle", default=0) > int(time.time()):
            x.add_row([_("Objet : trefle {exp} exp", language).format(**{"exp": database.getStat(message.channel, target, "trefle_exp", default=0)}),
                       objectTD(message.channel, target, language, "trefle")])
        if database.getStat(message.channel, target, "mouille", default=0) > int(time.time()):
            x.add_row([_("Effet : mouille", language), objectTD(message.channel, target, language, "mouille")])
        if database.getStat(message.channel, target, "AssuranceVie", default=0) > int(time.time()):
            x.add_row([_("Objet : assurance vie", language), objectTD(message.channel, target, language, "AssuranceVie")])

        yield from messageUser(message,
                               _("Statistiques de {mention} : \n```{table}```\nhttps://api-d.com/snaps/table_de_progression.html", language).format(
                                   **{"table": x.get_string(),
                                      "mention" : target.mention}))
        logwithinfos_message(message, "Duckstats affichés pour " + target.name)

    elif message.content.startswith(prefix + "aide") or message.content.startswith(prefix + "help") or message.content.startswith(prefix + "info"):
        logwithinfos_message(message, "AIDE")
        yield from deleteMessage(message)
        yield from messageUser(message, aideMsg, forcePv=True)

    elif message.content.startswith(prefix + "giveback"):
        yield from deleteMessage(message)

        logwithinfos_message(message, "GIVEBACK")

        if int(message.author.id) in admins:
            yield from messageUser(message, _("En cours...", language))
            logwithinfos_message(message, "En cours")
            database.giveBack(logger)
            yield from messageUser(message, _(":ok: Terminé. Voir les logs sur la console ! ", language))
            logwithinfos_message(message, "Terminé")
        else:
            logwithinfos_message(message, "Interdit de giveback")
            yield from messageUser(message, _(":x: Oupas (Permission Denied)", language))

    elif message.content.startswith(prefix + "coin"):
        yield from deleteMessage(message)
        logwithinfos_message(message, "COIN")

        if message.author.id in servers[message.channel.server.id]["admins"] or int(message.author.id) in admins:
            yield from nouveauCanard({"channel": message.channel, "time": int(time.time())})
            logwithinfos_message(message, "Nouveau canard")
        else:
            yield from messageUser(message, _(":x: Oupas (Permission Denied)", language))
            logwithinfos_message(message, "Interdit")

    elif message.content.startswith(prefix + "nextduck"):
        yield from deleteMessage(message)
        logwithinfos_message(message, "NEXTDUCK")

        if int(message.author.id) in admins:
            prochaincanard = yield from getprochaincanard()
            timetonext = int(prochaincanard["time"] - time.time())
            try:
                yield from client.send_message(message.author,
                                               _("Prochain canard : {time} (dans {timetonext} sec) sur #{channel} | {server}", language).format(**{
                                                   "server"    : prochaincanard["channel"].server.name, "channel": prochaincanard["channel"].name,
                                                   "timetonext": timetonext, "time": prochaincanard["time"]
                                               }))
                logwithinfos_message(message, "Envoyé")
            except:
                logwithinfos_message(message, "Erreur")
                pass
        else:
            yield from messageUser(message, _("Oupas (Permission Denied)", language))
            logwithinfos_message(message, "Interdit de nextduck")

    elif message.content.startswith(prefix + "delchannel"):

        logwithinfos_message(message, "DELCHANNEL")
        if message.author.id in servers[message.channel.server.id]["admins"]:
            if message.channel.id in servers[message.channel.server.id]["channels"]:
                logwithinfos_message(message, "Supression de la channel " + str(message.channel.id) + " | " + str(message.channel.name) + " du fichier...")
                servers[str(message.channel.server.id)]["channels"].remove(message.channel.id)
                JSONsaveToDisk(servers, "channels.json")
                yield from messageUser(message, _(":robot: Channel supprimée du jeu ! Les scores sont neanmoins conservés...", language))
                planification.pop(message.channel)
                logwithinfos_message(message, "Supprimé")

            else:
                yield from messageUser(message, _(":x: Cette channel n'existe pas dans le jeu.", language))
                logwithinfos_message(message, "Channel inexistante")
        elif int(message.author.id) in admins:
            if message.channel.id in servers[message.channel.server.id]["channels"]:
                logger.debug("Supression de la channel {channel_id} | {channel_name} du fichier...".format(
                    **{"channel_id": message.channel.id, "channel_name": message.channel.name}))
                servers[str(message.channel.server.id)]["channels"].remove(message.channel.id)
                JSONsaveToDisk(servers, "channels.json")
                yield from messageUser(message, _(
                    ":robot: Channel supprimée du jeu ! Les scores sont neanmoins conservés... :warning: Vous n'etes pas administrateur du serveur",
                    language))
                logwithinfos_message(message, "(GA) channel suprimée")
                planification.pop(message.channel)

            else:
                yield from messageUser(message,
                                       _(":x: Cette channel n'existe pas dans le jeu. :warning: Vous n'etes pas administrateur du serveur", language))
                logwithinfos_message(message, "(GA) Channel inexistante")
        else:
            logwithinfos_message(message, "Interdit de delchannel")
            yield from messageUser(message, _(":x: Vous n'etes pas l'administrateur du serveur.", language))

        return

    elif message.content.startswith(prefix + "set"):
        logwithinfos_message(message, "SET")
        args_ = message.content.split(" ")
        if len(args_) == 1 or len(args_) > 3:
            logwithinfos_message(message, "Erreur de syntaxe")
            yield from messageUser(message, _(":x: Oops, mauvaise syntaxe. !set [paramètre] <valeur>", language))
            x = PrettyTable()

            x._set_field_names([_("Paramètre", language), _("Valeur actuelle", language), _("Valeur par défaut", language)])
            for param in defaultSettings.keys():
                x.add_row([param, getPref(message.server, param), defaultSettings[param]])

            yield from messageUser(message,
                                   _("Liste des paramètres disponibles : \n```{table}```", language).format(
                                       **{"table": x.get_string(sortby=_("Paramètre", language))}))

            return

        if not args_[1] in defaultSettings:
            yield from messageUser(message, _(":x: Oops, le paramètre n'as pas été reconnu. !set [paramètre] <valeur>", language))
            logwithinfos_message(message, "Parametre introuvable : " + args_[1])
            return

        if message.author.id in servers[message.channel.server.id]["admins"] or int(message.author.id) in admins:
            if len(args_) == 2:
                if args_[1] in servers[message.server.id]["settings"]: servers[message.server.id]["settings"].pop(args_[1])
                logwithinfos_message(message, "Valeur de " + args_[1] + " réinitialisée")
                yield from messageUser(message, _(":ok: Valeur réinitialisée a la valeur par défaut !", language))
                JSONsaveToDisk(servers, "channels.json")
                return
            else:
                if args_[2].lower() == "true":
                    args_[2] = True
                elif args_[2].lower() == "false":
                    args_[2] = False

                try:
                    args_[2] = defaultSettings[args_[1]]["type"](args_[2])
                except ValueError:
                    logwithinfos_message(message, "Erreur de typage pour {arg} avec un type attendu à {type}".format(**{"type": defaultSettings[args_[1]]["type"].__name__,
                                                                                                                        "arg" : args_[2]}))

                    yield from messageUser(message, _(":x: Erreur, l'argument n'est pas typé correctement (attendu : {type})", language).format(**{"type": defaultSettings[args_[1]]["type"].__name__}))
                    return

                if args_[1] == "canardsJours":
                    maxCJ = int(125 + (message.server.member_count / (5+ ( message.server.member_count / 300))))
                    if args_[2] > maxCJ:
                        messageUser(message, _(":warning: Nombres de canards par jour limité afin de ne pas abuser des resources du bot.", language))
                        logwithinfos_message(message, "Limitation de canardsJours qui était à " + str(args_[2]) )
                        args_[2] = maxCJ
                logwithinfos_message(message, "Changement du paramétre " + args_[1] + " pour " + str(args_[2]) + " (" + str(type(args_[2])) + ")")
                servers[message.server.id]["settings"][args_[1]] = args_[2]

            JSONsaveToDisk(servers, "channels.json")

            yield from messageUser(message,
                                   _(":ok: Valeur modifiée à {value}", language).format(**{"value": args_[2]}))

            if args_[1] == "canardsJours":
                yield from planifie(channel=message.channel)
                logwithinfos_message(message, "Replanification en cours pour la channel")



        else:
            logwithinfos_message(message, "Interdit de set")
            yield from messageUser(message, _(":x: Oops, vous n'etes pas administrateur du serveur...", language))

        return

    elif message.content.startswith(prefix + "duckplanning"):
        yield from deleteMessage(message)
        logwithinfos_message(message, "DUCKPLANNING")
        if message.author.id in servers[message.channel.server.id]["admins"] or int(message.author.id) in admins:
            table = ""
            for timestamp in planification[message.channel]:
                table += str(int((time.time() - timestamp) / 60)) + "\n"

            try:
                yield from client.send_message(message.author,
                                               _(":hammer: TimeDelta en minutes pour les canards sur le chan\n```{table}```", language).format(
                                                   **{"table": table}))
                logwithinfos_message(message, "Duckplanning envoyé")
            except:
                logwithinfos_message(message, "Erreur dans duckplanning")
                pass


        else:
            logwithinfos_message(message, "Interdit de duckplanning")
            yield from messageUser(message, _(":x: Oops, vous n'etes pas administrateur du serveur...", language))

    elif message.content.startswith(prefix + "stat"):
        yield from deleteMessage(message)
        logwithinfos_message(message, "STATS")
        compteurCanards = 0
        serveurs = 0
        channels = 0
        membres = 0
        servsFr = 0
        servsEn = 0
        servsEt = 0
        servsDon = 0
        p100cj = 0
        p50cj = 0
        p24cj = 0
        m24cj = 0
        for server in client.servers:
            serveurs += 1
            slang = getPref(server, "lang")
            if slang == "fr":
                servsFr += 1
            elif slang == "en":
                servsEn += 1
            else:
                logger.debug("Serveur étranger : {lang : " + str(lang) + ", server:" + str(server.name) + "|" + str(server.id) + "}" )
                servsEt += 1
            if getPref(server, "donExp"):
                servsDon += 1
            cj = getPref(server, "canardsJours")
            if cj is not None:
                if cj >= 100:
                    p100cj += 1
                    p50cj += 1
                    p24cj += 1
                elif cj >= 50:
                    p50cj += 1
                    p24cj += 1
                elif cj > 24:
                    p24cj += 1
                elif cj < 24:
                    m24cj += 1

            for channel in server.channels:
                channels += 1
                if channel in planification.keys():
                    compteurCanards += len(planification[channel])
            membres += len(server.members)
        pid = os.getpid()
        py = psutil.Process(pid)
        memoryUsed = py.memory_info()[0] / 2. ** 30
        uptime = int(time.time() - startTime)

        yield from messageUser(message, _("""Statistiques de DuckHunt:

    DuckHunt est actif dans `{nbre_channels_actives}` channels, sur `{nbre_serveurs}` serveurs. Il voit `{nbre_channels}` channels, et plus de `{nbre_utilisateurs}` utilisateurs.
    Dans la planification d'aujourd'hui sont prévus et ont été lancés au total `{nbre_canards}` canards (soit `{nbre_canards_minute}` canards par minute).
    Au total, le bot connait `{nbre_serveurs_francais}` serveurs francais, `{nbre_serveurs_anglais}` serveurs anglais et `{nbre_serveurs_etrangers}` serveurs étrangers.
    Il a reçu au total durant la session `{messages}` message(s) (soit `{messages_minute}` message(s) par minute).
    Le bot est lancé depuis `{uptime_sec}` seconde(s), ce qui équivaut à `{uptime_min}` minute(s) ou encore `{uptime_heures}` heure(s), ou, en jours, `{uptime_jours}` jour(s).
    Sur l'ensemble des serveurs, `{servsDon}` ont activé le don d'experience, `{plusde100cj}` serveurs font apparaitre plus de 100 canards par jour, `{plusde24cj}` serveurs en font plus de 24 par jours, tandis que `{moinsde24cj}` en font apparaitre moins de 24 par jour!
    Le bot utilise actuellement `{memory_used}` MB de ram.

    Le bot est lancé avec Python ```{python_version}```""", language).format(**{
            "nbre_channels_actives"  : len(planification),
            "nbre_serveurs"          : serveurs,
            "nbre_serveurs_francais" : servsFr,
            "nbre_serveurs_anglais"  : servsEn,
            "nbre_serveurs_etrangers": servsEt,
            "nbre_channels"          : channels,
            "nbre_utilisateurs"      : membres,
            "nbre_canards"           : compteurCanards,
            "nbre_canards_minute"    : round(compteurCanards / 1440, 4),
            "messages"               : CompteurMessages,
            "messages_minute"        : round(CompteurMessages / (uptime / 60), 4),
            "uptime_sec"             : uptime,
            "uptime_min"             : int(uptime / 60),
            "uptime_heures"          : int(uptime / 60 / 60),
            "uptime_jours"           : int(uptime / 60 / 60 / 24),
            "servsDon"               : servsDon,
            "plusde100cj"            : p100cj,
            "plusde50cj"             : p50cj, # NU
            "plusde24cj"             : p24cj,
            "moinsde24cj"            : m24cj,
            "memory_used"            : round(memoryUsed * 1000, 5),
            "python_version"         : str(sys.version)
        }))
        logwithinfos_message(message, "Stats envoyées")

    elif message.content.startswith(prefix + "permissions"):
        yield from deleteMessage(message)
        logwithinfos_message(message, "PERMISSIONS")
        permissionsToHave = ["change_nicknames", "connect", "create_instant_invite", "embed_links", "manage_messages", "mention_everyone", "read_messages",
                             "send_messages", "send_tts_messages"]
        if message.author.id in servers[message.channel.server.id]["admins"] or int(message.author.id) in admins:
            permissions_str = ""
            for permission, value in message.server.me.permissions_in(message.channel):
                if value:
                    emo = ":white_check_mark:"
                else:
                    emo = ":negative_squared_cross_mark:"
                if (value and permission in permissionsToHave) or (not value and not permission in permissionsToHave):
                    pass
                else:
                    emo += ":warning:"
                permissions_str += "\n{value}\t{name}".format(**{"value": emo, "name": str(permission)})
            yield from messageUser(message, _("Permissions : {permissions}", language).format(**{"permissions": permissions_str}))
            logwithinfos_message(message, "Permissions affichées")
        else:
            logwithinfos_message(message, "Interdit de voir les permissions")
            yield from messageUser(message, _(":x: Oops, vous n'etes pas administrateur du serveur...", language))
    elif message.content.startswith(prefix + "dearm"):
        logwithinfos_message(message, "DEARM")
        if message.author.id in servers[message.channel.server.id]["admins"] or int(message.author.id) in admins:
            args_ = message.content.split(" ")

            if len(args_) == 1:
                yield from messageUser(message, _(":x: Joueur non spécifié", language))
                logwithinfos_message(message, "[dearm] Joueur non spécifié")
                return
            else:
                target = findUser(message, args_[1])

                if target is None:
                    yield from messageUser(message, _("Je ne reconnais pas cette personne : {target}", language).format(**{"target": args_[2]}))
                    logwithinfos_message(message, "[dearm] | Personne non reconnue : " + str(args_[2]))
                    return

            if not database.getStat(message.channel, target, "banni", default=False):
                if target.id not in servers[message.channel.server.id]["admins"] and int(target.id) not in admins:
                    database.setStat(message.channel, target, "banni", True)
                    yield from messageUser(message, _(":ok: Ce joueur est maintenant banni du bot !", language))
                    logwithinfos_message(message, "[dearm] " + target.name + " est banni du bot")
                else:
                    yield from messageUser(message, _(":x: Il est admin ce mec, c'est mort !", language))
                    logwithinfos_message(message, "[dearm] Fail : target admin")
            else:
                yield from messageUser(message, _(":x: Il est déja banni, lui ^^", language))
                logwithinfos_message(message, "[dearm] Fail : déjà banni")
        else:
            logwithinfos_message(message, "Interdit de dearm")
            yield from messageUser(message, _(":x: Oops, vous n'etes pas administrateur du serveur...", language))

    elif message.content.startswith(prefix + "rearm"):
        logwithinfos_message(message, "REARM")
        if message.author.id in servers[message.channel.server.id]["admins"] or int(message.author.id) in admins:
            args_ = message.content.split(" ")

            if len(args_) == 1:
                yield from messageUser(message, _(":x: Joueur non spécifié", language))
                logwithinfos_message(message, "[rearm] Joueur non spécifié")
                return
            else:
                target = findUser(message, args_[1])

                if target is None:
                    yield from messageUser(message, _("Je ne reconnais pas cette personne : {target}", language).format(**{"target": args_[2]}))
                    logwithinfos_message(message, "[rearm] | Personne non reconnue : " + str(args_[2]))
                    return

            if database.getStat(message.channel, target, "banni", default=False):
                database.setStat(message.channel, target, "banni", False)
                yield from messageUser(message, _(":ok: Ce joueur est maintenant dé-banni du bot !", language))
                logwithinfos_message(message, "[rearm] " + target.name + " est débanni du bot")
            else:
                yield from messageUser(message, _(":x: Il est pas banni, lui ^^", language))
                logwithinfos_message(message, "[rearm] Joueur non banni")
        else:
            yield from messageUser(message, _(":x: Oops, vous n'etes pas administrateur du serveur...", language))
            logwithinfos_message(message, "Non autorisé à rearm")

    elif message.content.startswith(prefix + "sendexp"):
        yield from deleteMessage(message)
        logwithinfos_message(message, "SENDEXP")
        if getPref(message.server, "donExp"):
            args_ = message.content.split(" ")

            if len(args_) < 3:
                yield from messageUser(message, _(":x: Joueur/Montant non spécifié : `!sendexp @joueur montant`", language))
                logwithinfos_message(message, "[sendexp] Joueur non spécifié")
                return
            else:
                target = findUser(message, args_[1])

                if target is None:
                    yield from messageUser(message, _("Je ne reconnais pas cette personne : {target}", language).format(**{"target": args_[2]}))
                    logwithinfos_message(message, "[sendexp] | Personne non reconnue : " + str(args_[2]))
                    return
            montant = args_[2]
            if not representsInt(montant) or int(montant) <= 0:
                yield from messageUser(message, _(":x: Essaye de préciser un montant valide, c'est a dire positif et entier", language))
                logwithinfos_message(message, "[sendexp] montant invalide")
                return
            montant = int(montant)
            if database.getStat(message.channel, message.author, "exp") > montant:
                database.addToStat(message.channel, message.author, "exp", -montant)
                if getPref(message.server, "donExpTaxe") > 0:
                    taxes = montant * (getPref(message.server, "donExpTaxe") / 100)
                else:
                    taxes = 0
                database.addToStat(message.channel, target, "exp", montant - taxes)
                yield from messageUser(message,
                                       _("Vous avez envoyé {amount} exp à {target} (et payé {taxes} exp de taxe de transfert) !", language).format(
                                           **{"amount": montant - taxes, "target": target.mention, "taxes": taxes}))
                logwithinfos_message(message, "[sendexp] Exp envoyé à {target} : {amount} exp et {taxes}".format(
                    **{"amount": montant - taxes, "target": target.mention, "taxes": taxes}))
            else:
                logwithinfos_message(message, "[sendexp] manque d'experience")
                yield from messageUser(message, _("Vous n'avez pas assez d'experience", language))



        else:
            logwithinfos_message(message, "[sendexp] Don non activé")
            yield from messageUser(message,
                                   _("Le don d'exp n'est pas activé sur le serveur, vous pouvez demander aux admins de l'activer avec `!set donExp True`",
                                     language))

    elif message.content.startswith(prefix + "giveexp"):
        logwithinfos_message(message, "GIVEEXP")
        if message.author.id in servers[message.channel.server.id]["admins"] or int(message.author.id) in admins:
            args_ = message.content.split(" ")

            if len(args_) < 3:
                messageUser(message, _("Erreur de syntaxe : !giveexp <joueur> <exp>", language))
                logwithinfos_message(message, "[giveexp] Erreur de syntaxe")
                return
            else:
                target = findUser(message, args_[1])

                if target is None:
                    yield from messageUser(message, _("Je ne reconnais pas cette personne : {target}", language).format(**{"target": args_[2]}))
                    logwithinfos_message(message, "[giveexp] | Personne non reconnue : " + str(args_[2]))
                    return

            if not representsInt(args_[2]):
                yield from messageUser(message, _("Erreur de syntaxe : !giveexp <joueur> <exp>", language))
                logwithinfos_message(message, "[giveexp] Erreur de syntaxe, le 2eme argument n'est pas un int")
                return
            else:
                args_[2] = int(args_[2])

                database.addToStat(message.channel, target, "exp", args_[2])
                logwithinfos_message(message, "[giveexp] Ajout de " + str(args_[2]) + " points d'experience à " + target.name)
                yield from messageUser(message, _(":ok:, il a maintenant {newexp} points d'experience !", language).format(
                    **{"newexp": database.getStat(message.channel, target, "exp")}))

        else:
            logwithinfos_message(message, "Giveexp interdit")
            yield from messageUser(message, _(":x: Oops, vous n'etes pas administrateur du serveur...", language))

    elif message.content.startswith(prefix + "purgemessages"):
        logwithinfos_message(message, "PURGE MESSAGES (" + str(message.author) + ")")

        if message.author.id in servers[message.channel.server.id]["admins"] or int(message.author.id) in admins:
            if message.channel.permissions_for(message.server.me).manage_messages:
                deleted = yield from client.purge_from(message.channel, limit=500)
                yield from messageUser(message, _("{deleted} message(s) supprimés", language).format(**{"deleted": len(deleted)}))
                logwithinfos_message(message, str(len(deleted)) + " messages supprimés")
            else:
                yield from messageUser(message, _("0 message(s) supprimés : permission refusée", language))
                logwithinfos_message(message, "Le bot n'as pas la permission")
        else:
            logwithinfos_message(message, "Interdit de purgemessages")
            yield from messageUser(message, _(":x: Oops, vous n'etes pas administrateur du serveur...", language))

    elif message.content.startswith(prefix + "deladmin"):
        logwithinfos_message(message, "DELADMIN")

        args_ = message.content.split(" ")
        if len(args_) == 1:
            target = message.author
        else:
            target = findUser(message, args_[1])

            if target is None:
                yield from messageUser(message, _("Je ne reconnais pas cette personne : {target}", language).format(**{"target": args_[2]}))
                return

        if message.author.id in servers[message.channel.server.id]["admins"] or int(message.author.id) in admins:
            if target.id in servers[message.channel.server.id]["admins"]:
                servers[message.channel.server.id]["admins"].remove(target.id)
                logwithinfos_message(message, "Supression de l'admin {admin_name} | {admin_id}".format(
                    **{
                        "admin_id"   : target.id, "admin_name": target.name
                    }))
                yield from messageUser(message,
                                       _(":robot: Supression de l'admin {admin_name} | {admin_id} sur le serveur : {server_name} | {server_id}",
                                         language).format(
                                           **{
                                               "admin_id"   : target.id, "admin_name": target.name, "server_id": message.server.id,
                                               "server_name": message.server.name
                                           }))
                JSONsaveToDisk(servers, "channels.json")
            else:
                yield from messageUser(message, _(":x: Oops, cette personne n'est pas administrateur du serveur...", language))
                logwithinfos_message(message, "Personne non administrateur")
        else:
            logwithinfos_message(message, "Interdit de deladmin")
            yield from messageUser(message, _(":x: Oops, vous n'etes pas administrateur du serveur...", language))

        return

    elif message.content.startswith(prefix + "deleteeverysinglescoreandstatonthischannel"):
        logwithinfos_message(message, "deleteeverysinglescoreandstatonthischannel")

        if message.author.id in servers[message.channel.server.id]["admins"] or int(message.author.id) in admins:
            database.delChannelTable(message.channel)
            yield from messageUser(message, _(":ok: Les scores / stats de la channel ont bien étés supprimés.", language))
            logwithinfos_message(message, "Scores + stats supprimés")
        else:
            logwithinfos_message(message, "Action interdite")
            yield from messageUser(message, _(":x: Oops, vous n'etes pas administrateur du serveur...", language))

    elif message.content.startswith(prefix + "serverlist"):
        logwithinfos_message(message, "SERVERLIST")
        if int(message.author.id) in admins:
            logwithinfos_message(message, "Construction de la serverlist")
            x = PrettyTable()
            args_ = message.content.split(" ")
            x._set_field_names([_("Nom", language), _("Invitation", language), _("Channels actives", language), _("Nombres de connectés", language), _("Canards par jour", language),
                                _("Permissions en trop", language), _("Permissions manquantes", language)])
            x.reversesort = True

            tmp = yield from client.send_message(message.channel, str(message.author.mention) + _(" > En cours", language))
            servers = JSONloadFromDisk("channels.json", default="{}")

            total = len(client.servers)
            i = 0
            lu = 0
            for server in client.servers:
                i += 1
                if time.time() - lu >= 1.5 or i == total:
                    lu = time.time()
                    try:
                        yield from client.edit_message(tmp, str(message.author.mention) + _(" > En cours ({done}/{total})", language).format(
                            **{"done": i, "total": total}))
                    except:
                        pass
                invite = None

                permissionsToHave = ["change_nicknames", "connect", "create_instant_invite", "embed_links", "manage_messages", "mention_everyone",
                                     "read_messages",
                                     "send_messages", "send_tts_messages"]

                permEnMoins = 0
                permEnPlus = 0
                channel = server.default_channel
                for permission, value in channel.permissions_for(server.me):
                    if not value and permission in permissionsToHave:
                        permEnMoins += 1
                    elif value and not permission in permissionsToHave:
                        permEnPlus += 1

                if "invitations" in args_:
                    for channel in server.channels:
                        permissions = channel.permissions_for(server.me)
                        if permissions.create_instant_invite:
                            invite = yield from client.create_invite(channel, max_age=10 * 60)
                            try:
                                x.add_row([server.name, invite.url, str(len(servers[server.id]["channels"])) + "/" + str(len(server.channels)),
                                           server.member_count, database.getPref(server, "canardsJours"), permEnPlus, permEnMoins])
                            except KeyError:  # Pas de channels ou une autre merde dans le genre ?
                                x.add_row([server.name, invite.url, "0" + "/" + str(len(server.channels)), server.member_count, database.getPref(server, "canardsJours"), permEnPlus, permEnMoins])
                            break
                if not invite:
                    try:
                        x.add_row(
                            [server.name, "", str(len(servers[server.id]["channels"])) + "/" + str(len(server.channels)), server.member_count, database.getPref(server, "canardsJours"), permEnPlus,
                             permEnMoins])
                    except KeyError:  # Pas de channels ou une autre merde dans le genre ?
                        x.add_row([server.name, "", str(0) + "/" + str(len(server.channels)), server.member_count, database.getPref(server, "canardsJours"), permEnPlus, permEnMoins])

            yield from messageUser(message, x.get_string(sortby=_("Nombres de connectés", language)))
            logwithinfos_message(message, "Serverlist envoyée")

        else:
            logwithinfos_message(message, "Interdit de serverlist")
            yield from messageUser(message, _(":x: Oops, vous n'etes pas administrateur du serveur...", language))


@client.async_event
def on_channel_delete(channel):
    logger.info(_("Channel supprimée... {channel_id} | {channel_name}").format(**{"channel_id": channel.id, "channel_name": channel.name}))
    servers = JSONloadFromDisk("channels.json", default="{}")
    if channel in planification.keys():
        planification.pop(channel)
    if channel.id in servers[channel.server.id]["channels"]:
        prev = len(canards)
        canards[:] = [canard for canard in canards if not channel == canard["channel"]]
        logwithinfos(channel, "", "Canards supprimés : " + str(prev - len(canards)))
        servers[channel.server.id]["channels"].remove(channel.id)
        database.delChannelTable(channel)
        JSONsaveToDisk(servers, "channels.json")


@client.async_event
def on_server_remove(server):
    logger.info(_("Serveur supprimé... {server_id} | {server_name}").format(**{"server_id": server.id, "server_name": server.name}))
    for channel in server.channels:
        yield from on_channel_delete(channel)
    database.delServerTables(server)
    servers = JSONloadFromDisk("channels.json", default="{}")
    servers.pop(server.id)
    JSONsaveToDisk(servers, "channels.json")
    logger.debug("Serveur supprimé")



@client.async_event
def on_message_edit(old, new):
    if new.author == client.user:
        return
    if new.author.bot:
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
    if getPref(new.server, "malusFauxCanards") and getPref(new.server, "malusFauxCanards") and any(word in new.content for word in canards_trace_tocheck):
        logwithinfos_message(new, "Faux canard edité")
        yield from messageUser(new, _("Tu as essayé de brain le bot sortant un drapeau de canard après coup! [-5 exp]", language))
        database.addToStat(new.channel, new.author, "exp", -5)


logger.debug("Connexion à Discord — Début de la boucle")
try:
    client.loop.run_until_complete(client.start(token))
except KeyboardInterrupt:
    logger.warn(_("Arret demandé"))
    client.loop.run_until_complete(allCanardsGo())
    client.loop.run_until_complete(client.logout())
    asyncio.sleep(2)
    # cancel all tasks lingering
finally:
    client.loop.close()

