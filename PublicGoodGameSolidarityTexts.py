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


def get_histo_header():
    return [
        le2mtrans(u"Period"), trans_PGGS(u"Individual\naccount"),
        trans_PGGS(u"Group\naccount"),
        trans_PGGS(u"Total in\nthe group\naccount"),
        trans_PGGS(u"Payoff\nfrom\nindividual\naccount"),
        trans_PGGS(u"Payoff\nfrom\ngroup\naccount"),
        le2mtrans(u"Period\npayoff"),
        le2mtrans(u"Cumulative\npayoff")
    ]


def get_text_sinistred(sinistred):
    txt = trans_PGGS(u"Your group") + u" {}".format(
        trans_PGGS(u"is sinistred") if sinistred else
        trans_PGGS(u"is not sinistred"))
    return txt


def get_text_vote():
    txt = trans_PGGS(u"You must vote in favour of or againts the share of the "
                     u"public account of your group with a sinistred group.")
    return txt


def get_text_explanation():
    txt = trans_PGGS(u"You must choose how much tokens you put in the public "
                     u"account.")
    return txt


def get_text_summary(period_content):
    txt = trans_PGGS(u"You put") + \
          u" {} ".format(get_pluriel(period_content.get("PGGS_indivaccount"),
                                     trans_PGGS(u"token"))) + \
        trans_PGGS(u"in your individual account and ") + \
        u" {} ".format(get_pluriel(period_content.get("PGGS_groupaccount"),
                                   trans_PGGS(u"token"))) + \
        trans_PGGS(u"in the public account.") + u"<br />" + \
        trans_PGGS(u"Your group put a total of") + \
        u" {} ".format(get_pluriel(period_content.get("PGGS_groupaccountsum"),
                                   trans_PGGS(u"token"))) + \
        trans_PGGS(u"in the public account.") + u"<br />" + \
        trans_PGGS(u"Your payoff for the period is equal to") + \
        u" {} + {} = {}.".format(period_content.get("PGGS_indivaccountpayoff"),
                               period_content.get("PGGS_groupaccountpayoff"),
                               get_pluriel(period_content.get("PGGS_periodpayoff"),
                                           pms.MONNAIE))

    if pms.TREATMENT == pms.get_treatment("sol_auto") or \
            (pms.TREATMENT == pms.get_treatment("sol_vote") and
                     period_content.get("PGGS_votemajority") == pms.IN_FAVOR):
        txt += u"<br />" + trans_PGGS(u"Each member of the sinistred "
                                      u"groups has a payoff for the period "
                                      u"equal to") + u" {}.".format(
            get_pluriel(period_content.get("PGGS_groupaccountpayoff"),
                        pms.MONNAIE))
    return txt
