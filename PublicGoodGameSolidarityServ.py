# -*- coding: utf-8 -*-

from __future__ import division
import logging
from collections import OrderedDict
from twisted.internet import defer
from util import utiltools
from util.utili18n import le2mtrans
import PublicGoodGameSolidarityParams as pms
import PublicGoodGameSolidarityTexts as text_PGGS
from PublicGoodGameSolidarityTexts import trans_PGGS
from PublicGoodGameSolidarityGui import DConfig, DGains, DSequenceChoice
from PyQt4 import QtGui
import random


logger = logging.getLogger("le2m.{}".format(__name__))


class Serveur(object):
    def __init__(self, le2mserv):
        self._le2mserv = le2mserv

        # creation of the menu (will be placed in the "part" menu on the
        # server screen)
        actions = OrderedDict()
        actions[le2mtrans(u"Configure")] = self._configure
        actions[le2mtrans(u"Display parameters")] = \
            lambda _: self._le2mserv.gestionnaire_graphique. \
            display_information2(
                utiltools.get_module_info(pms), le2mtrans(u"Parameters"))
        actions[le2mtrans(u"Start")] = lambda _: self._demarrer()
        actions[le2mtrans(u"Display payoffs")] = self._display_payoffs

        self._le2mserv.gestionnaire_graphique.add_topartmenu(
            u"Public Good Game Solidarity", actions)

        # final question
        self._le2mserv.gestionnaire_graphique.screen.action_finalquest.\
            triggered.disconnect()
        self._le2mserv.gestionnaire_graphique.screen.action_finalquest.\
            triggered.connect(lambda _: self._display_questfinal())

        self._currentsequence = 0

    def _configure(self):
        """
        To make changes in the parameters
        :return:
        """
        screen = DConfig(self._le2mserv.gestionnaire_graphique.screen)
        if screen.exec_():
            params = [
                le2mtrans(u"Treatment") + u": {}".format(
                    pms.TREATMENTS_NAMES[pms.TREATMENT]),
                trans_PGGS(u"Number of periods") + u": {}".format(pms.NOMBRE_PERIODES),
                trans_PGGS(u"Groups' size") + u": {}".format(pms.TAILLE_GROUPES),
                trans_PGGS(u"MPCR (normal)") + u": {}".format(pms.MPCR_NORM),
                trans_PGGS(u"MPCR (solidarity)") + u": {}".format(pms.MPCR_SOL),
                trans_PGGS(u"Expectations") + u": {}".format(pms.EXPECTATIONS)
            ]
            self._le2mserv.gestionnaire_graphique.infoserv(params)


    @defer.inlineCallbacks
    def _demarrer(self):
        """
        Start the part
        :return:
        """
        # check conditions =====================================================
        if self._le2mserv.gestionnaire_joueurs.nombre_joueurs == 0:
            self._le2mserv.gestionnaire_graphique.display_error(
                le2mtrans(u"No clients connected!"))
            return
        if pms.TREATMENT == pms.BASELINE:
            if self._le2mserv.gestionnaire_joueurs.nombre_joueurs % \
                    pms.TAILLE_GROUPES != 0:
                self._le2mserv.gestionnaire_graphique.display_error(
                    le2mtrans(u"The number of players is not compatible with "
                              u"the groups size"))
                return
        else:
            if self._le2mserv.gestionnaire_joueurs.nombre_joueurs % \
                    (2 * pms.TAILLE_GROUPES) != 0:
                self._le2mserv.gestionnaire_graphique.display_error(
                    le2mtrans(u"The number of players is not compatible with "
                              u"the groups size"))
                return

        confirmation = self._le2mserv.gestionnaire_graphique.\
            question(le2mtrans(u"Start") + u" PublicGoodGameSolidarity?")
        if not confirmation:
            return

        # init part ============================================================
        yield (self._le2mserv.gestionnaire_experience.init_part(
            "PublicGoodGameSolidarity", "PartiePGGS", "RemotePGGS", pms))
        self._tous = self._le2mserv.gestionnaire_joueurs.get_players(
            'PublicGoodGameSolidarity')

        self._currentsequence += 1
        self._le2mserv.gestionnaire_graphique.infoserv(
            trans_PGGS(u"Sequence") + u" {}".format(
                self._currentsequence))

        # configure part (player and remote)
        yield (self._le2mserv.gestionnaire_experience.run_step(
            u"Configure", self._tous, "configure", self._currentsequence))
        
        # form groups
        self._le2mserv.gestionnaire_groupes.former_groupes(
            self._le2mserv.gestionnaire_joueurs.get_players(),
            pms.TAILLE_GROUPES, forcer_nouveaux=False)

        # Sinistre =============================================================
        if pms.TREATMENT == pms.SOL_WITHOUT or \
            pms.TREATMENT == pms.SOL_AUTO or \
            pms.TREATMENT == pms.SOL_VOTE:
            groups_keys = list(self._le2mserv.gestionnaire_groupes.get_groupes(
                "PublicGoodGameSolidarity").viewkeys())

            self._sinistred = {}
            sinistred_no = groups_keys[:len(groups_keys)//2]
            sinistred_yes = groups_keys[len(groups_keys)//2:]
            logger.debug("sinistred_no: {} / sinistred_yes: {}".format(
                sinistred_no, sinistred_yes))

            for i, g in enumerate(sinistred_no):
                self._sinistred[g] = {}
                self._sinistred[g]["comp"] = [
                    j.get_part("PublicGoodGameSolidarity") for j in
                     self._le2mserv.gestionnaire_groupes.get_composition_groupe(g)]
                self._sinistred[g]["paired"] = sinistred_yes[i]
                self._sinistred[g]["paired_comp"] = [
                    j.get_part("PublicGoodGameSolidarity") for j in
                     self._le2mserv.gestionnaire_groupes.get_composition_groupe(
                         sinistred_yes[i])]

            self._le2mserv.gestionnaire_graphique.infoserv(
                trans_PGGS(u"Not sinistred") + u": {}".format(
                    [u"G{}".format(g.split("_")[2]) for g in
                     self._sinistred.viewkeys()]))

            self._le2mserv.gestionnaire_graphique.infoserv(
                trans_PGGS(u"Sinistred") + u": {}".format(
                    [u"G{}".format(v["paired"].split("_")[2]) for v in
                     self._sinistred.viewvalues()]))

            for v in self._sinistred.viewvalues():
                for j in v["comp"]:
                    j.sinistred = False
                for j in v["paired_comp"]:
                    j.sinistred = True

            yield (self._le2mserv.gestionnaire_experience.run_step(
                trans_PGGS(u"Information sinistre"), self._tous,
                "display_infosinistre"))

            # vote =============================================================
            if pms.TREATMENT == pms.SOL_VOTE:
                vote_players = []
                for v in self._sinistred.viewvalues():
                    vote_players.extend(v["comp"])

                yield (self._le2mserv.gestionnaire_experience.run_step(
                    trans_PGGS(u"Vote"), vote_players, "display_vote"))

                for k, v in self._sinistred.viewitems():
                    votes_for = pms.TAILLE_GROUPES - \
                                sum([j.vote for j in v["comp"]])
                    vote_majority = pms.IN_FAVOR if \
                        votes_for > pms.TAILLE_GROUPES / 2 else \
                        pms.AGAINST
                    for j in v["comp"]:
                        j.set_votes(votesfor=votes_for,
                                    votemajority=vote_majority)
                    for j in v["paired_comp"]:
                        j.set_votes(votesfor=votes_for,
                                    votemajority=vote_majority)

                    self._le2mserv.gestionnaire_graphique.infoserv(
                        u"G{}: {}".format(k.split("_")[2],
                                          text_PGGS.VOTES.get(vote_majority)))

                # display info vote
                yield (self._le2mserv.gestionnaire_experience.run_step(
                    trans_PGGS(u"Info vote"), self._tous,
                    "display_infovote"))

        # Start ================================================================
        for period in range(1 if pms.NOMBRE_PERIODES else 0,
                        pms.NOMBRE_PERIODES + 1):

            if self._le2mserv.gestionnaire_experience.stop_repetitions:
                break

            # init period ------------------------------------------------------
            self._le2mserv.gestionnaire_graphique.infoserv(
                [None, le2mtrans(u"Period") + u" {}".format(period)])
            self._le2mserv.gestionnaire_graphique.infoclt(
                [None, le2mtrans(u"Period") + u" {}".format(period)],
                fg="white", bg="gray")
            yield (self._le2mserv.gestionnaire_experience.run_func(
                self._tous, "newperiod", period))

            # expectation ------------------------------------------------------
            if pms.EXPECTATIONS and period == 1:
                yield (self._le2mserv.gestionnaire_experience.run_step(
                    trans_PGGS(u"Expectations"), self._tous,
                    "display_expectations"))
                for g, m in self._le2mserv.gestionnaire_groupes.get_groupes(
                        "PublicGoodGameSolidarity").viewitems():
                    group_expectation = \
                        sum([j.currentperiod.PGGS_expectation for j in m])
                    self._le2mserv.gestionnaire_graphique.infoserv(
                        u"G{}: {}".format(g.split("_")[2], group_expectation))

            # decision ---------------------------------------------------------
            # the decision screen is displayed on every screen, even when the
            # player cannot contribute
            yield(self._le2mserv.gestionnaire_experience.run_step(
                le2mtrans(u"Decision"), self._tous, "display_decision"))

            for g, m in self._le2mserv.gestionnaire_groupes.get_groupes(
                    "PublicGoodGameSolidarity").viewitems():
                group_contrib = sum([j.currentperiod.PGGS_groupaccount for j in m])
                self._le2mserv.gestionnaire_graphique.infoserv(
                    u"G{}: {}".format(g.split("_")[2], group_contrib))
                for j in m:
                    j.currentperiod.PGGS_groupaccountsum = group_contrib

            if pms.TREATMENT == pms.SOL_AUTO:
                self._le2mserv.gestionnaire_graphique.infoserv(
                    trans_PGGS(u"Solidarity"))
                for v in self._sinistred.viewvalues():
                    gcontrib = v["comp"][0].currentperiod.PGGS_groupaccountsum
                    for j in v["paired_comp"]:
                        j.currentperiod.PGGS_groupaccountshared = gcontrib
                    self._le2mserv.gestionnaire_graphique.infoserv(
                        u"G{}: {}".format(v["paired"].split("_")[2], gcontrib))

            elif pms.TREATMENT == pms.SOL_VOTE:
                self._le2mserv.gestionnaire_graphique.infoserv(
                    trans_PGGS(u"Solidarity"))
                for v in self._sinistred.viewvalues():
                    if v["comp"][0].votemajority == pms.IN_FAVOR:
                        for j in v["paired_comp"]:
                            j.currentperiod.PGGS_groupaccountshared = \
                                v["comp"][0].currentperiod.PGGS_groupaccountsum
                        self._le2mserv.gestionnaire_graphique.infoserv(
                            u"G{}: {}".format(
                                v["paired"].split("_")[2],
                                v["paired_comp"][0].currentperiod.
                                    PGGS_groupaccountshared))
                    else:
                        for j in v["paired_comp"]:
                            j.currentperiod.PGGS_groupaccountsum = 0
                        self._le2mserv.gestionnaire_graphique.infoserv(
                            u"G{}: {}".format(
                                v["paired"].split("_")[2],
                                v["paired_comp"][0].currentperiod.
                                    PGGS_groupaccountshared))

            # period payoffs ---------------------------------------------------
            self._le2mserv.gestionnaire_experience.compute_periodpayoffs(
                "PublicGoodGameSolidarity")
        
            # summary ----------------------------------------------------------
            # also displayed on every screen
            yield(self._le2mserv.gestionnaire_experience.run_step(
                le2mtrans(u"Summary"), self._tous, "display_summary"))
        
        # End of part ==========================================================
        if pms.EXPECTATIONS and self._currentsequence == 1:
            yield (self._le2mserv.gestionnaire_experience.run_step(
                trans_PGGS(u"Expectations"), self._tous,
                "display_expectations"))
            for g, m in self._le2mserv.gestionnaire_groupes.get_groupes(
                    "PublicGoodGameSolidarity").viewitems():
                group_expectation = \
                    sum([j.currentperiod.PGGS_expectation for j in m])
                self._le2mserv.gestionnaire_graphique.infoserv(
                    u"G{}: {}".format(g.split("_")[2], group_expectation))
        yield (self._le2mserv.gestionnaire_experience.finalize_part(
            "PublicGoodGameSolidarity"))

    def _display_payoffs(self):
        if self._currentsequence >= 0:
            screen = DSequenceChoice(
                self._currentsequence,
                self._le2mserv.gestionnaire_graphique.screen)
            if screen.exec_():
                sequence = screen.get_choice()
                self._ecran_gains = DGains(self._le2mserv, sequence)
                self._ecran_gains.show()
        else:  # no sequence has been run
            return

    @defer.inlineCallbacks
    def _display_questfinal(self):
        if not self._le2mserv.gestionnaire_base.is_created():
            QtGui.QMessageBox.warning(
                self._le2mserv.gestionnaire_graphique.screen,
                le2mtrans(u"Warning"),
                le2mtrans(u"There is no database yet. You first need to "
                          u"load at least one part."))
            return
        if not hasattr(self, "_tous"):
            QtGui.QMessageBox.warning(
                self._le2mserv.gestionnaire_graphique.screen,
                le2mtrans(u"Warning"),
                trans_PGGS(u"PGGS has to be run before to "
                         u"start this questionnaire"))
            return

        confirmation = QtGui.QMessageBox.question(
            self._le2mserv.gestionnaire_graphique.screen,
            le2mtrans(u"Confirmation"),
            le2mtrans(u"Start the final questionnaire?"),
            QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok)
        if confirmation != QtGui.QMessageBox.Ok:
            return

        yield (self._le2mserv.gestionnaire_experience.run_step(
            trans_PGGS(u"Final questionnaire"), self._tous,
            "display_questfinal"))
