# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5

token = "Enter a bot token here"
admins = [138751484517941259]

canardsJours = 99
channelWL = False
whitelist = [136797998217822208, 184672042770104321, 187961300704428033] # Ids des channels sur lequel le bot est actif
tempsAttente = 5 * 60
levels = [{"niveau": 0, "expMin": -5, "nom": "danger public", "precision": 55, "fiabilitee": 85, "balles": 6, "chargeurs": 1},
          {"niveau": 1, "expMin": -4, "nom": "touriste", "precision": 55, "fiabilitee": 85, "balles": 6, "chargeurs": 2},
          {"niveau": 2, "expMin": 20, "nom": "noob", "precision": 56, "fiabilitee": 86, "balles": 6, "chargeurs": 2},
          {"niveau": 3, "expMin": 50, "nom": "stagiaire", "precision": 57, "fiabilitee": 87, "balles": 6, "chargeurs": 2},
          {"niveau": 4, "expMin": 90, "nom": "rateur de canards", "precision": 58, "fiabilitee": 88, "balles": 6, "chargeurs": 2},
          {"niveau": 5, "expMin": 140, "nom": "membre du Comité Contre les Canards", "precision": 59, "fiabilitee": 89, "balles": 6, "chargeurs": 2},
          {"niveau": 6, "expMin": 200, "nom": "détesteur de canards", "precision": 60, "fiabilitee": 90, "balles": 4, "chargeurs": 3},
          {"niveau": 7, "expMin": 270, "nom": "emmerdeur de canards", "precision": 65, "fiabilitee": 93, "balles": 4, "chargeurs": 3},
          {"niveau": 8, "expMin": 350, "nom": "déplumeur de canards", "precision": 67, "fiabilitee": 93, "balles": 4, "chargeurs": 3},
          {"niveau": 9, "expMin": 440, "nom": "chasseur", "precision": 55, "fiabilitee": 93, "balles": 4, "chargeurs": 3},
          {"niveau": 10, "expMin": 540, "nom": "retourneur de canards", "precision": 71, "fiabilitee": 94, "balles": 4, "chargeurs": 3},
          {"niveau": 11, "expMin": 650, "nom": "assommeur de canards", "precision": 73, "fiabilitee": 94, "balles": 4, "chargeurs": 3},
          {"niveau": 12, "expMin": 770, "nom": "mâchouilleur de canards", "precision": 73, "fiabilitee": 94, "balles": 4, "chargeurs": 3},
          {"niveau": 13, "expMin": 900, "nom": "bouffeur de canards", "precision": 74, "fiabilitee": 95, "balles": 4, "chargeurs": 3},
          {"niveau": 14, "expMin": 1040, "nom": "aplatisseur de canards", "precision": 74, "fiabilitee": 95, "balles": 4, "chargeurs": 3},
          {"niveau": 15, "expMin": 1190, "nom": "démonteur de canards", "precision": 75, "fiabilitee": 95, "balles": 4, "chargeurs": 3},
          {"niveau": 16, "expMin": 1350, "nom": "démolisseur de canards", "precision": 80, "fiabilitee": 97, "balles": 2, "chargeurs": 4},
          {"niveau": 17, "expMin": 1520, "nom": "tueur de canards", "precision": 81, "fiabilitee": 97, "balles": 2, "chargeurs": 4},
          {"niveau": 18, "expMin": 1700, "nom": "écorcheur de canards", "precision": 81, "fiabilitee": 97, "balles": 2, "chargeurs": 4},
          {"niveau": 19, "expMin": 1890, "nom": "prédateur", "precision": 82, "fiabilitee": 97, "balles": 2, "chargeurs": 4},
          {"niveau": 20, "expMin": 2090, "nom": "découpeur de canards", "precision": 82, "fiabilitee": 97, "balles": 2, "chargeurs": 4},
          {"niveau": 21, "expMin": 2300, "nom": "décortiqueur de canards", "precision": 83, "fiabilitee": 98, "balles": 2, "chargeurs": 4},
          {"niveau": 22, "expMin": 2520, "nom": "fraggeur de canards", "precision": 83, "fiabilitee": 98, "balles": 2, "chargeurs": 4},
          {"niveau": 23, "expMin": 2750, "nom": "éclateur de canards", "precision": 84, "fiabilitee": 98, "balles": 2, "chargeurs": 4},
          {"niveau": 24, "expMin": 2990, "nom": "défonceur de canards", "precision": 84, "fiabilitee": 98, "balles": 2, "chargeurs": 4},
          {"niveau": 25, "expMin": 3240, "nom": "bousilleur de canards", "precision": 85, "fiabilitee": 98, "balles": 2, "chargeurs": 4},
          {"niveau": 26, "expMin": 3500, "nom": "poutreur de canards", "precision": 90, "fiabilitee": 99, "balles": 1, "chargeurs": 5},
          {"niveau": 27, "expMin": 3770, "nom": "empaleur de canards", "precision": 91, "fiabilitee": 99, "balles": 1, "chargeurs": 5},
          {"niveau": 28, "expMin": 4050, "nom": "éventreur de canards", "precision": 91, "fiabilitee": 99, "balles": 1, "chargeurs": 5},
          {"niveau": 29, "expMin": 4340, "nom": "terreur des canards", "precision": 92, "fiabilitee": 99, "balles": 1, "chargeurs": 5},
          {"niveau": 30, "expMin": 4640, "nom": "exploseur de canards", "precision": 92, "fiabilitee": 99, "balles": 1, "chargeurs": 5},
          {"niveau": 31, "expMin": 4950, "nom": "destructeur de canards", "precision": 93, "fiabilitee": 99, "balles": 1, "chargeurs": 5},
          {"niveau": 32, "expMin": 5270, "nom": "pulvérisateur de canards", "precision": 93, "fiabilitee": 99, "balles": 1, "chargeurs": 5},
          {"niveau": 33, "expMin": 5600, "nom": "démolécularisateur de canards", "precision": 94, "fiabilitee": 99, "balles": 1, "chargeurs": 5},
          {"niveau": 34, "expMin": 5940, "nom": "désintégrateur de canards", "precision": 94, "fiabilitee": 99, "balles": 1, "chargeurs": 5},
          {"niveau": 35, "expMin": 6290, "nom": "atomiseur de canards", "precision": 95, "fiabilitee": 99, "balles": 1, "chargeurs": 5},
          {"niveau": 36, "expMin": 6650, "nom": "annihilateur de canards", "precision": 95, "fiabilitee": 99, "balles": 1, "chargeurs": 5},
          {"niveau": 37, "expMin": 7020, "nom": "serial duck killer", "precision": 96, "fiabilitee": 99, "balles": 1, "chargeurs": 5},
          {"niveau": 38, "expMin": 7400, "nom": "génocideur de canards", "precision": 96, "fiabilitee": 99, "balles": 1, "chargeurs": 5},
          {"niveau": 39, "expMin": 7790, "nom": "chômeur pour cause d'extinction de l'espèce", "precision": 97, "fiabilitee": 99, "balles": 1, "chargeurs": 5}]


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


inutilite = ["un canard en peluche.", "un canard en plastique pour le bain.", "un canard vibrant.", "un tas de plumes.", "un chewing-gum mâchouillé.",
             "un prospectus du CCCCC (Coalition Contre le Comité Contre les Canards).", "une vieille chaussure.", "un truc à ressort.",
             "une bouse de vache.", "une crotte de chien.", "un permis de chasse expiré.", "une douille.", "un mégot.", "un préservatif usagé.",
             "une lunette de visée cassée.", "un détecteur infrarouge cassé.", "un silencieux tordu.", "une boîte vide de munitions AP.",
             "une boîte vide de munitions explosives.", "un trèfle à 4 feuilles auquel il en manque une.", "un appeau cassé.", "un miroir cassé.",
             "un canard mécanique rouillé.", "une paire de lunettes de soleil sans ses verres.", "le béret de Donald.",
             "une pastille de menthe à moitié fondue.", "une boîte de nettoyant Abraxo.", "un fusil avec le bout du canon en fleur.",
             "un vieux couteau de chasse.", "un vieil enregistrement vidéo : http://tinyurl.com/zbejktu",
             "une vieille photo de chasse : http://tinyurl.com/hmn4r88", "une vieille carte postale : http://tinyurl.com/hbnkpzr",
             "une photo de super-canard : http://tinyurl.com/hle8fjf", "un pin's de chasseur : http://tinyurl.com/hqy7fhq", "des buissons.",
             "100 balles et un mars."]
