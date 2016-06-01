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

def main():
    pass

if __name__ == '__main__':
    main()
