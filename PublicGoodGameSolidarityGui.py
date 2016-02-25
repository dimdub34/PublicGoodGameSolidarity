# -*- coding: utf-8 -*-
"""
Gui module
"""

import logging
from PyQt4 import QtGui, QtCore
from client.cltgui.cltguidialogs import GuiHistorique
import PublicGoodGameSolidarityParams as pms
import PublicGoodGameSolidarityTexts as texts
from client.cltgui.cltguiwidgets import WExplication, WCombo, WSpinbox, WPeriod
from PublicGoodGameSolidarityTexts import _PGGS

logger = logging.getLogger("le2m")


class GuiDecision(QtGui.QDialog):
    def __init__(self, defered, automatique, parent, periode, historique,
                 sinistred):
        super(GuiDecision, self).__init__(parent)

        # variables
        self._defered = defered
        self._automatique = automatique
        self._historique = GuiHistorique(self, historique)
        self._historique.widtableview.set_size(600, 400)

        layout = QtGui.QVBoxLayout(self)

        # period and history button
        wperiod = WPeriod(period=periode, ecran_historique=self._historique,
                          parent=self)
        layout.addWidget(wperiod)

        wexplanation = WExplication(
            text=_PGGS(u"Explanation text"), parent=self, size=(450, 80))
        layout.addWidget(wexplanation)

        max = 0 if sinistred else pms.DECISION_MAX
        self._wcontrib = WSpinbox(
            minimum=0, maximum=max, automatique=self._automatique, parent=self,
            label=_PGGS(u"How much do you invest in the public account?"))
        layout.addWidget(self._wcontrib)

        buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        buttons.accepted.connect(self._accept)
        layout.addWidget(buttons)

        self.setWindowTitle(_PGGS(u"Decision"))
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
        decision = self._wcontrib.get_value()
        if not self._automatique:
            confirmation = QtGui.QMessageBox.question(
                self, texts.DECISION_confirmation.titre,
                texts.DECISION_confirmation.message,
                QtGui.QMessageBox.No | QtGui.QMessageBox.Yes)
            if confirmation != QtGui.QMessageBox.Yes: 
                return
        self.accept()
        self._defered.callback(decision)


class DConfig(QtGui.QDialog):
    def __init__(self, parent):
        super(DConfig, self).__init__(parent)

        layout = QtGui.QVBoxLayout(self)

        treats = sorted(pms.TREATMENTS.viewkeys())
        self._combo_treat = WCombo(
            label=_PGGS(u"Treatment choice"),
            items=[pms.TREATMENTS[k] for k in treats])
        self._combo_treat.ui.comboBox.setCurrentIndex(pms.TREATMENT)
        layout.addWidget(self._combo_treat)

        buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setWindowTitle(u"Configuration")
        self.adjustSize()
        self.setFixedSize(self.size())

    def get_config(self):
        return self._combo_treat.get_currentindex()
