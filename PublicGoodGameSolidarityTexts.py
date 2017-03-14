# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from util.utili18n import le2mtrans
from util.utiltools import get_pluriel
import PublicGoodGameSolidarityParams as pms
import os
import configuration.configparam as params
import gettext


try:
    localedir = os.path.join(
        params.getp("PARTSDIR"), "PublicGoodGameSolidarity", "locale")
    trans_PGGS = gettext.translation(
      "PublicGoodGameSolidarity", localedir,
        languages=[params.getp("LANG")]).ugettext
except (AttributeError, IOError):
    trans_PGGS = lambda x: x


VOTES = {
    pms.IN_FAVOR: trans_PGGS(u"In favor of"),
    pms.AGAINST: trans_PGGS(u"Against")
}


POLITICS = {
    0: u"Extrême gauche",
    1: u"Gauche",
    2: u"Centre",
    3: u"Droite",
    4: u"Extrême droite"
}


def get_text_risk():
    text = u"Etes-vous généralement une personne qui " \
           u"prend des risques ou essayez-vous de les éviter?<br />" \
           u"Veuillez cocher une case sur l'échelle ci-contre, où 0 signifie " \
           u"\"peur du risque\" et 10 signifie \"prêt à prendre des risques\"."
    return text


def get_text_inequality():
    text = u"L'Etat devrait prendre des mesures pour réduire les inégalités.<br />" \
           u"Veuillez cocher une case sur l'échelle ci-contre, où 0 signifie " \
           u"\"pas du tout d'accord\" et 10 signifie \"tout à fait d'accord\"."
    return text


def get_histo(treatment, sinistred, vote):
    histo = list()
    histo.append((le2mtrans(u"Period"), "PGGS_period"))
    histo.append((trans_PGGS(u"Individual\naccount"), "PGGS_indivaccount"))
    histo.append((trans_PGGS(u"Group\naccount"), "PGGS_groupaccount"))

    if treatment == pms.SOL_AUTO_CONDITIONAL or \
    (treatment == pms.SOL_VOTE_CONDITIONAL and vote == pms.IN_FAVOR):
        histo.append((trans_PGGS(u"Group\naccount\nshared"),
                      "PGGS_groupaccountshare"))

    histo.append((trans_PGGS(u"Total in\nthe group\naccount"),
                 "PGGS_groupaccountsum"))

    if (treatment == pms.SOL_AUTO and sinistred) or \
    (treatment == pms.SOL_VOTE and sinistred and vote == pms.IN_FAVOR) or \
    treatment == pms.SOL_AUTO_CONDITIONAL or \
    (treatment == pms.SOL_VOTE_CONDITIONAL and vote == pms.IN_FAVOR):
        histo.append((trans_PGGS(u"Total in\nthe shared\ngroup account"),
                      "PGGS_groupaccountsharedsum"))

    histo.append((trans_PGGS(u"Payoff\nfrom\nindividual\naccount"),
                  "PGGS_indivaccountpayoff"))

    if treatment == pms.BASELINE or treatment == pms.SOL_WITHOUT or \
    treatment == pms.SOL_AUTO or treatment == pms.SOL_VOTE or \
    (treatment == pms.SOL_VOTE_CONDITIONAL and vote == pms.AGAINST):
        histo.append((trans_PGGS(u"Payoff\nfrom\ngroup\naccount"),
                      "PGGS_groupaccountpayoff"))

    if (treatment == pms.SOL_AUTO and sinistred) or \
    (treatment == pms.SOL_VOTE and sinistred and vote == pms.IN_FAVOR) or \
    treatment == pms.SOL_AUTO_CONDITIONAL or \
    (treatment == pms.SOL_VOTE_CONDITIONAL and vote == pms.IN_FAVOR):
        histo.append((trans_PGGS(u"Payoff\nfrom the\nshared group\naccount"),
                      "PGGS_groupaccountsharedpayoff"))

    histo.append((le2mtrans(u"Period\npayoff"), "PGGS_periodpayoff"))
    histo.append((le2mtrans(u"Cumulative\npayoff"), "PGGS_cumulativepayoff"))

    return zip(*histo)  # return the_headers, the_vars


def get_text_sinistred(sinistred):
    txt = trans_PGGS(u"Your group") + u" {}".format(
        trans_PGGS(u"is sinistred") if sinistred else
        trans_PGGS(u"is not sinistred"))
    return txt


def get_text_vote():
    txt = trans_PGGS(u"You must vote in favour of or against the share of the "
                     u"public account of your group with a sinistred group.")
    return txt


def get_text_infovote(majority_vote, sinistred):
    if not sinistred:
        txt = trans_PGGS(u"Your group has voted") + u" \"{}\" ".format(
            VOTES.get(majority_vote)) + \
              trans_PGGS(u"the share of its public account.")
    else:
        txt = trans_PGGS(u"The group has voted") + u" \"{}\" ".format(
            VOTES.get(majority_vote)) + \
              trans_PGGS(u"the share of its public account.")
    return txt


def get_text_explanation():
    txt = trans_PGGS(u"You must choose how much tokens you put in the public "
                     u"account.")
    return txt


def get_text_summary(period_content):
    # todo: change the text depending on the treatment
    txt = trans_PGGS(u"You put") + \
          u" {} ".format(get_pluriel(period_content.get("PGGS_indivaccount"),
                                     trans_PGGS(u"token"))) + \
        trans_PGGS(u"in your individual account and") + \
        u" {} ".format(get_pluriel(period_content.get("PGGS_groupaccount"),
                                   trans_PGGS(u"token"))) + \
        trans_PGGS(u"in the group account.") + u"<br />" + \
        trans_PGGS(u"Your group put a total of") + \
        u" {} ".format(get_pluriel(period_content.get("PGGS_groupaccountsum"),
                                   trans_PGGS(u"token"))) + \
        trans_PGGS(u"in the group account.")

    if period_content.get("PGGS_treatment") == pms.SOL_AUTO \
            or (period_content.get("PGGS_treatment") == pms.SOL_VOTE
                and period_content.get("PGGS_votemajority") == pms.IN_FAVOR):
        txt += u"<br />"
        if period_content.get("PGGS_sinistred"):
            txt += trans_PGGS(u"The other group put") + u" {} ".format(
                get_pluriel(period_content.get("PGGS_groupaccountshared"),
                            trans_PGGS(u"token"))) + \
                   trans_PGGS(u"in its group account, shared with your group.")
            txt += u"<br />" + \
                   trans_PGGS(u"Your payoff for the period is equal to") + \
                u" {} + {} + {} = {}.".format(
                    period_content.get("PGGS_indivaccountpayoff"),
                    period_content.get("PGGS_groupaccountpayoff"),
                    period_content.get("PGGS_groupaccountsharedpayoff"),
                    get_pluriel(period_content.get("PGGS_periodpayoff"),
                                pms.MONNAIE))
        else:
            txt += trans_PGGS(u"Each member of the sinistred groups has a "
                             u"payoff for the period equal to") + \
                  u" {}.".format(
                      get_pluriel(period_content.get("PGGS_groupaccountpayoff"),
                                  pms.MONNAIE))
            txt += u"<br />" + \
                   trans_PGGS(u"Your payoff for the period is equal to") + \
                u" {} + {} = {}.".format(
                    period_content.get("PGGS_indivaccountpayoff"),
                    period_content.get("PGGS_groupaccountpayoff"),
                    get_pluriel(period_content.get("PGGS_periodpayoff"),
                                pms.MONNAIE))
    return txt


def get_text_expectation(period):
    text = trans_PGGS(u"How much token(s) do you think the {} other members "
                      u"of your group will put, on average, in the "
                      u"collective account?".format(pms.TAILLE_GROUPES-1))
    return text


def get_text_explanation_grilles():
    text = trans_PGGS("Count the number of 1 in the following grids")
    return text


def get_grille_to_html(grille):
    html = "<table style='width: 150px;'>"
    for l in grille:
        html += "<tr>"
        for c in l:
            html += "<td style='width: 15px;'>{}</td>".format(c)
        html += "</tr>"
    html += "</table>"
    return html
