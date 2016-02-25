# -*- coding: utf-8 -*-

from __future__ import division
import logging
from collections import OrderedDict
from twisted.internet import defer
from util import utiltools
import PublicGoodGameSolidarityParams as pms
from PublicGoodGameSolidarityTexts import _PGGS
from PublicGoodGameSolidarityGui import DConfig


logger = logging.getLogger("le2m.{}".format(__name__))


class Serveur(object):
    def __init__(self, le2mserv):
        self._le2mserv = le2mserv

        # creation of the menu (will be placed in the "part" menu on the
        # server screen)
        actions = OrderedDict()
        actions[u"Configurer"] = self._configure
        actions[u"Afficher les paramètres"] = \
            lambda _: self._le2mserv.gestionnaire_graphique. \
            display_information2(
                utiltools.get_module_info(pms), u"Paramètres")
        actions[u"Démarrer"] = lambda _: self._demarrer()
        actions[u"Afficher les gains"] = \
            lambda _: self._le2mserv.gestionnaire_experience.\
            display_payoffs_onserver("PublicGoodGameSolidarity")
        self._le2mserv.gestionnaire_graphique.add_topartmenu(
            u"Public Good Game Solidarity", actions)

    def _configure(self):
        """
        To make changes in the parameters
        :return:
        """
        screen = DConfig(self._le2mserv.gestionnaire_graphique.screen)
        if screen.exec_():
            treat = screen.get_config()
            pms.TREATMENT = treat
            self._le2mserv.gestionnaire_graphique.infoserv(
                _PGGS(u"Treatment: {}".format(pms.get_treatment(pms.TREATMENT))))


    @defer.inlineCallbacks
    def _demarrer(self):
        """
        Start the part
        :return:
        """
        # check conditions =====================================================
        if self._le2mserv.gestionnaire_joueurs.nombre_joueurs % \
                (2 * pms.TAILLE_GROUPES) != 0:
            self._le2mserv.gestionnaire_graphique.display_error(
                _PGGS(u"It is necessary to have a multiple of {} players").format(
                    2*pms.TAILLE_GROUPES))
            return

        confirmation = self._le2mserv.gestionnaire_graphique.\
            question(_PGGS(u"Start PublicGoodGameSolidarity?"))
        if not confirmation:
            return

        # init part ============================================================
        yield (self._le2mserv.gestionnaire_experience.init_part(
            "PublicGoodGameSolidarity", "PartiePGGS", "RemotePGGS", pms))
        self._tous = self._le2mserv.gestionnaire_joueurs.get_players(
            'PublicGoodGameSolidarity')

        # configure part (player and remote)
        yield (self._le2mserv.gestionnaire_experience.run_step(
            u"Configure", self._tous, "configure"))
        
        # form groups
        if pms.TAILLE_GROUPES > 0:
            try:
                self._le2mserv.gestionnaire_groupes.former_groupes(
                    self._le2mserv.gestionnaire_joueurs.get_players(),
                    pms.TAILLE_GROUPES, forcer_nouveaux=False)
            except ValueError as e:
                self._le2mserv.gestionnaire_graphique.display_error(
                    e.message)
                return

        # Sinistre =============================================================
        if pms.TREATMENT == pms.get_treatment("sol_without") or \
            pms.TREATMENT == pms.get_treatment("sol_auto") or \
            pms.TREATMENT == pms.get_treatment("sol_vote"):
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
                _PGGS(u"Not sinistred: {}").format(
                    [u"G{}".format(g.split("_")[2]) for g in
                     self._sinistred.viewkeys()]))

            self._le2mserv.gestionnaire_graphique.infoserv(
                _PGGS(u"Sinistred: {}").format(
                    [u"G{}".format(v["paired"].split("_")[2]) for v in
                     self._sinistred.viewvalues()]))

            for v in self._sinistred.viewvalues():
                for j in v["comp"]:
                    j.sinistred = False
                for j in v["paired_comp"]:
                    j.sinistred = True

            yield (self._le2mserv.gestionnaire_experience.run_step(
                _PGGS(u"Information sinistre"), self._tous,
                "display_infosinistre"))

            # vote =============================================================
            if pms.TREATMENT == pms.get_treatment("sol_vote"):
                vote_players = []
                for v in self._sinistred.viewvalues():
                    vote_players.extend(v["comp"])

                yield (self._le2mserv.gestionnaire_experience.run_step(
                    _PGGS(u"Vote"), vote_players, "display_vote"))

                for k, v in self._sinistred.viewitems():
                    votes_for = pms.TAILLE_GROUPES - \
                                sum([j.currentperiod.vote for j in v["comp"]])
                    vote_majority = pms.get_vote("pour") if \
                        votes_for > pms.TAILLE_GROUPES / 2 else \
                        pms.get_vote("contre")
                    for j in v["comp"]:
                        j.set_votes(votesfor=votes_for,
                                    votemajority=vote_majority)
                    for j in v["paired_comp"]:
                        j.set_votes(votesfor=votes_for,
                                    votemajority=vote_majority)

                    self._le2mserv.gestionnaire_graphique.infoserv(
                        u"G{}: {}".format(k.split("_")[2],
                                          pms.get_vote(vote_majority)))

        # Start ================================================================
        for period in xrange(1 if pms.NOMBRE_PERIODES else 0,
                        pms.NOMBRE_PERIODES + 1):

            if self._le2mserv.gestionnaire_experience.stop_repetitions:
                break

            # init period ------------------------------------------------------
            self._le2mserv.gestionnaire_graphique.infoserv(
                [None, _PGGS(u"Period {}").format(period)])
            self._le2mserv.gestionnaire_graphique.infoclt(
                [None, _PGGS(u"Period {}").format(period)], fg="white", bg="gray")
            yield (self._le2mserv.gestionnaire_experience.run_func(
                self._tous, "newperiod", period))

            # decision ---------------------------------------------------------
            # the decision screen is displayed on every screen, even when the
            # player cannot contribute
            yield(self._le2mserv.gestionnaire_experience.run_step(
                _PGGS(u"Decision"), self._tous, "display_decision"))

            for g, m in self._le2mserv.gestionnaire_groupes.get_groupes(
                    "PublicGoodGameSolidarity").viewitems():
                group_contrib = sum([j.currentperiod.PGGS_groupaccount for j in m])
                self._le2mserv.gestionnaire_graphique.infoserv(
                    u"G{}: {}".format(g.split("_")[2], group_contrib))
                for j in m:
                    j.currentperiod.PGGS_groupaccountsum = group_contrib

            if pms.TREATMENT == pms.get_treatment("sol_auto"):
                self._le2mserv.gestionnaire_graphique.infoserv(
                    _PGGS(u"Solidarity"))
                for v in self._sinistred.viewvalues():
                    gcontrib = v["comp"][0].currentperiod.PGGS_groupaccountsum
                    for j in v["paired_comp"]:
                        j.currentperiod.PGGS_groupaccountsum = gcontrib
                    self._le2mserv.gestionnaire_graphique.infoserv(
                        u"G{}: {}".format(v["paired"].split("_")[2], gcontrib))

            elif pms.TREATMENT == pms.get_treatment("sol_vote"):
                self._le2mserv.gestionnaire_graphique.infoserv(
                    _PGGS(u"Solidarity"))
                for v in self._sinistred.viewvalues():
                    if v["comp"][0].votemajority == pms.get_vote("pour"):
                        for j in v["paired_comp"]:
                            j.currentperiod.PGGS_groupaccountsum = \
                                v["comp"][0].currentperiod.PGGS_groupaccountsum
                        self._le2mserv.gestionnaire_graphique.infoserv(
                            u"G{}: {}".format(
                                v["paired"].split("_2")[2],
                                v["paired_comp"][0].currentperiod.PGGS_groupaccount))

            # period payoffs ---------------------------------------------------
            self._le2mserv.gestionnaire_experience.compute_periodpayoffs(
                "PublicGoodGameSolidarity")
        
            # summary ----------------------------------------------------------
            # also displayed on every screen
            yield(self._le2mserv.gestionnaire_experience.run_step(
                _PGGS(u"Summary"), self._tous, "display_summary"))
        
        # End of part ==========================================================
        yield (self._le2mserv.gestionnaire_experience.finalize_part(
            "PublicGoodGameSolidarity"))
