# -*- coding: utf-8 -*-

import logging
from PyQt4 import QtGui, QtCore
from twisted.internet import defer
from util.utili18n import le2mtrans
from client.cltgui.cltguidialogs import GuiHistorique, DQuestFinal
from server.servgui.servguidialogs import GuiPayoffs
import PublicGoodGameSolidarityParams as pms
from client.cltgui.cltguiwidgets import WExplication, WCombo, WSpinbox, \
    WPeriod, WRadio
import PublicGoodGameSolidarityTexts as texts_PGGS

logger = logging.getLogger("le2m")


class GuiDecision(QtGui.QDialog):
    def __init__(self, defered, automatique, parent, periode, historique,
                 sinistred):
        super(GuiDecision, self).__init__(parent)

        # variables
        self._defered = defered
        self._automatique = automatique
        self._historique = GuiHistorique(self, historique, size=(700, 500))
        self._sinistred = sinistred

        layout = QtGui.QVBoxLayout(self)

        # period and history button
        wperiod = WPeriod(period=periode, ecran_historique=self._historique,
                          parent=self)
        layout.addWidget(wperiod)

        wexplanation = WExplication(
            text=texts_PGGS.get_text_explanation(), parent=self, size=(500, 60))
        layout.addWidget(wexplanation)

        max = 0 if self._sinistred else pms.DECISION_MAX
        self._wcontrib = WSpinbox(
            minimum=0, maximum=max, automatique=self._automatique, parent=self,
            label=texts_PGGS.trans_PGGS(u"How much do you invest in "
                                        u"the public account?"))
        layout.addWidget(self._wcontrib)

        buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        buttons.accepted.connect(self._accept)
        layout.addWidget(buttons)

        self.setWindowTitle(le2mtrans(u"Decision"))
        self.adjustSize()
        self.setFixedSize(self.size())

        if self._automatique:
            self._timer_automatique = QtCore.QTimer()
            self._timer_automatique.timeout.connect(
                buttons.button(QtGui.QDialogButtonBox.Ok).click)
            self._timer_automatique.start(7000)
                
    def reject(self):
        pass
    
    def _accept(self):
        try:
            self._timer_automatique.stop()
        except AttributeError:
            pass

        try:
            decision = self._wcontrib.get_value()
        except ValueError as e:
            return QtGui.QMessageBox.warning(
                self, le2mtrans(u"Warning"), e.message)

        if not self._automatique:
            if not self._sinistred:
                if not QtGui.QMessageBox.question(
                    self, le2mtrans(u"Confirmation"),
                    le2mtrans(u"Do you confirm your choice?"),
                    QtGui.QMessageBox.No | QtGui.QMessageBox.Yes) == \
                        QtGui.QMessageBox.Yes:
                    return

        logger.info(u"Send back {}".format(decision))
        self.accept()
        self._defered.callback(decision)


class DConfig(QtGui.QDialog):
    def __init__(self, parent):
        super(DConfig, self).__init__(parent)

        layout = QtGui.QVBoxLayout(self)

        self._combo_treat = WCombo(
            label=texts_PGGS.trans_PGGS(u"Treatment choice"),
            items=[v for k, v in sorted(pms.TREATMENTS.viewitems())])
        self._combo_treat.ui.comboBox.setCurrentIndex(pms.TREATMENT)
        layout.addWidget(self._combo_treat)

        buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setWindowTitle(le2mtrans(u"Configure"))
        self.adjustSize()
        self.setFixedSize(self.size())

    def get_config(self):
        return self._combo_treat.get_currentindex()


class DVote(QtGui.QDialog):
    def __init__(self, defered, automatique, parent):
        super(DVote, self).__init__(parent)

        self._defered = defered
        self._automatique = automatique

        layout = QtGui.QVBoxLayout(self)

        self._explanation = WExplication(
            parent=self, text=texts_PGGS.get_text_vote(),
            size=(450, 80))
        layout.addWidget(self._explanation)

        self._vote = WRadio(
            parent=self, automatique=self._automatique,
            label=texts_PGGS.trans_PGGS(u"Your vote"),
            texts=[v for k, v in sorted(texts_PGGS.VOTES.iteritems())])
        layout.addWidget(self._vote)

        buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        buttons.accepted.connect(self._accept)
        layout.addWidget(buttons)

        self.setWindowTitle(texts_PGGS.trans_PGGS(u"Vote"))
        self.adjustSize()
        self.setFixedSize(self.size())

        if self._automatique:
            self._timer = QtCore.QTimer()
            self._timer.timeout.connect(
                buttons.button(QtGui.QDialogButtonBox.Ok).click)
            self._timer.start(7000)

    def reject(self):
        pass

    def _accept(self):
        try:
            self._timer.stop()
        except AttributeError:
            pass

        try:
            vote = self._vote.get_checkedbutton()
        except ValueError:
            return QtGui.QMessageBox.warning(
                self, le2mtrans(u"Warning"),
                texts_PGGS.trans_PGGS(u"You must take a decision"))

        if not self._automatique:
            if QtGui.QMessageBox.question(
                self, le2mtrans(u"Confirmation"),
                le2mtrans(u"Do you confirm your choice"),
                QtGui.QMessageBox.No | QtGui.QMessageBox.Yes) != \
                QtGui.QMessageBox.Yes:
                return

        logger.info(u"Send back {}".format(vote))
        self.accept()
        self._defered.callback(vote)


class DGains(GuiPayoffs):
    def __init__(self, le2mserver, sequence):

        self._le2mserv = le2mserver
        self._sequence = sequence
        self._players = self._le2mserv.gestionnaire_joueurs.get_players(
            "PublicGoodGameSolidarity")
        self._gains = {}
        for j in self._players:
            self._gains[j.joueur] = j.sequences[sequence]["gain_euros"]
        gains_txt = [[str(k), u"{:.2f}".format(v)] for k, v in
                     sorted(self._gains.viewitems())]

        GuiPayoffs.__init__(self, le2mserver, "PublicGoodGameSolidarity",
                            gains_txt)
        self.ui.pushButton_afficher.clicked.disconnect()
        self.ui.pushButton_afficher.clicked.connect(
            lambda _: self._display_onremotes2())

    @defer.inlineCallbacks
    def _display_onremotes2(self):
        if not self._le2mserv.gestionnaire_graphique.question(
                texts_PGGS.trans_PGGS(u"Display payoff on remotes' screen?")):
            return
        self._le2mserv.gestionnaire_graphique.set_waitmode(self._players)
        yield (self._le2mserv.gestionnaire_experience.run_func(
            self._players, "display_payoffs", self._sequence))

    def _addto_finalpayoffs(self):
        if not self._gains:
            return
        if not self._le2mserv.gestionnaire_graphique.question(
            texts_PGGS.trans_PGGS(u"Add part's payoffs to final payoffs?"),
            parent=self):
                return
        for k, v in self._gains.viewitems():
            k.get_part("base").paiementFinal += float(v)
        self._le2mserv.gestionnaire_base.enregistrer()
        self._le2mserv.gestionnaire_graphique.infoserv(
            texts_PGGS.trans_PGGS(u"PGSS payoffs added to final payoffs"),
            fg="red")


class DQuestFinalPGGS(DQuestFinal):
    def __init__(self, defered, automatique, parent):
        DQuestFinal.__init__(self, defered, automatique, parent)

        politics = [v for k, v in sorted(texts_PGGS.POLITICS.viewitems())]
        politics.insert(0, le2mtrans(u"Choose"))
        politics.append(le2mtrans(u"Not in the list above"))
        self._politics = WCombo(
            parent=self, automatique=self._automatique,
            label=texts_PGGS.trans_PGGS(
                u"Politically, you feel yourself in line with"),
                items=politics)
        self._gridlayout.addWidget(self._politics, 6, 1)

        self._risk = WRadio(parent=self, automatique=self._automatique,
                            label=texts_PGGS.get_text_risk(),
                            texts=map(str, range(11)))
        self._gridlayout.addWidget(self._risk, 7, 0, 1, 3)

        self._inequality = WRadio(parent=self, automatique=self._automatique,
                            label=texts_PGGS.get_text_inequality(),
                            texts=map(str, range(11)))

        self._gridlayout.addWidget(self._inequality, 8, 0, 1, 3)

        self.setMinimumSize(0, 0)
        self.setMaximumSize(16777215, 16777215)
        self.adjustSize()
        self.setFixedSize(self.size())

    def _accept(self):
        try:
            self._timer_automatique.stop()
        except AttributeError:
            pass
        inputs = self._get_inputs()
        if type(inputs) is dict:

            try:

                inputs["politics"] = self._politics.get_currentindex()
                inputs["risk"] = self._risk.get_checkedbutton()
                inputs["inequality"] = self._inequality.get_checkedbutton()

            except ValueError:
                return QtGui.QMessageBox.warning(
                    self, le2mtrans(u"Warning"),
                    le2mtrans(u"You must answer to all the questions"))

            if not self._automatique:
                confirm = QtGui.QMessageBox.question(
                    self, le2mtrans(u"Confirmation"),
                    le2mtrans(u"Do you confirm your answers?"),
                    QtGui.QMessageBox.No | QtGui.QMessageBox.Yes)
                if confirm != QtGui.QMessageBox.Yes:
                    return

            logger.info(u"Send back: {}".format(inputs))
            self.accept()
            self._defered.callback(inputs)

        else:
            return