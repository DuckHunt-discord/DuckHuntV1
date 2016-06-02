# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5

token = "Enter a bot token here"
canardsJours = 99
channelWL = True
whitelist = [136797998217822208, 184672042770104321, 187961300704428033] # Ids des channels sur lequel le bot est actif
tempsAttente = 5

aideMsg = """Aide pour DuckHunt :
```Le but du jeu est de tuer les canards dès que vous les voyez ! C'est un peu un fps, mais pour discord :°)

Les commandes disponibles sont les suivantes :

Commandes joueur:
!bang\t\tPour (tenter) de tuer le canard qui est apparu. e pas tirer quand il n'y a pas de canards, sinon...
!reload\t\tRecharge ou décoince votre arme
!duckstats\t\tAffiche les statistiques DuckHunt
!aide\t\tAffiche l'aide

Commandes admin:
!info\t\tAffiche des informations sur le channel en cours
!coin\t\tFait apparaitre un canard
```"""