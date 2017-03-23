# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import sys
import logging
from PyQt4 import QtGui, QtCore, QtWebKit
from twisted.internet import defer
import numpy as np
from random import randint
from util.utili18n import le2mtrans
from client.cltgui.cltguidialogs import GuiHistorique, DQuestFinal
from server.servgui.servguidialogs import GuiPayoffs
import PublicGoodGameSolidarityParams as pms
from client.cltgui.cltguiwidgets import (WExplication, WCombo, WSpinbox,
                                         WPeriod, WRadio, WCompterebours)
import PublicGoodGameSolidarityTexts as texts_PGGS
from PublicGoodGameSolidarityTexts import trans_PGGS

HISTO_WIDTH = 1000


logger = logging.getLogger("le2m")


class GuiDecision(QtGui.QDialog):
    def __init__(self, defered, automatique, parent, periode, historique,
                 max_decision):
        super(GuiDecision, self).__init__(parent)

        # variables
        self._defered = defered
        self._automatique = automatique
        self._historique = GuiHistorique(self, historique,
                                         size=(HISTO_WIDTH, 500))
        self._max_decision = max_decision

        layout = QtGui.QVBoxLayout(self)

        # period and history button
        wperiod = WPeriod(period=periode, ecran_historique=self._historique,
                          parent=self)
        layout.addWidget(wperiod)

        wexplanation = WExplication(
            text=texts_PGGS.get_text_explanation(), parent=self,
            size=(HISTO_WIDTH, 60))
        layout.addWidget(wexplanation)

        self._wcontrib = WSpinbox(
            minimum=0, maximum=self._max_decision,
            automatique=self._automatique, parent=self,
            label=trans_PGGS(u"How much do you invest in "
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
            if self._max_decision > 0:
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
        self.setLayout(layout)

        form = QtGui.QFormLayout()
        layout.addLayout(form)
        
        # treatment
        self._combo_treat = QtGui.QComboBox()
        self._combo_treat.addItems(
            [v for k, v in sorted(pms.TREATMENTS_NAMES.viewitems())])
        form.addRow(QtGui.QLabel(le2mtrans(u"Treatment")), self._combo_treat)
        
        # periods
        self._spin_periods = QtGui.QSpinBox()
        self._spin_periods.setMinimum(0)
        self._spin_periods.setMaximum(100)
        self._spin_periods.setSingleStep(1)
        self._spin_periods.setButtonSymbols(QtGui.QSpinBox.NoButtons)
        self._spin_periods.setFixedWidth(50)
        self._spin_periods.setValue(pms.NOMBRE_PERIODES)
        form.addRow(QtGui.QLabel(trans_PGGS(u"Number of periods")),
                    self._spin_periods)
        
        # group size
        self._spin_group_size = QtGui.QSpinBox()
        self._spin_group_size.setMinimum(0)
        self._spin_group_size.setMaximum(100)
        self._spin_group_size.setSingleStep(1)
        self._spin_group_size.setButtonSymbols(QtGui.QSpinBox.NoButtons)
        self._spin_group_size.setFixedWidth(50)
        self._spin_group_size.setValue(pms.TAILLE_GROUPES)
        form.addRow(QtGui.QLabel(trans_PGGS(u"Group size")),
                    self._spin_group_size)
        
        # mpcr normal
        self._spin_mpcr_normal = QtGui.QDoubleSpinBox()
        self._spin_mpcr_normal.setDecimals(2)
        self._spin_mpcr_normal.setMinimum(0)
        self._spin_mpcr_normal.setMaximum(5)
        self._spin_mpcr_normal.setSingleStep(0.01)
        self._spin_mpcr_normal.setButtonSymbols(QtGui.QSpinBox.NoButtons)
        self._spin_mpcr_normal.setFixedWidth(50)
        self._spin_mpcr_normal.setValue(pms.MPCR_NORM)
        form.addRow(QtGui.QLabel(trans_PGGS(u"MPCR (normal)")),
                    self._spin_mpcr_normal)
        
        # mpcr solidarity
        self._spin_mpcr_solidarity = QtGui.QDoubleSpinBox()
        self._spin_mpcr_solidarity.setDecimals(2)
        self._spin_mpcr_solidarity.setMinimum(0)
        self._spin_mpcr_solidarity.setMaximum(5)
        self._spin_mpcr_solidarity.setSingleStep(0.01)
        self._spin_mpcr_solidarity.setButtonSymbols(QtGui.QSpinBox.NoButtons)
        self._spin_mpcr_solidarity.setFixedWidth(50)
        self._spin_mpcr_solidarity.setValue(pms.MPCR_SOL)
        form.addRow(QtGui.QLabel(trans_PGGS(u"MPCR (solidarity)")),
                    self._spin_mpcr_solidarity)

        # expectation
        self._checkbox_expectation = QtGui.QCheckBox()
        self._checkbox_expectation.setChecked(pms.EXPECTATIONS)
        form.addRow(QtGui.QLabel(trans_PGGS(u"Expectations")),
                    self._checkbox_expectation)

        # number of grid
        self._spin_nb_grilles = QtGui.QSpinBox()
        self._spin_nb_grilles.setMinimum(0)
        self._spin_nb_grilles.setMaximumWidth(100)
        self._spin_nb_grilles.setSingleStep(1)
        self._spin_nb_grilles.setButtonSymbols(QtGui.QSpinBox.NoButtons)
        self._spin_nb_grilles.setValue(pms.NB_GRILLES)
        self._spin_nb_grilles.setFixedWidth(50)
        form.addRow(QtGui.QLabel(trans_PGGS(u"Number of grids")),
                    self._spin_nb_grilles)

        # grid size
        self._spin_grilles_size = QtGui.QSpinBox()
        self._spin_grilles_size.setMinimum(0)
        self._spin_grilles_size.setMaximumWidth(100)
        self._spin_grilles_size.setSingleStep(1)
        self._spin_grilles_size.setButtonSymbols(QtGui.QSpinBox.NoButtons)
        self._spin_grilles_size.setValue(pms.SIZE_GRILLES)
        self._spin_grilles_size.setFixedWidth(50)
        form.addRow(QtGui.QLabel(trans_PGGS(u"Grid size")),
                    self._spin_grilles_size)

        buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setWindowTitle(le2mtrans(u"Configure"))
        self.adjustSize()
        self.setFixedSize(self.size())

    def _accept(self):
        pms.TREATMENT = self._combo_treat.currentIndex()
        pms.NOMBRE_PERIODES = self._spin_periods.value()
        pms.TAILLE_GROUPES = self._spin_group_size.value()
        pms.MPCR_NORM = self._spin_mpcr_normal.value()
        pms.MPCR_SOL = self._spin_mpcr_solidarity.value()
        pms.EXPECTATIONS = self._checkbox_expectation.isChecked()
        pms.NB_GRILLES = self._spin_nb_grilles.value()
        pms.SIZE_GRILLES = self._spin_grilles_size.value()
        self.accept()


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
            texts=[v for k, v in sorted(texts_PGGS.VOTES.viewitems())])
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
        confirmation = QtGui.QMessageBox.question(
            self, u"Confirmation",
            texts_PGGS.trans_PGGS(u"Display payoff on remotes' screen?"),
            QtGui.QMessageBox.No | QtGui.QMessageBox.Yes)
        if confirmation != QtGui.QMessageBox.Yes:
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


class DSequenceChoice(QtGui.QDialog):
    def __init__(self, nb_played_seq, parent):
        super(DSequenceChoice, self).__init__(parent)

        layout = QtGui.QVBoxLayout(self)

        self._choice = WSpinbox(
            minimum=1, maximum=nb_played_seq, automatique=False, parent=self,
            label=texts_PGGS.trans_PGGS(u"Choose the sequence to display"))
        layout.addWidget(self._choice)

        buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Cancel |QtGui.QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setWindowTitle(le2mtrans(u"Sequence choice"))
        self.adjustSize()
        self.setFixedSize(self.size())

    def get_choice(self):
        return self._choice.get_value()


class DExpectation(QtGui.QDialog):
    def __init__(self, defered, automatique, parent, text, expec_before=None):
        QtGui.QDialog.__init__(self, parent)

        self._defered = defered
        self._automatique = automatique

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        explanation = WExplication(text=text[0])
        layout.addWidget(explanation)

        self._spin_expectation = WSpinbox(
            parent=self, minimum=pms.DECISION_MIN, maximum=pms.DECISION_MAX,
            interval=pms.DECISION_STEP, label=text[1],
            automatique=self._automatique)
        if expec_before is not None:
            self._spin_expectation.ui.spinBox.setValue(expec_before)
        layout.addWidget(self._spin_expectation)

        button = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        button.accepted.connect(self._accept)
        layout.addWidget(button)

        self.setWindowTitle(trans_PGGS(u"Expectations"))
        self.adjustSize()
        self.setFixedSize(self.size())

        if self._automatique:
            self._timer = QtCore.QTimer()
            self._timer.timeout.connect(self._accept)
            self._timer.start(7000)

    def reject(self):
        pass

    def _accept(self):
        try:
            self._timer.stop()
        except AttributeError:
            pass
        expectation = self._spin_expectation.get_value()
        if not self._automatique:
            confirm = QtGui.QMessageBox.question(
                self, u"Confirmation", le2mtrans(u"Do you confirm your choice?"),
                QtGui.QMessageBox.No | QtGui.QMessageBox.Yes)
            if confirm != QtGui.QMessageBox.Yes:
                return
        logger.info(le2mtrans(u"Send back {}".format(expectation)))
        self.accept()
        self._defered.callback(expectation)


class DExpectationBefore(QtGui.QDialog):
    def __init__(self, defered, automatique, parent, text):
        QtGui.QDialog.__init__(self, parent)

        self._defered = defered
        self._automatique = automatique

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        explanation = WExplication(text[0])
        layout.addWidget(explanation)

        form_layout = QtGui.QFormLayout()
        layout.addLayout(form_layout)

        self._spin_expectation_favor = QtGui.QSpinBox()
        self._spin_expectation_favor.setMinimum(pms.DECISION_MIN)
        self._spin_expectation_favor.setMaximum(pms.DECISION_MAX)
        self._spin_expectation_favor.setButtonSymbols(QtGui.QSpinBox.NoButtons)
        form_layout.addRow(QtGui.QLabel(text[1]), self._spin_expectation_favor)
        
        self._spin_expectation_against = QtGui.QSpinBox()
        self._spin_expectation_against.setMinimum(pms.DECISION_MIN)
        self._spin_expectation_against.setMaximum(pms.DECISION_MAX)
        self._spin_expectation_against.setButtonSymbols(QtGui.QSpinBox.NoButtons)
        form_layout.addRow(QtGui.QLabel(text[2]), self._spin_expectation_against)

        button = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        button.accepted.connect(self._accept)
        layout.addWidget(button)

        self.setWindowTitle(trans_PGGS(u"Expectations"))
        self.adjustSize()
        self.setFixedSize(self.size())

        if self._automatique:
            self._spin_expectation_favor.setValue(randint(0, pms.DECISION_MAX))
            self._spin_expectation_against.setValue(randint(0, pms.DECISION_MAX))
            self._timer = QtCore.QTimer()
            self._timer.timeout.connect(self._accept)
            self._timer.start(7000)

    def reject(self):
        pass

    def _accept(self):
        try:
            self._timer.stop()
        except AttributeError:
            pass
        expectations = (self._spin_expectation_favor.value(),
                        self._spin_expectation_against.value())
        if not self._automatique:
            confirm = QtGui.QMessageBox.question(
                self, u"Confirmation", le2mtrans(u"Do you confirm your choice?"),
                QtGui.QMessageBox.No | QtGui.QMessageBox.Yes)
            if confirm != QtGui.QMessageBox.Yes:
                return
        logger.info(le2mtrans(u"Send back {}".format(expectations)))
        self.accept()
        self._defered.callback(expectations)


class WGrille(QtGui.QWidget):
    def __init__(self, parent, grille, automatique):
        QtGui.QWidget.__init__(self, parent)
        self._grille = grille
        self._is_ok = False

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        webview = QtWebKit.QWebView(self)
        webview.setHtml(texts_PGGS.get_grille_to_html(self._grille))
        webview.setFixedSize(160, 160)
        layout.addWidget(webview)

        form = QtGui.QFormLayout()
        layout.addLayout(form)

        self._spin_grille =QtGui.QSpinBox()
        self._spin_grille.setMinimum(0)
        self._spin_grille.setMaximum(100)
        self._spin_grille.setSingleStep(1)
        self._spin_grille.setButtonSymbols(QtGui.QSpinBox.NoButtons)
        self._spin_grille.setFixedWidth(50)
        form.addRow(QtGui.QLabel(trans_PGGS("Number of 1: ")),
                       self._spin_grille)

        self._pushButton_ok = QtGui.QPushButton("Ok")
        self._pushButton_ok.setFixedWidth(50)
        self._pushButton_ok.clicked.connect(self._check)
        self._label_result = QtGui.QLabel(trans_PGGS("?"))
        form.addRow(self._pushButton_ok, self._label_result)

        if automatique:
            if randint(0, 1):
                self._spin_grille.setValue(np.sum(self._grille))
            else:
                self._spin_grille.setValue(randint(0, pms.SIZE_GRILLES**2 + 1))
            self._pushButton_ok.click()

    def _check(self):
        answer = self._spin_grille.value()
        if answer == np.sum(self._grille):
            self._is_ok = True
            self._label_result.setText("V")
            self._label_result.setStyleSheet("color: green; font-weight: bold;")
            self._spin_grille.setEnabled(False)
            self._pushButton_ok.setEnabled(False)
        else:
            self._is_ok = False
            self._label_result.setText("X")
            self._label_result.setStyleSheet("color: red; font-weight: bold;")

    def is_ok(self):
        return self._is_ok


class DEffort(QtGui.QDialog):
    def __init__(self, defered, automatique, parent, grilles):
        QtGui.QDialog.__init__(self, parent)

        self._defered = defered
        self._automatique = automatique
        self._grilles = grilles

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        explanation = WExplication(
            parent=self, text=texts_PGGS.get_text_explanation_grilles())
        layout.addWidget(explanation)

        self._countdown = WCompterebours(
            self, temps=pms.TIME_TO_FILL_GRILLES, actionfin=self._accept)
        layout.addWidget(self._countdown)

        grid_layout = QtGui.QGridLayout()
        layout.addLayout(grid_layout)

        self._widgets_grilles = list()
        current_line = 0
        for i, g in enumerate(self._grilles):
            self._widgets_grilles.append(WGrille(self, g, self._automatique))
            grid_layout.addWidget(
                self._widgets_grilles[-1], current_line,
                i - current_line * pms.NB_GRILLES_PER_LINE)
            if i > 0 and (i+1) % pms.NB_GRILLES_PER_LINE == 0:
                current_line += 1

        buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        buttons.accepted.connect(self._accept)
        layout.addWidget(buttons)

        self.adjustSize()
        self.setFixedSize(self.size())
        self.setWindowTitle(trans_PGGS("Effort"))

    def reject(self):
        pass

    def _accept(self):
        if self._countdown.is_running():
            confirmation = QtGui.QMessageBox.question(
                self, "Confirmation", "Do you want to quit before the end of "
                                      "the timer?",
                QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Yes)
            if confirmation != QtGui.QMessageBox.Yes:
                return
            else:
                self._countdown.stop()
        answers = sum([int(g.is_ok()) for g in self._widgets_grilles])
        if not self._automatique:
            QtGui.QMessageBox.information(
                self, "Information",
                trans_PGGS("You've found {} grids.".format(answers)))
        logger.info("send back {}".format(answers))
        self.accept()
        self._defered.callback(answers)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    # grilles = pms.get_grilles()
    # screen = DEffort(None, False, None, grilles)
    text = texts_PGGS.get_text_expectation(expectation_before=5)
    # screen = DExpectationBefore(None, False, None, text)
    screen = DExpectation(None, False, None, text, 5)
    screen.show()
    sys.exit(app.exec_())