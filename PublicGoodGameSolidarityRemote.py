# -*- coding: utf-8 -*-

import logging
import random
from twisted.internet import defer
from client.cltremote import IRemote
from client.cltgui.cltguidialogs import GuiRecapitulatif
from client.clttexts import get_payoff_text
import PublicGoodGameSolidarityParams as pms
from PublicGoodGameSolidarityGui import GuiDecision, DVote
import PublicGoodGameSolidarityTexts as texts_PGGS
from PyQt4 import QtGui


logger = logging.getLogger("le2m")


class RemotePGGS(IRemote):
    def __init__(self, le2mclt):
        IRemote.__init__(self, le2mclt)
        self._histo_vars = [
            "PGGS_period", "PGGS_indivaccount", "PGGS_groupaccount",
            "PGGS_groupaccountsum", "PGGS_indivaccountpayoff",
            "PGGS_groupaccountpayoff", "PGGS_periodpayoff",
            "PGGS_cumulativepayoff"
        ]
        self.histo.append(texts_PGGS.get_histo_header())
        self._currentsequence = 0
        self._sinistred = False
        self._payoffs = {}

    def remote_configure(self, params, currentsequence):
        logger.info(u"{} configure".format(self.le2mclt.uid))
        self._currentsequence = currentsequence
        for k, v in params.iteritems():
            setattr(pms, k, v)

    def remote_display_sinistre(self, sinistred):
        logger.info(u"{} display_sinistre".format(self.le2mclt.uid))
        self._sinistred = sinistred
        return self.le2mclt.get_remote("base").remote_display_information(
            texts_PGGS.get_text_sinistred(sinistred))

    def remote_display_vote(self):
        logger.info(u"{} display_vote".format(self.le2mclt.uid))
        if self.le2mclt.simulation:
            dec = random.randint(0, 1)
            logger.info(u"Send back {}".format(dec))
            return dec
        else:
            defered = defer.Deferred()
            screen = DVote(
                parent=self.le2mclt.screen, defered=defered,
                automatique=self.le2mclt.automatique)
            screen.show()
            return defered

    def remote_display_infovote(self, majority_vote):
        logger.info(u"{} info vote".format(self.le2mclt.uid))
        return self.le2mclt.get_remote("base").remote_display_information(
            texts_PGGS.get_text_infovote(majority_vote, self._sinistred))

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
                texts_PGGS.get_text_summary(period_content),
                size_histo=(650, 100))
            ecran_recap.show()
            return defered

    def remote_set_payoffs(self, in_euros, in_ecus=None):
        logger.info(u"{} set_payoffs".format(self.le2mclt.uid))
        self._payoff_euros = in_euros
        self._payoff_ecus = in_ecus
        self._payoff_text = get_payoff_text(self.payoff_euros, self.payoff_ecus)
        self._payoffs[self._currentsequence] = {
            "euros": self.payoff_euros, "ecus": self.payoff_ecus,
            "txt": self.payoff_text}

    def remote_display_payoffs_PGGS(self, sequence):
        logger.info(u"{} display_payoffs".format(self.le2mclt.uid))
        return self.le2mclt.get_remote("base").remote_display_information(
            self._payoffs[sequence]["txt"])
