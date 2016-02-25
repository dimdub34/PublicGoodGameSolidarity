# -*- coding: utf-8 -*-
"""
Ce module contient les textes des écrans
"""
__author__ = "Dimitri DUBOIS"


from collections import namedtuple
from util.utiltools import get_pluriel
import PublicGoodGameSolidarityParams as pms
import os
import configuration.configparam as params
import gettext
localedir = os.path.join(
    params.getp("PARTSDIR"), "PublicGoodGameSolidarity", "locale")
_PGGS = gettext.translation(
  "PublicGoodGameSolidarity", localedir, languages=[params.getp("LANG")]).ugettext


TITLE_MSG = namedtuple("TITLE_MSG", "titre message")


# ECRAN DECISION ===============================================================
DECISION_titre = u"Decision"
DECISION_explication = u"Explanation text"
DECISION_label = u"Decision label text"
DECISION_erreur = TITLE_MSG(
    u"Warning",
    u"Warning message")
DECISION_confirmation = TITLE_MSG(
    u"Confirmation",
    u"Confirmation message")


# ECRAN RECAPITULATIF ==========================================================
def get_recapitulatif(currentperiod):
    txt = u"Summary text"
    return txt


# TEXTE FINAL PARTIE ===========================================================
def get_texte_final(gain_ecus, gain_euros):
    txt = u"Vous avez gagné {gain_en_ecu}, soit {gain_en_euro}.".format(
        gain_en_ecu=get_pluriel(gain_ecus, u"ecu"),
        gain_en_euro=get_pluriel(gain_euros, u"euro")
    )
    return txt