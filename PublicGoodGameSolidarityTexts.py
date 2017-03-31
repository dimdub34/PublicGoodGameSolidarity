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


def get_histo(sinistred, vote):
    histo = list()
    # history for BASELINE, SOL_WITHOUT, SOL_AUTO if not sinistred,
    # SOL_VOTE if vote == AGAINST, SOL_VOTE if vote=IN_FAVOR and not sinistred
    histo.append((le2mtrans(u"Period"), "PGGS_period"))
    histo.append((trans_PGGS(u"Individual\naccount"), "PGGS_indivaccount"))
    histo.append((trans_PGGS(u"Group\naccount"), "PGGS_groupaccount"))
    histo.append((trans_PGGS(u"Total in\nthe group\naccount"),
                  "PGGS_groupaccountsum"))
    histo.append((trans_PGGS(u"Payoff\nfrom\nindividual\naccount"),
                  "PGGS_indivaccountpayoff"))
    histo.append((trans_PGGS(u"Payoff\nfrom\ngroup\naccount"),
                  "PGGS_groupaccountpayoff"))
    histo.append((le2mtrans(u"Period\npayoff"), "PGGS_periodpayoff"))
    histo.append((le2mtrans(u"Cumulative\npayoff"), "PGGS_cumulativepayoff"))

    if (pms.TREATMENT == pms.SOL_AUTO and sinistred) or \
    (pms.TREATMENT == pms.SOL_VOTE and vote == pms.IN_FAVOR and sinistred) or \
                    pms.TREATMENT == pms.SOL_AUTO_CONDITIONAL or \
    (pms.TREATMENT == pms.SOL_VOTE_CONDITIONAL and vote == pms.IN_FAVOR):
        histo.insert(4, (trans_PGGS(u"Total in\nthe shared\ngroup account"),
                      "PGGS_groupaccountsharedsum"))
        histo.insert(7, (trans_PGGS(u"Payoff\nfrom the\nshared group\naccount"),
                      "PGGS_groupaccountsharedpayoff"))

    if (pms.TREATMENT == pms.SOL_AUTO_CONDITIONAL and sinistred) or \
    (pms.TREATMENT == pms.SOL_VOTE_CONDITIONAL and vote == pms.IN_FAVOR and
     sinistred):
        histo.insert(3, (trans_PGGS(u"Shared\ngroup account"),
                         "PGGS_groupaccountshared"))
        histo.insert(4, (trans_PGGS(u"Total in\nthe shared\naccount by\n"
                                   u"your group"),
                         "PGGS_groupaccountsharedsinistredsum"))

    if (pms.TREATMENT == pms.SOL_AUTO_CONDITIONAL and not sinistred) or \
    (pms.TREATMENT == pms.SOL_VOTE_CONDITIONAL and vote == pms.IN_FAVOR and
     not sinistred):
        histo.pop(6)

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
    get_token = lambda x: get_pluriel(x, trans_PGGS(u"token"))
    sentences = list()

    sentences.append(
        trans_PGGS(u"you put {} in your individual account and {} in the "
                   u"collective account. Your group put a total of "
                   u"{} in the collective account.").format(
            get_token(period_content["PGGS_indivaccount"]),
            get_token(period_content["PGGS_groupaccount"]),
            get_token(period_content["PGGS_groupaccountsum"])))
    sentences.append(
        trans_PGGS(u"Your payoff for the period is equal to {} + {} = {}.").format(
                    period_content["PGGS_indivaccountpayoff"],
                    period_content["PGGS_groupaccountpayoff"],
                    get_pluriel(period_content["PGGS_periodpayoff"],
                                pms.MONNAIE)))

    if pms.TREATMENT == pms.SOL_AUTO or \
    (pms.TREATMENT == pms.SOL_VOTE and vote == pms.IN_FAVOR):
        sentences.pop(1)
        if sinistred:
            sentences.append(
                trans_PGGS(u"The other group put {} in its collective "
                              u"account, shared with your group. Your "
                              u"payoff for the period is equal to "
                              u"{} + {} + {} = {}").format(
                get_token(period_content["PGGS_groupaccountsharedsum"]),
                period_content["PGGS_indivaccountpayoff"],
                period_content["PGGS_groupaccountpayoff"],
                period_content["PGGS_groupaccountsharedpayoff"],
                get_pluriel(period_content["PGGS_periodpayoff"],
                            pms.MONNAIE)))
        else:
            sentences.append(
                trans_PGGS(u"Each member of the sinistred group has a "
                           u"payoff for the period equal to {}. Your "
                           u"payoff for the period is equal to "
                           u"{} + {} = {}.").format(
                    get_pluriel(period_content.get("PGGS_groupaccountpayoff"),
                                pms.MONNAIE),
                    period_content["PGGS_indivaccountpayoff"],
                    period_content["PGGS_groupaccountpayoff"],
                    get_pluriel(period_content["PGGS_periodpayoff"],
                                pms.MONNAIE)))

    if pms.TREATMENT == pms.SOL_AUTO_CONDITIONAL or \
    (pms.TREATMENT == pms.SOL_VOTE_CONDITIONAL and vote == pms.IN_FAVOR):
        sentences.pop(1)
        if sinistred:
            sentences.append(
                trans_PGGS(u"You have found {} and therefore have put {} in "
                           u"the collective account shared by the other "
                           u"group. Your group put a total of {} in this "
                           u"account and the other group {}. "
                           u"There are a total of {} in this account. Your "
                           u"payoff for the period is equal to "
                           u"{} + {} + {} = {}.").format(
                    get_pluriel(period_content["PGGS_grids"], trans_PGGS(u"grid")),
                    get_token(period_content["PGGS_groupaccountshared"]),
                    get_token(period_content["PGGS_groupaccountsharedsinistredsum"]),
                    get_token(period_content["PGGS_groupaccountsharedsum"] -
                period_content["PGGS_groupaccountsharedsinistredsum"]),
                    get_token(period_content["PGGS_groupaccountsharedsum"]),
                    period_content["PGGS_indivaccountpayoff"],
                    period_content["PGGS_groupaccountpayoff"],
                    period_content["PGGS_groupaccountsharedpayoff"],
                    get_pluriel(period_content["PGGS_periodpayoff"],
                                pms.MONNAIE)))
        else:
            sentences.append(
                trans_PGGS(u"The other group put {} in the collective "
                           u"account you share you him. There are "
                           u"therefore a total of {} in this account. Each "
                           u"member of the sinistred group has a "
                           u"payoff for the period equal to {}. Your "
                           u"payoff for the period is equal to "
                           u"{} + {} = {}.").format(
                    get_token(period_content["PGGS_groupaccountsharedsum"] -
                period_content["PGGS_groupaccountsum"]),
                    get_token(period_content["PGGS_groupaccountsharedsum"]),
                    period_content["PGGS_groupaccountsharedpayoff"],
                    period_content["PGGS_indivaccountpayoff"],
                    period_content["PGGS_groupaccountsharedpayoff"],
                    get_pluriel(period_content["PGGS_periodpayoff"],
                                pms.MONNAIE)))

    return u"<br />".join(sentences)


def get_text_expectation(expectation_before=None):
    if expectation_before is not None:
        text = (
            trans_PGGS(u"Now that you know the issue of the vote, would you "
                       u"change your expectation") + u" ({})?<br />".format(
                expectation_before) + trans_PGGS(u"This expectation "
                       u"will replace the expectation you did before."),
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
    text = trans_PGGS(u"If you want to, you can contribute to the collective "
                      u"account shared by the other group, by realizing the "
                      u"tasks below. The task consists in counting the number "
                      u"of 1 in the grid. For aach grid for which you find the "
                      u"right number of 1 you put {} in the shared collective "
                      u"account.".format(pms.EFFORT_UNIT_VALUE))
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
