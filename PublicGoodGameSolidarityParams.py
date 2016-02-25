# -*- coding: utf-8 -*-
"""
This module holds the variables and parameters.
Variables must not be changed
Some parameters can be changed. For safety reasons please contact the
developer
"""

# variables
TREATMENTS = {0: "baseline", 1: "sol_without", 2: "sol_auto", 3: "sol_vote"}
IN_FAVOR = 0
AGAINST = 1

# parameters
TREATMENT = 0  # change from the configuration screen
TAUX_CONVERSION = 0.05
NOMBRE_PERIODES = 10
TAILLE_GROUPES = 5
MONNAIE = u"ecu"
MPCR_NORM = 0.5
MPCR_SOL = 0.25

# DECISION
DECISION_MIN = 0
DECISION_MAX = 20
DECISION_STEP = 1


def get_treatment(code_or_name):
    if type(code_or_name) is int:
        return TREATMENTS.get(code_or_name, None)
    elif type(code_or_name) is str:
        for k, v in TREATMENTS.viewitems():
            if v == code_or_name.lower():
                return k
    else:
        return None


def get_vote(code_or_name):
    if type(code_or_name) is int:
        return VOTES.get(code_or_name, None)
    elif type(code_or_name) is str:
        for k, v in VOTES.viewitems():
            if v == code_or_name.lower():
                return k
    else:
        return None
