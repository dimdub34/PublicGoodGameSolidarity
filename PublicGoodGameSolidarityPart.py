# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from collections import OrderedDict
from twisted.internet import defer
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Float, ForeignKey, Boolean
from server.servbase import Base
from server.servparties import Partie
from util.utili18n import le2mtrans
from util.utiltools import get_module_attributes
import PublicGoodGameSolidarityParams as pms
import PublicGoodGameSolidarityTexts as texts
from PublicGoodGameSolidarityTexts import _PGGS


logger = logging.getLogger("le2m")


class PartiePGGS(Partie):
    __tablename__ = "partie_PublicGoodGameSolidarity"
    __mapper_args__ = {'polymorphic_identity': 'PublicGoodGameSolidarity'}
    partie_id = Column(Integer, ForeignKey('parties.id'), primary_key=True)
    repetitions = relationship('RepetitionsPGGS')

    def __init__(self, le2mserv, joueur):
        super(PartiePGGS, self).__init__("PublicGoodGameSolidarity", "PGGS")
        self._le2mserv = le2mserv
        self.joueur = joueur
        self._texte_recapitulatif = u""
        self._texte_final = u""
        self.PGGS_gain_ecus = 0
        self.PGGS_gain_euros = 0
        self._histo_build = OrderedDict()
        self._histo_build[le2mtrans(u"Period")] = "PGGS_period"
        self._histo_build[_PGGS(u"Individual\naccount")] = "PGGS_indivaccount"
        self._histo_build[_PGGS(u"Group\naccount")] = "PGGS_groupaccount"
        self._histo_build[_PGGS(u"Payoff from\nindividual\naccount")] = \
            "PGGS_indivaccountpayoff"
        self._histo_build[_PGGS(u"Payoff from\ngroup\naccount")] = \
        "PGGS_groupaccountpayoff"
        self._histo_build[le2mtrans(u"Period\npayoff")] = "PGGS_periodpayoff"
        self._histo_build[le2mtrans(u"Cumulative\npayoff")] = "PGGS_cumulativepayoff"
        self._histo_content = [list(self._histo_build.viewkeys())]
        self.periods = {}
        self._currentperiod = None
        self._sinistred = False
        self._vote = None
        self._votesfor = None
        self._votemajority = None

    @property
    def currentperiod(self):
        return self._currentperiod

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
        """
        Create a new period and inform the remote
        If this is the first period then empty the historic
        :param periode:
        :return:
        """
        logger.debug(u"{} New Period".format(self.joueur))
        if period == 1:
            del self._histo_content[1:]
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
        txt = _PGGS(u"Your group {}").format(
            _PGGS(u"is sinistred") if self._sinistred else
            _PGGS(u"is not sinistred"))
        yield (self.joueur.get_part("base").remote.callRemote(
            "display_information", txt))
        self.joueur.info(u"Ok")
        self.joueur.remove_waitmode()

    @defer.inlineCallbacks
    def display_vote(self):
        logger.debug(u"{} vote".format(self.joueur))
        self._vote = yield (self.remote.callRemote("display_vote"))
        self.joueur.info(pms.get_treatment(self._vote))


    @defer.inlineCallbacks
    def display_decision(self):
        """
        Display the decision screen on the remote
        Get back the decision
        :return:
        """
        logger.debug(u"{} Decision".format(self.joueur))
        debut = datetime.now()
        self.currentperiod.PGGS_groupaccount = yield(self.remote.callRemote(
            "display_decision", self._sinistred))
        self.currentperiod.PGGS_decisiontime = (datetime.now() - debut).seconds
        if not self.sinistred:
            self.currentperiod.PGGS_indivaccount = \
                pms.DECISION_MAX - self.currentperiod.PGGS_groupaccount
        else:
            self.currentperiod.PGGS_indivaccount = 0
        self.joueur.info(u"{}".format(self.currentperiod.PGGS_groupaccount))
        self.joueur.remove_waitmode()

    def compute_periodpayoff(self):
        """
        Compute the payoff for the period
        :return:
        """
        logger.debug(u"{} Period Payoff".format(self.joueur))

        # indiv account
        self.currentperiod.PGGS_indivaccountpayoff = \
            self.currentperiod.PGGS_indivaccount * 1

        # group account
        mpcr = pms.MPCR_NORM
        if pms.TREATMENT == pms.get_treatment("sol_auto") or \
                (pms.TREATMENT == pms.get_treatment("sol_vote") and
                 self.currentperiod.PGGS_votemajority == pms.get_vote(("pour"))):
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

        # we store the period in the self.periodes dictionnary
        self.periods[self.currentperiod.PGGS_period] = self.currentperiod

        logger.debug(u"{} Period Payoff {}".format(
            self.joueur, self.currentperiod.PGGS_periodpayoff))

    @defer.inlineCallbacks
    def display_summary(self):
        """
        Create the summary (txt and historic) and then display it on the
        remote
        :param args:
        :return:
        """
        logger.debug(u"{} Summary".format(self.joueur))
        self._texte_recapitulatif = texts.get_recapitulatif(self.currentperiod)
        self._histo_content.append(
            [getattr(self.currentperiod, e) for e
             in self._histo_build.viewvalues()])
        yield(self.remote.callRemote(
            "display_summary", self._texte_recapitulatif, self._histo_content))
        self.joueur.info("Ok")
        self.joueur.remove_waitmode()
    
    def compute_partpayoff(self):
        """
        Compute the payoff of the part
        :return:
        """
        logger.debug(u"{} Part Payoff".format(self.joueur))
        # gain partie
        self.PGGS_gain_ecus = self.currentperiod.PGGS_cumulativepayoff
        self.PGGS_gain_euros = \
            float(self.PGGS_gain_ecus) * float(pms.TAUX_CONVERSION)

        # texte final
        self._texte_final = texts.get_texte_final(
            self.PGGS_gain_ecus,
            self.PGGS_gain_euros)

        logger.debug(u"{} Final text {}".format(self.joueur, self._texte_final))
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

    def todict(self, joueur):
        temp = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        temp["joueur"] = joueur
        return temp

