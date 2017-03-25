# -*- coding: utf-8 -*-
"""
This module holds the variables and parameters.
Variables must not be changed
Some parameters can be changed. For safety reasons please contact the
developer
"""
from datetime import time
from util import utiltools

# variables
BASELINE = 0
SOL_WITHOUT = 1
SOL_AUTO = 2
SOL_VOTE = 3
SOL_AUTO_CONDITIONAL = 4
SOL_VOTE_CONDITIONAL = 5
TREATMENTS_NAMES = {BASELINE: "BASELINE", SOL_WITHOUT: "SOL_WITHOUT",
                    SOL_AUTO: "SOL_AUTO", SOL_VOTE: "SOL_VOTE",
                    SOL_AUTO_CONDITIONAL: "SOL_AUTO_CONDITIONAL",
                    SOL_VOTE_CONDITIONAL: "SOL_VOTE_CONDITIONAL"}
IN_FAVOR = 0
AGAINST = 1

# parameters
TREATMENT = BASELINE  # change from the configuration screen
TAUX_CONVERSION = 0.05
NOMBRE_PERIODES = 10
TAILLE_GROUPES = 5
MONNAIE = u"ecu"
MPCR_NORM = 0.5
MPCR_SOL = 0.25
EXPECTATIONS = True
NB_GRILLES = 5
SIZE_GRILLES = 8
NB_GRILLES_PER_LINE = 5
TIME_TO_FILL_GRILLES = time(0, 2, 0)  # hours, minutes, seconds
EFFORT_UNIT_VALUE = 2

# DECISION
DECISION_MIN = 0
DECISION_MAX = 20
DECISION_STEP = 1


def get_payoff_expectation(expectation, average_others):
    if abs(expectation - round(average_others, 0)) <= 1:
        return 1
    else:
        return 0


def get_grilles():
    return utiltools.get_grids(NB_GRILLES, SIZE_GRILLES)
