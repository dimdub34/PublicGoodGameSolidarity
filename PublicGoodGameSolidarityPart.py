# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from twisted.internet import defer
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Float, ForeignKey, Boolean
from server.servbase import Base
from server.servparties import Partie
from util.utiltools import get_module_attributes
import PublicGoodGameSolidarityParams as pms


logger = logging.getLogger("le2m")


class PartiePGGS(Partie):
    __tablename__ = "partie_PublicGoodGameSolidarity"
    __mapper_args__ = {'polymorphic_identity': 'PublicGoodGameSolidarity'}
    partie_id = Column(Integer, ForeignKey('parties.id'), primary_key=True)
    repetitions = relationship('RepetitionsPGGS')

    def __init__(self, le2mserv, joueur):
        super(PartiePGGS, self).__init__(
            nom="PublicGoodGameSolidarity", nom_court="PGGS",
            joueur=joueur, le2mserv=le2mserv)
        self.PGGS_gain_ecus = 0
        self.PGGS_gain_euros = 0
        self._sinistred = False
        self._vote = None
        self._votesfor = None
        self._votemajority = None

    @property
    def sinistred(self):
        return self._sinistred

    @property
    def vote(self):
        return self._vote

    def set_votes(self, votesfor, votemajority):
        self._votesfor = votesfor
        self._votemajority = votemajority

    @property
    def votemajority(self):
        return self._votemajority

    @sinistred.setter
    def sinistred(self, true_or_false):
        self._sinistred = true_or_false

    @defer.inlineCallbacks
    def configure(self):
        logger.debug(u"{} Configure".format(self.joueur))
        yield (self.remote.callRemote("configure", get_module_attributes(pms)))
        self.joueur.info(u"Ok")

    @defer.inlineCallbacks
    def newperiod(self, period):
        logger.debug(u"{} New Period".format(self.joueur))
        self._currentperiod = RepetitionsPGGS(period)
        self.currentperiod.PGGS_group = self.joueur.groupe
        self.currentperiod.PGGS_sinistred = self.sinistred
        self.currentperiod.PGGS_vote = self._vote
        self.currentperiod.PGGS_voteforgroup = self._votesfor
        self.currentperiod.PGGS_votemajority = self._votemajority
        self._le2mserv.gestionnaire_base.ajouter(self.currentperiod)
        self.repetitions.append(self.currentperiod)
        yield (self.remote.callRemote("newperiod", period))
        logger.info(u"{} Ready for period {}".format(self.joueur, period))

    @defer.inlineCallbacks
    def display_infosinistre(self):
        logger.debug(u"{} info sinistre".format(self.joueur))
        yield (self.remote.callRemote("display_sinistre", self._sinistred))
        self.joueur.info(u"Ok")
        self.joueur.remove_waitmode()

    @defer.inlineCallbacks
    def display_vote(self):
        logger.debug(u"{} vote".format(self.joueur))
        self._vote = yield (self.remote.callRemote("display_vote"))
        self.joueur.info(pms.get_treatment(self._vote))

    @defer.inlineCallbacks
    def display_decision(self):
        logger.debug(u"{} Decision".format(self.joueur))
        debut = datetime.now()
        self.currentperiod.PGGS_groupaccount = yield(self.remote.callRemote(
            "display_decision"))
        self.currentperiod.PGGS_decisiontime = (datetime.now() - debut).seconds
        if not self.sinistred:
            self.currentperiod.PGGS_indivaccount = \
                pms.DECISION_MAX - self.currentperiod.PGGS_groupaccount
        else:
            self.currentperiod.PGGS_indivaccount = 0
        self.joueur.info(u"{}".format(self.currentperiod.PGGS_groupaccount))
        self.joueur.remove_waitmode()

    def compute_periodpayoff(self):
        logger.debug(u"{} Period Payoff".format(self.joueur))

        # indiv account
        self.currentperiod.PGGS_indivaccountpayoff = \
            self.currentperiod.PGGS_indivaccount * 1

        # group account
        mpcr = pms.MPCR_NORM
        if pms.TREATMENT == pms.get_treatment("sol_auto") or \
                (pms.TREATMENT == pms.get_treatment("sol_vote") and
                 self.currentperiod.PGGS_votemajority == pms.IN_FAVOR):
            mpcr = pms.MPCR_SOL
        self.currentperiod.PGGS_groupaccountpayoff = \
            self.currentperiod.PGGS_groupaccountsum * mpcr

        # period payoff
        self.currentperiod.PGGS_periodpayoff = \
            self.currentperiod.PGGS_indivaccountpayoff + \
            self.currentperiod.PGGS_groupaccountpayoff

        # cumulative payoff since the first period
        if self.currentperiod.PGGS_period < 2:
            self.currentperiod.PGGS_cumulativepayoff = \
                self.currentperiod.PGGS_periodpayoff
        else: 
            previousperiod = self.periods[self.currentperiod.PGGS_period - 1]
            self.currentperiod.PGGS_cumulativepayoff = \
                previousperiod.PGGS_cumulativepayoff + \
                self.currentperiod.PGGS_periodpayoff

        # we store the period in the self.periods dictionary
        self.periods[self.currentperiod.PGGS_period] = self.currentperiod

        logger.debug(u"{} Period Payoff {}".format(
            self.joueur, self.currentperiod.PGGS_periodpayoff))

    @defer.inlineCallbacks
    def display_summary(self):
        logger.debug(u"{} Summary".format(self.joueur))
        yield (self.remote.callRemote(
            "display_summary", self.currentperiod.todict()))
        self.joueur.info("Ok")
        self.joueur.remove_waitmode()

    @defer.inlineCallbacks
    def compute_partpayoff(self):
        logger.debug(u"{} Part Payoff".format(self.joueur))

        self.PGGS_gain_ecus = self.currentperiod.PGGS_cumulativepayoff
        self.PGGS_gain_euros = float("{:.2f}".format(
            float(self.PGGS_gain_ecus) * float(pms.TAUX_CONVERSION)))
        yield (self.remote.callRemote(
            "set_payoffs", self.PGGS_gain_euros, self.PGGS_gain_ecus))

        logger.info(u'{} Payoff ecus {} Payoff euros {:.2f}'.format(
            self.joueur, self.PGGS_gain_ecus, self.PGGS_gain_euros))


class RepetitionsPGGS(Base):
    __tablename__ = 'partie_PublicGoodGameSolidarity_repetitions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    partie_partie_id = Column(
        Integer,
        ForeignKey("partie_PublicGoodGameSolidarity.partie_id"))

    PGGS_period = Column(Integer)
    PGGS_treatment = Column(Integer)
    PGGS_group = Column(Integer)
    PGGS_sinistred = Column(Boolean)
    PGGS_vote = Column(Integer)  # 0=for, 1=against
    PGGS_voteforgroup = Column(Integer)  # nb of for
    PGGS_votemajority = Column(Integer)  # 0=for, 1=against
    PGGS_indivaccount = Column(Integer)
    PGGS_groupaccount = Column(Integer)
    PGGS_groupaccountsum = Column(Integer)
    PGGS_decisiontime = Column(Integer)
    PGGS_indivaccountpayoff= Column(Integer)
    PGGS_groupaccountpayoff = Column(Float)
    PGGS_periodpayoff = Column(Float)
    PGGS_cumulativepayoff = Column(Float)

    def __init__(self, period):
        self.PGGS_treatment = pms.TREATMENT
        self.PGGS_period = period
        self.PGGS_decisiontime = 0
        self.PGGS_periodpayoff = 0
        self.PGGS_cumulativepayoff = 0

    def todict(self, joueur=None):
        temp = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        if joueur:
            temp["joueur"] = joueur
        return temp

