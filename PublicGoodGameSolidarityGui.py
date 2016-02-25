# -*- coding: utf-8 -*-

import logging
from PyQt4 import QtGui, QtCore
from util.utili18n import le2mtrans
from client.cltgui.cltguidialogs import GuiHistorique
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
        self._historique = GuiHistorique(self, historique)

        layout = QtGui.QVBoxLayout(self)

        # period and history button
        wperiod = WPeriod(period=periode, ecran_historique=self._historique,
                          parent=self)
        layout.addWidget(wperiod)

        wexplanation = WExplication(
            text=texts_PGGS.get_text_explanation(), parent=self, size=(450, 80))
        layout.addWidget(wexplanation)

        max = 0 if sinistred else pms.DECISION_MAX
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