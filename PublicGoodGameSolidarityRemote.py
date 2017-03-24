# -*- coding: utf-8 -*-

import logging
import random
from twisted.internet import defer
from client.cltremote import IRemote
from client.cltgui.cltguidialogs import GuiRecapitulatif
from client.clttexts import get_payoff_text
import PublicGoodGameSolidarityParams as pms
from PublicGoodGameSolidarityGui import (GuiDecision, DVote, DQuestFinalPGGS,
                                         DExpectation, DEffort,
                                         DExpectationBefore, HISTO_WIDTH)
import PublicGoodGameSolidarityTexts as texts_PGGS


logger = logging.getLogger("le2m")


class RemotePGGS(IRemote):
    def __init__(self, le2mclt):
        IRemote.__init__(self, le2mclt)
        self._histo_vars = []
        self._currentsequence = 0
        self._sinistred = False
        self._majorityvote = pms.AGAINST
        self._payoffs = {}

    def remote_configure(self, params, currentsequence):
        logger.info(u"{} configure".format(self.le2mclt.uid))
        self._currentsequence = currentsequence
        for k, v in params.viewitems():
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
        self._majorityvote = majority_vote
        return self.le2mclt.get_remote("base").remote_display_information(
            texts_PGGS.get_text_infovote(majority_vote, self._sinistred))

    def remote_newperiod(self, periode):
        logger.info(u"{} Period {}".format(self.le2mclt.uid, periode))
        self.currentperiod = periode
        if self.currentperiod == 1:
            del self.histo[:]

    def remote_display_decision(self, max_decision):
        """
        max_decision tells us what is the endowment of the player.
        If the player is sinistred it is zero except if this is a treatment
        with efforts. In that case the endowment is equal to the effort
        times pms.EFFORT_UNIT_VALUE
        :param max_decision:
        :return:
        """
        logger.info(u"{} Decision".format(self.le2mclt.uid))
        if self.le2mclt.simulation:
            decision = \
                random.randrange(
                    pms.DECISION_MIN, max_decision + pms.DECISION_STEP,
                    pms.DECISION_STEP)
            logger.info(u"{} Send back {}".format(self.le2mclt.uid, decision))
            return decision
        else: 
            defered = defer.Deferred()
            ecran_decision = GuiDecision(
                defered, self.le2mclt.automatique,
                self.le2mclt.screen, self.currentperiod, self.histo,
                max_decision)
            ecran_decision.show()
            return defered

    def remote_display_summary(self, period_content):
        logger.info(u"{} Summary".format(self.le2mclt.uid))
        if not self.histo:
            headers, self._histo_vars = texts_PGGS.get_histo(
                self._sinistred, self._majorityvote)
            self.histo.append(headers)
        self.histo.append([period_content.get(k) for k in self._histo_vars])
        if self.le2mclt.simulation:
            return 1
        else:
            defered = defer.Deferred()
            ecran_recap = GuiRecapitulatif(
                defered, self.le2mclt.automatique, self.le2mclt.screen,
                self.currentperiod, self.histo,
                texts_PGGS.get_text_summary(period_content),
                size_histo=(HISTO_WIDTH, 120))
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

    def remote_display_expectations(self):
        """
        Display the dialog in which the subject enters his/her expectation
        :return:
        """
        logger.debug(u"{} display_expectations".format(self.le2mclt.uid))
        if self.le2mclt.simulation:
            expectation = random.randrange(
            pms.DECISION_MIN, pms.DECISION_MAX + pms.DECISION_STEP,
            pms.DECISION_STEP)
            logger.info(u"{} Send back {}".format(self.le2mclt.uid, expectation))
            return expectation
        else:
            text_expectation = texts_PGGS.get_text_expectation()
            defered = defer.Deferred()
            screen_expectation = DExpectation(
                defered, self.le2mclt.automatique, self.le2mclt.screen,
                text_expectation)
            screen_expectation.show()
            return defered

    def remote_display_expectations_vote(self, before_vote=True,
                                        expectation_before=None):
        def get_random():
            return random.randrange(
            pms.DECISION_MIN, pms.DECISION_MAX + pms.DECISION_STEP,
            pms.DECISION_STEP)

        if self.le2mclt.simulation:
            if before_vote:
                if random.randint(0, 1):
                    expectation = expectation_before
                else:
                    expectation = (get_random(), get_random())
            else:
                expectation = get_random()
            logger.info(u"{} Send back {}".format(self.le2mclt.uid, expectation))
            return expectation

        else:
            defered = defer.Deferred()
            if before_vote:
                txt = texts_PGGS.get_text_expectation_before()
                screen = DExpectationBefore(
                    defered, self.le2mclt.automatique, self.le2mclt.screen, txt)
            else:
                txt = texts_PGGS.get_text_expectation(expectation_before)
                screen = DExpectation(
                    defered, self.le2mclt.automatique, self.le2mclt.screen,
                    txt)
            screen.show()
            return defered

    def remote_display_effort(self, grilles):
        logger.debug(u"{} display_effort".format(self.le2mclt.uid))
        if self.le2mclt.simulation:
            answers = 0
            for i in range(len(grilles)):
                answers += random.randint(0, 1)  # 1 if success, 0 otherwise
            logger.info(u"{} send back {}".format(self.le2mclt.uid, answers))
            return answers
        else:
            defered = defer.Deferred()
            screen_effort = DEffort(
                defered, self.le2mclt.automatique, self.le2mclt.screen,
                grilles)
            screen_effort.show()
            return defered

    def remote_display_questfinal(self):
        logger.info(u"{} display_questfinal".format(self._le2mclt.uid))
        if self.le2mclt.simulation:
            from datetime import datetime
            inputs = {}
            today_year = datetime.now().year
            inputs['naissance'] = today_year - random.randint(16, 60)
            inputs['genre'] = random.randint(0, 1)
            inputs['nationalite'] = random.randint(1, 100)
            inputs['couple'] = random.randint(0, 1)
            inputs['etudiant'] = random.randint(0, 1)
            if inputs['etudiant'] == 0:
                inputs['etudiant_discipline'] = random.randint(1, 10)
                inputs['etudiant_niveau'] = random.randint(1, 6)
            inputs['experiences'] = random.randint(0, 1)
            inputs["fratrie_nombre"] = random.randint(0, 10)
            if inputs["fratrie_nombre"] > 0:
                inputs["fratrie_rang"] = random.randint(
                    1, inputs["fratrie_nombre"] + 1)
            else:
                inputs["fratrie_rang"] = 0
            # sportivité
            inputs["sportif"] = random.randint(0, 1)
            if inputs["sportif"] == 0:
                inputs["sportif_type"] = random.randint(0, 1)
                inputs["sportif_competition"] = random.randint(0, 1)
            # religiosité
            inputs['religion_place'] = random.randint(1, 4)
            inputs['religion_croyance'] = random.randint(1, 4)
            inputs['religion_nom'] = random.randint(1, 6)
            # additional questions
            inputs["politics"] = random.randint(1, 5)
            inputs["risk"] = random.randint(0, 10)
            inputs["inequality"] = random.randint(0, 10)
            logger.info(u"Renvoi: {}".format(inputs))
            return inputs

        else:
            defered = defer.Deferred()
            screen = DQuestFinalPGGS(defered, self.le2mclt.automatique,
                                   self.le2mclt.screen)
            screen.show()
            return defered
