# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5

token = "Enter a bot token here"
admins = [138751484517941259]

canardsJours = 99
channelWL = False
whitelist = [136797998217822208, 184672042770104321, 187961300704428033] # Ids des channels sur lequel le bot est actif
tempsAttente = 5 * 60

deleteCommands = True

aideMsg = """Aide pour DuckHunt :
```Le but du jeu est de tuer les canards dès que vous les voyez ! C'est un peu un fps, mais pour discord :°)

Les commandes disponibles sont les suivantes :

Commandes joueur:
!bang\t\tPour (tenter) de tuer le canard qui est apparu. Ne pas tirer quand il n'y a pas de canards, sinon...
!reload\t\tRecharge ou décoince votre arme
!duckstats\t\tAffiche les statistiques DuckHunt
!shop [N° ITEM]\t\tPermet d'acher des items à l'aide de points d'experience.
!top <Nombre de joueurs maxi>\t\tAffiche les meilleurs scores
!aide\t\tAffiche l'aide

Liste des items dans le shop:

N°1\t\tAjoute une balle a votre arme (7 exp)
N°2\t\tAjoute un chargeur à votre réserve (13 exp)
N°23\t\tInvoque un canard mécanique (faux canard), 75 secondes aprés la commande sur le chan (50 exp)


Commandes admin:
!info\t\tAffiche des informations sur le channel en cours
!giveback\t\tDonne aux joueurs leurs armes et des chargeurs, comme à minuit !
!coin\t\tFait apparaitre un canard
```"""