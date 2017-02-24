# -*- coding: utf-8 -*-

from util.utili18n import le2mtrans
from util.utiltools import get_pluriel
import PublicGoodGameSolidarityParams as pms
import os
import configuration.configparam as params
import gettext


localedir = os.path.join(
    params.getp("PARTSDIR"), "PublicGoodGameSolidarity", "locale")
trans_PGGS = gettext.translation(
  "PublicGoodGameSolidarity", localedir, languages=[params.getp("LANG")]).ugettext


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


def get_histo_header(treatment, sinistred, vote):
    h = [le2mtrans(u"Period"), trans_PGGS(u"Individual\naccount"),
         trans_PGGS(u"Group\naccount"),
         trans_PGGS(u"Total in\nthe group\naccount")]

    if (treatment == pms.SOL_AUTO and sinistred) or \
            (treatment == pms.SOL_VOTE and sinistred and
                     vote == pms.IN_FAVOR):
        h.append(trans_PGGS(u"Total in\nthe shared\ngroup account"))

    h.extend([trans_PGGS(u"Payoff\nfrom\nindividual\naccount"),
        trans_PGGS(u"Payoff\nfrom\ngroup\naccount")])

    if (treatment == pms.SOL_AUTO and sinistred) or \
            (treatment == pms.SOL_VOTE and sinistred and
                     vote == pms.IN_FAVOR):
        h.append(trans_PGGS(u"Payoff\nfrom the\nshared group\naccount"))

    h.extend([le2mtrans(u"Period\npayoff"), le2mtrans(u"Cumulative\npayoff")])
    return h


def get_text_sinistred(sinistred):
    txt = trans_PGGS(u"Your group") + u" {}".format(
        trans_PGGS(u"is sinistred") if sinistred else
        trans_PGGS(u"is not sinistred"))
    return txt


def get_text_vote():
    txt = trans_PGGS(u"You must vote in favour of or againts the share of the "
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
    text = u""
    if period == 1:
        text = trans_PGGS(u"How much token(s) do you think the other members "
                          u"of your group will put, on average, in the "
                          u"collective account?")
    elif period == pms.NOMBRE_PERIODES:
        text = trans_PGGS(u"If you had to play the game once again with the "
                          u"same group members, how much token(s) do you think "
                          u"they would put, on average, in the collective "
                          u"account?")
    return text