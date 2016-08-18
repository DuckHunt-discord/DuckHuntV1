# -*- coding:Utf-8 -*-
# !/usr/bin/env python3.5
def _(string): return string  # Fake definition pour la traduction


#### MODIFIEZ A PARTIR DE CETTE LIGNE ####
token = "BOT TOKEN HERE"

admins = [138751484517941259]  # Global admins

canards_trace = ["-,_,.-'\`'°-,_,.-'\`'°", "-,..,.-'\`'°-,_,.-'\`'°", "-._..-'\`'°-,_,.-'\`'°", "-,_,.-'\`'°-,_,.-''\`"]
canards_portrait = ["\\_O<", "\\_o<", "\\_Õ<", "\\_õ<", "\\_Ô<", "\\_ô<", "\\_Ö<", "\\_ö<", "\\_Ø<", "\\_ø<", "\\_Ò<", "\\_ò<", "\\_Ó<", "\\_ó<", "\\_0<",
                    "\\_©<", "\\_@<", "\\_º<", "\\_°<", "\\_^<", "/_O<", "/_o<", "/_Õ<", "/_õ<", "/_Ô<", "/_ô<", "/_Ö<", "/_ö<", "/_Ø<", "/_ø<", "/_Ò<",
                    "/_ò<", "/_Ó<", "/_ó<", "/_0<", "/_©<", "/_@<", "/_^<", "§_O<", "§_o<", "§_Õ<", "§_õ<", "§_Ô<", "§_ô<", "§_Ö<", "§_ö<", "§_Ø<", "§_ø<",
                    "§_Ò<", "§_ò<", "§_Ó<", "§_ó<", "§_0<", "§_©<", "§_@<", "§_º<", "§_°<", "§_^<", "\\_O-", "\\_o-", "\\_Õ-", "\\_õ-", "\\_Ô-", "\\_ô-",
                    "\\_Ö-", "\\_ö-", "\\_Ø-", "\\_ø-", "\\_Ò-", "\\_ò-", "\\_Ó-", "\\_ó-", "\\_0-", "\\_©-", "\\_@-", "\\_º-", "\\_°-", "\\_^-", "/_O-",
                    "/_o-", "/_Õ-", "/_õ-", "/_Ô-", "/_ô-", "/_Ö-", "/_ö-", "/_Ø-", "/_ø-", "/_Ò-", "/_ò-", "/_Ó-", "/_ó-", "/_0-", "/_©-", "/_@-", "/_^-",
                    "§_O-", "§_o-", "§_Õ-", "§_õ-", "§_Ô-", "§_ô-", "§_Ö-", "§_ö-", "§_Ø-", "§_ø-", "§_Ò-", "§_ò-", "§_Ó-", "§_ó-", "§_0-", "§_©-", "§_@-",
                    "§_^-", "\\_O\{", "\\_o\{", "\\_Õ\{", "\\_õ\{", "\\_Ô\{", "\\_ô\{", "\\_Ö\{", "\\_ö\{", "\\_Ø\{", "\\_ø\{", "\\_Ò\{", "\\_ò\{",
                    "\\_Ó\{", "\\_ó\{", "\\_0\{", "\\_©\{", "\\_@\{", "\\_º\{", "\\_°\{", "\\_^\{", "/_O\{", "/_o\{", "/_Õ\{", "/_õ\{", "/_Ô\{", "/_ô\{",
                    "/_Ö\{", "/_ö\{", "/_Ø\{", "/_ø\{", "/_Ò\{", "/_ò\{", "/_Ó\{", "/_ó\{", "/_0\{", "/_©\{", "/_@\{", "/_^\{", "§_O\{", "§_o\{", "§_Õ\{",
                    "§_õ\{", "§_Ô\{", "§_ô\{", "§_Ö\{", "§_ö\{", "§_Ø\{", "§_ø\{", "§_Ò\{", "§_ò\{", "§_Ó\{", "§_ó\{", "§_0\{", "§_©\{", "§_@\{", "§_º\{",
                    "§_°\{", "§_^\{"]
canards_cri = ["COIN", "COIN", "COIN", "COIN", "COIN", "KWAK", "KWAK", "KWAAK", "KWAAK", "KWAAAK", "KWAAAK", "COUAK", "COUAK", "COUAAK", "COUAAK",
               "COUAAAK", "COUAAAK", "QUAK", "QUAK", "QUAAK", "QUAAK", "QUAAAK", "QUAAAK", "QUACK", "QUACK", "QUAACK", "QUAACK", "QUAAACK", "QUAAACK",
               "COUAC", "COUAC", "COUAAC", "COUAAC", "COUAAAC", "COUAAAC", "COUACK", "COUACK", "COUAACK", "COUAACK", "COUAAACK", "COUAAACK", "QWACK",
               "QWACK", "QWAACK", "QWAACK", "QWAAACK", "QWAAACK", "ARK", "ARK", "AARK", "AARK", "AAARK", "AAARK", "CUI ?", "PIOU ?", _("*sifflote*"),
               _("Hello world"), _("c'est ici pour le casting ?"), _("pourvu que personne ne me remarque..."), "http://tinyurl.com/2qc9pl",
               _("Canard un jour, canard de bain")]

canards_bye = [_("Le canard prend la fuite.  ·°'\`'°-.,¸¸.·°'\`"),
               _("Le canard va voir ailleurs.  ·°'\`'°-.,¸¸.·°'\`"),
               _("Le canard n'a pas le temps pour ça.  ·°'\`'°-.,¸¸.·°'\`"),
               _("Le canard est parti.  ·°'\`'°-.,¸¸.·°'\`"),
               _("Le canard se dissipe dans l'espace-temps.  ·°'\`'°-.,¸¸.·°'\`"),
               _("Le canard en a ras le bol d'être ignoré et fuit.  ·°'\`'°-.,¸¸.·°'\`"),
               _("Le canard ne veut pas etre canardé.  ·°'\`'°-.,¸¸.·°'\`")]

levels = [{"niveau": 0, "expMin": -999, "nom": _("danger public"), "precision": 55, "fiabilitee": 85, "balles": 6, "chargeurs": 1},
          {"niveau": 1, "expMin": -4, "nom": _("touriste"), "precision": 55, "fiabilitee": 85, "balles": 6, "chargeurs": 2},
          {"niveau": 2, "expMin": 20, "nom": _("noob"), "precision": 56, "fiabilitee": 86, "balles": 6, "chargeurs": 2},
          {"niveau": 3, "expMin": 50, "nom": _("stagiaire"), "precision": 57, "fiabilitee": 87, "balles": 6, "chargeurs": 2},
          {"niveau": 4, "expMin": 90, "nom": _("rateur de canards"), "precision": 58, "fiabilitee": 88, "balles": 6, "chargeurs": 2},
          {"niveau": 5, "expMin": 140, "nom": _("membre du Comité Contre les Canards"), "precision": 59, "fiabilitee": 89, "balles": 6, "chargeurs": 2},
          {"niveau": 6, "expMin": 200, "nom": _("détesteur de canards"), "precision": 60, "fiabilitee": 90, "balles": 4, "chargeurs": 3},
          {"niveau": 7, "expMin": 270, "nom": _("emmerdeur de canards"), "precision": 65, "fiabilitee": 93, "balles": 4, "chargeurs": 3},
          {"niveau": 8, "expMin": 350, "nom": _("déplumeur de canards"), "precision": 67, "fiabilitee": 93, "balles": 4, "chargeurs": 3},
          {"niveau": 9, "expMin": 440, "nom": _("chasseur"), "precision": 69, "fiabilitee": 93, "balles": 4, "chargeurs": 3},
          {"niveau": 10, "expMin": 540, "nom": _("retourneur de canards"), "precision": 71, "fiabilitee": 94, "balles": 4, "chargeurs": 3},
          {"niveau": 11, "expMin": 650, "nom": _("assommeur de canards"), "precision": 73, "fiabilitee": 94, "balles": 4, "chargeurs": 3},
          {"niveau": 12, "expMin": 770, "nom": _("mâchouilleur de canards"), "precision": 73, "fiabilitee": 94, "balles": 4, "chargeurs": 3},
          {"niveau": 13, "expMin": 900, "nom": _("bouffeur de canards"), "precision": 74, "fiabilitee": 95, "balles": 4, "chargeurs": 3},
          {"niveau": 14, "expMin": 1040, "nom": _("aplatisseur de canards"), "precision": 74, "fiabilitee": 95, "balles": 4, "chargeurs": 3},
          {"niveau": 15, "expMin": 1190, "nom": _("démonteur de canards"), "precision": 75, "fiabilitee": 95, "balles": 4, "chargeurs": 3},
          {"niveau": 16, "expMin": 1350, "nom": _("démolisseur de canards"), "precision": 80, "fiabilitee": 97, "balles": 2, "chargeurs": 4},
          {"niveau": 17, "expMin": 1520, "nom": _("tueur de canards"), "precision": 81, "fiabilitee": 97, "balles": 2, "chargeurs": 4},
          {"niveau": 18, "expMin": 1700, "nom": _("écorcheur de canards"), "precision": 81, "fiabilitee": 97, "balles": 2, "chargeurs": 4},
          {"niveau": 19, "expMin": 1890, "nom": _("prédateur"), "precision": 82, "fiabilitee": 97, "balles": 2, "chargeurs": 4},
          {"niveau": 20, "expMin": 2090, "nom": _("découpeur de canards"), "precision": 82, "fiabilitee": 97, "balles": 2, "chargeurs": 4},
          {"niveau": 21, "expMin": 2300, "nom": _("décortiqueur de canards"), "precision": 83, "fiabilitee": 98, "balles": 2, "chargeurs": 4},
          {"niveau": 22, "expMin": 2520, "nom": _("fraggeur de canards"), "precision": 83, "fiabilitee": 98, "balles": 2, "chargeurs": 4},
          {"niveau": 23, "expMin": 2750, "nom": _("éclateur de canards"), "precision": 84, "fiabilitee": 98, "balles": 2, "chargeurs": 4},
          {"niveau": 24, "expMin": 2990, "nom": _("défonceur de canards"), "precision": 84, "fiabilitee": 98, "balles": 2, "chargeurs": 4},
          {"niveau": 25, "expMin": 3240, "nom": _("bousilleur de canards"), "precision": 85, "fiabilitee": 98, "balles": 2, "chargeurs": 4},
          {"niveau": 26, "expMin": 3500, "nom": _("poutreur de canards"), "precision": 90, "fiabilitee": 99, "balles": 1, "chargeurs": 5},
          {"niveau": 27, "expMin": 3770, "nom": _("empaleur de canards"), "precision": 91, "fiabilitee": 99, "balles": 1, "chargeurs": 5},
          {"niveau": 28, "expMin": 4050, "nom": _("éventreur de canards"), "precision": 91, "fiabilitee": 99, "balles": 1, "chargeurs": 5},
          {"niveau": 29, "expMin": 4340, "nom": _("terreur des canards"), "precision": 92, "fiabilitee": 99, "balles": 1, "chargeurs": 5},
          {"niveau": 30, "expMin": 4640, "nom": _("exploseur de canards"), "precision": 92, "fiabilitee": 99, "balles": 1, "chargeurs": 5},
          {"niveau": 31, "expMin": 4950, "nom": _("destructeur de canards"), "precision": 93, "fiabilitee": 99, "balles": 1, "chargeurs": 5},
          {"niveau": 32, "expMin": 5270, "nom": _("pulvérisateur de canards"), "precision": 93, "fiabilitee": 99, "balles": 1, "chargeurs": 5},
          {"niveau": 33, "expMin": 5600, "nom": _("démolécularisateur de canards"), "precision": 94, "fiabilitee": 99, "balles": 1, "chargeurs": 5},
          {"niveau": 34, "expMin": 5940, "nom": _("désintégrateur de canards"), "precision": 94, "fiabilitee": 99, "balles": 1, "chargeurs": 5},
          {"niveau": 35, "expMin": 6290, "nom": _("atomiseur de canards"), "precision": 95, "fiabilitee": 99, "balles": 1, "chargeurs": 5},
          {"niveau": 36, "expMin": 6650, "nom": _("annihilateur de canards"), "precision": 95, "fiabilitee": 99, "balles": 1, "chargeurs": 5},
          {"niveau": 37, "expMin": 7020, "nom": _("serial duck killer"), "precision": 96, "fiabilitee": 99, "balles": 1, "chargeurs": 5},
          {"niveau": 38, "expMin": 7400, "nom": _("génocideur de canards"), "precision": 96, "fiabilitee": 99, "balles": 1, "chargeurs": 5},
          {
              "niveau"   : 39, "expMin": 7790, "nom": _("chômeur pour cause d'extinction de l'espèce"), "precision": 97, "fiabilitee": 99, "balles": 1,
              "chargeurs": 5
          }]
lang = "fr"  # Language specified here is for console messages, everything that is not sent to a server
defaultSettings = {
    "deleteCommands" : True, "canardsJours": 24, "findObjects": True, "duckLeaves": True, "pmMostMessages": False, "tempsAttente": 11 * 60, "lagOnBang": 1,
    "expParCanard"   : 10, "lang": lang, "randomCanard": True, "malusFauxCanards": False, "SCactif": True, "SCchance": 10, "SCviemin": 3, "SCviemax": 7,
    "duckChanceLeave": 5, "SClevelmultiplier": 0.75, "global": False, "trefleMin" : 1, "trefleMax" : 10
}

aideMsg = "https://github.com/DuckHunt-discord/DuckHunt-Discord/wiki/Aide"
inutilite = [_("un canard en peluche."), _("un canard en plastique pour le bain."), _("un canard vibrant."), _("un tas de plumes."),
             _("un chewing-gum mâchouillé."),
             _("un prospectus du CCCCC (Coalition Contre le Comité Contre les Canards)."), _("une vieille chaussure."), _("un truc à ressort."),
             _("une bouse de vache."), _("une crotte de chien."), _("un permis de chasse expiré."), _("une douille."), _("un mégot."),
             _("un préservatif usagé."),
             _("une lunette de visée cassée."), _("un détecteur infrarouge cassé."), _("un silencieux tordu."), _("une boîte vide de munitions AP."),
             _("une boîte vide de munitions explosives."), _("un trèfle à 4 feuilles auquel il en manque une."), _("un appeau cassé."),
             _("un miroir cassé."),
             _("un canard mécanique rouillé."), _("une paire de lunettes de soleil sans ses verres."), _("le béret de Donald."),
             _("une pastille de menthe à moitié fondue."), _("une boîte de nettoyant Abraxo."), _("un fusil avec le bout du canon en fleur."),
             _("un vieux couteau de chasse."), _("un vieil enregistrement vidéo : http://tinyurl.com/zbejktu"),
             _("une vieille photo de chasse : http://tinyurl.com/hmn4r88"), _("une vieille carte postale : http://tinyurl.com/hbnkpzr"),
             _("une photo de super-canard : http://tinyurl.com/hle8fjf"), _("un pin's de chasseur : http://tinyurl.com/hqy7fhq"), _("des buissons."),
             _("100 balles et un mars.")]

#### NE PLUS MODIFIER APRES CETTE LIGNE ####

del _
