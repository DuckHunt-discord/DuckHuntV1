# DuckHunt-Discord
Un super bot pour discord. idée du jeu par MenzAgitat, porté selon son idée (http://scripts.eggdrop.fr/details-Duck+Hunt-s228.html)

# Qu'est-ce que c'est ?
Le but du jeu est de tuer les canards dès que vous les voyez ! C'est un peu un fps, mais pour discord :°)

# Quelles sont les commandes ?

Les commandes disponibles sont les suivantes :

## Commandes joueur:
!bang\t\tPour (tenter) de tuer le canard qui est apparu. Ne pas tirer quand il n'y a pas de canards, sinon...
!reload\t\tRecharge ou décoince votre arme
!duckstats\t\tAffiche les statistiques DuckHunt
!shop [N° ITEM] <argument>\t\tPermet d'acher des items à l'aide de points d'experience.
!top <Nombre de joueurs maxi>\t\tAffiche les meilleurs scores
!aide\t\tAffiche l'aide

Liste des items dans le shop:

N°1\t\tAjoute une balle a votre arme (7 exp)
N°2\t\tAjoute un chargeur à votre réserve (13 exp)
N°17\t\tSabote l'arme de <argument> (14 exp)
N°20\t\tAppeau : attire un canard dans les 10 prochaines minutes. (8 exp)
N°23\t\tInvoque un canard mécanique (faux canard), 75 secondes aprés la commande sur le chan (50 exp)


## Commandes admin serveur:
!claimserver\t\tVous définit comme administrateur du serveur
!addchannel\t\tAjoute la channel courante a la liste des channels ou le bot est actif
!info\t\tAffiche des informations sur le channel en cours

## Commandes admins globaux:
!giveback\t\tDonne aux joueurs leurs armes et des chargeurs, comme à minuit !
!coin\t\tFait apparaitre un canard
!nextduck\t\tEnvoie par MP le temps avant l'apparaition et la channel du prochain canard

# Comment avoir le bot sur son serveur ?

Deux moyens : 
- l'inviter et taper !claimserver, puis ajouter chacune des channels avec !addchannel. > https://discordapp.com/oauth2/authorize?&client_id=187636051135823872&scope=bot&permissions=-1
- L'héberger vous meme, ce qui vous permet d'avoir plus de contrôle sur les préférances du bot. Pour cela, il vous faut python 3.4+. 

# J'ai besoin d'aide, que faire ?

Ouvrez une issue ! 
