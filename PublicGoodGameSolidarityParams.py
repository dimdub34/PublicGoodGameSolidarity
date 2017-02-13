# -*- coding: utf-8 -*-
"""
This module holds the variables and parameters.
Variables must not be changed
Some parameters can be changed. For safety reasons please contact the
developer
"""

# variables
BASELINE = 0
SOL_WITHOUT = 1
SOL_AUTO = 2
SOL_VOTE = 3
TREATMENTS_NAMES = {BASELINE: "BASELINE", SOL_WITHOUT: "SOL_WITHOUT",
                    SOL_AUTO: "SOL_AUTO", SOL_VOTE: "SOL_VOTE"}
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

