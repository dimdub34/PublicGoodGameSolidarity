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
        trans_PGGS(u"Payoff from\nindividual\naccount"),
        trans_PGGS(u"Payoff from\ngroup\naccount"), le2mtrans(u"Period\npayoff"),
        le2mtrans(u"Cumulative\npayoff")
    ]


def get_text_sinistred(sinistred):
    txt = trans_PGGS(u"Your group") + u" {}".format(
        trans_PGGS(u"is sinistred") if sinistred else
        trans_PGGS(u"is not sinistred"))
    return txt


def get_text_explanation():
    txt = u"Explanation text"
    return txt


def get_text_summary(period_content):
    txt = u"Summary text"
    return txt
