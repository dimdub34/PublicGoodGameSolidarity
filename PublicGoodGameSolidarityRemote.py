# -*- coding: utf-8 -*-

import logging
import random
from twisted.internet import defer
from client.cltremote import IRemote
from client.cltgui.cltguidialogs import GuiRecapitulatif
import PublicGoodGameSolidarityParams as pms
from PublicGoodGameSolidarityGui import GuiDecision
import PublicGoodGameSolidarityTexts as texts_PGGS


logger = logging.getLogger("le2m")


class RemotePGGS(IRemote):
    def __init__(self, le2mclt):
        IRemote.__init__(self, le2mclt)
        self._histo_vars = [
            "PGGS_period", "PGGS_indivaccount", "PGGS_groupaccount",
            "PGGS_indivaccountpayoff", "PGGS_groupaccountpayoff",
            "PGGS_periodpayoff", "PGGS_cumulativepayoff"
        ]
        self.histo.append(texts_PGGS.get_histo_header())
        self._sinistred = False

    def remote_configure(self, params):
        logger.info(u"{} configure".format(self.le2mclt.uid))
        for k, v in params.iteritems():
            setattr(pms, k, v)

    def remote_display_sinistre(self, sinistred):
        self._sinistred = sinistred
        return self.le2mclt.get_remote("base").remote_display_information(
            texts_PGGS.get_text_sinistred(sinistred))

    def remote_newperiod(self, periode):
        logger.info(u"{} Period {}".format(self.le2mclt.uid, periode))
        self.currentperiod = periode
        if self.currentperiod == 1:
            del self.histo[1:]

    def remote_display_decision(self):
        logger.info(u"{} Decision".format(self.le2mclt.uid))
        if self.le2mclt.simulation:
            max = pms.DECISION_MAX if not self._sinistred else 0
            decision = \
                random.randrange(
                    pms.DECISION_MIN, max + pms.DECISION_STEP,
                    pms.DECISION_STEP)
            logger.info(u"{} Send back {}".format(self.le2mclt.uid, decision))
            return decision
        else: 
            defered = defer.Deferred()
            ecran_decision = GuiDecision(
                defered, self.le2mclt.automatique,
                self.le2mclt.screen, self.currentperiod, self.histo,
                self._sinistred)
            ecran_decision.show()
            return defered

    def remote_display_summary(self, period_content):
        logger.info(u"{} Summary".format(self.le2mclt.uid))
        self.histo.append([period_content.get(k) for k in self._histo_vars])
        if self.le2mclt.simulation:
            return 1
        else:
            defered = defer.Deferred()
            ecran_recap = GuiRecapitulatif(
                defered, self.le2mclt.automatique, self.le2mclt.screen,
                self.currentperiod, self.histo,
                texts_PGGS.get_text_summary(period_content))
            ecran_recap.show()
            return defered
