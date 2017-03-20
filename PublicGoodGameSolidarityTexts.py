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

    if (treatment == pms.SOL_AUTO_CONDITIONAL and sinistred) or \
    (treatment == pms.SOL_VOTE_CONDITIONAL and vote == pms.IN_FAVOR and
     sinistred):
        histo.append(
            (trans_PGGS(u"Total in\nthe shared\ngroup account\nby your group"),
             "PGGS_groupaccountsharedsinistredsum"))

    histo.append((trans_PGGS(u"Total in\nthe group\naccount"),
                 "PGGS_groupaccountsum"))

    if (treatment == pms.SOL_AUTO and sinistred) or \
    (treatment == pms.SOL_VOTE and vote == pms.IN_FAVOR and sinistred) or \
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

    sinistred = period_content.get("PGGS_sinistred")
    vote = period_content.get("PGGS_votemajority")
    txt = u""

    if pms.TREATMENT == pms.SOL_AUTO_CONDITIONAL or \
    (pms.TREATMENT == pms.SOL_VOTE_CONDITIONAL and vote == pms.IN_FAVOR and
    sinistred):
        txt += trans_PGGS(u"You found") + u" {}. ".format(
            get_pluriel(period_content.get("PGGS_grids"), trans_PGGS(u"grid")))

    if pms.TREATMENT == pms.BASELINE or \
    pms.TREATMENT == pms.SOL_WITHOUT or \
    pms.TREATMENT == pms.SOL_AUTO or \
    pms.TREATMENT == pms.SOL_VOTE or \
    (pms.TREATMENT == pms.SOL_AUTO_CONDITIONAL and not sinistred) or \
    (pms.TREATMENT == pms.SOL_VOTE_CONDITIONAL and vote == pms.AGAINST) or \
    (pms.TREATMENT == pms.SOL_VOTE_CONDITIONAL and vote == pms.IN_FAVOR and
         not sinistred):
        txt = trans_PGGS(u"You put") + \
              u" {} ".format(get_pluriel(
                  period_content.get("PGGS_indivaccount"),
                  trans_PGGS(u"token"))) + \
              trans_PGGS(u"in your individual account and") + \
              u" {} ".format(get_pluriel(
                  period_content.get("PGGS_groupaccount"),
                  trans_PGGS(u"token"))) + \
              trans_PGGS(u"in the group account.") + u"<br />" + \
              trans_PGGS(u"Your group put a total of") + \
              u" {} ".format(get_pluriel(
                  period_content.get("PGGS_groupaccountsum"),
                  trans_PGGS(u"token"))) + \
              trans_PGGS(u"in the group account.")

    elif (pms.TREATMENT == pms.SOL_AUTO_CONDITIONAL and sinistred) or \
    (pms.TREATMENT == pms.SOL_VOTE_CONDITIONAL and vote == pms.IN_FAVOR and
     sinistred):
        txt += trans_PGGS(u"You put") + \
               u"{} ".format(get_pluriel(
                   period_content.get("PGGS_indivaccount"),
                   trans_PGGS(u"token"))) + \
               trans_PGGS(u"in your individual account and") + \
               u"{} ".format(get_pluriel(
                   period_content.get("PGGS_groupaccountshared"),
                   trans_PGGS(u"token"))) + \
               trans_PGGS(u"in the group account shared by the other group.")
        txt += u" " + trans_PGGS(u"Your group put a total of") + \
               u" {} ".format(get_pluriel(
                   period_content.get("PGGS_groupaccountsharedsinistredsum"),
                   u"token")) + trans_PGGS(u"in the group account shared by "
                                           u"the other group.")


    if pms.TREATMENT == pms.SOL_AUTO \
    or (pms.TREATMENT == pms.SOL_VOTE and vote == pms.IN_FAVOR):

        if sinistred:
            txt += trans_PGGS(u"The other group put") + u" {} ".format(
                get_pluriel(period_content.get("PGGS_groupaccountsharedsum"),
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

    elif pms.TREATMENT == pms.SOL_AUTO_CONDITIONAL or \
    (pms.TREATMENT == pms.SOL_VOTE_CONDITIONAL and vote == pms.IN_FAVOR):

        if sinistred:
            other_group_in_shared_account = \
                period_content["PGGS_groupaccountsharedsum"] - \
                period_content["PGGS_groupaccountsharedsinistredsum"]
            txt += trans_PGGS(u"The other group put") + u" {} ".format(
                   get_pluriel(other_group_in_shared_account,
                            trans_PGGS(u"token"))) + \
                   trans_PGGS(u"in its group account, shared with your group.")
            txt += trans_PGGS(u"There are therefore") + \
                   u" {} ".format(get_pluriel(
                       period_content["PGGS_groupaccountsharedsum"],
                       u"token")) + \
                   u"in the other group account shared with your group."
            txt += u"<br />" + \
                   trans_PGGS(u"Your payoff for the period is equal to") + \
                u" {} + {} + {} = {}.".format(
                    period_content.get("PGGS_indivaccountpayoff"),
                    period_content.get("PGGS_groupaccountpayoff"),
                    period_content.get("PGGS_groupaccountsharedpayoff"),
                    get_pluriel(period_content.get("PGGS_periodpayoff"),
                                pms.MONNAIE))

        else:
            other_group_in_shared_account = \
                period_content["PGGS_groupaccountsharedsum"] - \
                period_content["PGGS_groupaccountsum"]
            txt += trans_PGGS(u"The other group put") + u" {} ".format(
                   get_pluriel(other_group_in_shared_account,
                            trans_PGGS(u"token"))) + \
                   trans_PGGS(u"in your group account, shared with him.")
            txt += trans_PGGS(u"There are therefore") + \
                   u" {} ".format(get_pluriel(
                       period_content["PGGS_groupaccountsharedsum"],
                       u"token")) + \
                   u"in the your group account shared with the other."
            txt += u"<br />" + \
                   trans_PGGS(u"Your payoff for the period is equal to") + \
                u" {} + {} = {}.".format(
                    period_content.get("PGGS_indivaccountpayoff"),
                    period_content.get("PGGS_groupaccountsharedpayoff"),
                    get_pluriel(period_content.get("PGGS_periodpayoff"),
                                pms.MONNAIE))

    return txt


def get_text_expectation(expectation_before=None):
    if expectation_before is not None:
        text = (
            trans_PGGS(u"Now that you know the issue of the vote, would you "
                       u"change your expectation ({})?<br />This expectation "
                       u"will replace the expectation you did before.".format(
                expectation_before)),
            trans_PGGS(u"Your expectation")
        )
    else:
        text = (
            trans_PGGS(u"How much token(s) do you think the other members "
                       u"of your group will put, on average, in the collective "
                       u"account?"),
            trans_PGGS(u"Your expectation")
        )
    return text


def get_text_expectation_before():
    text = (
        trans_PGGS(u"How much token(s) do you expect the other members "
                   u"of your group will put, on average, in the "
                   u"collective account"),
        trans_PGGS(u"if the majority of your group "
                   u"vote in favor of the share of its collective "
                   u"account?"),
        trans_PGGS(u"if the majority of your group "
                   u"vote against the share of its collective "
                   u"account?"))
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
