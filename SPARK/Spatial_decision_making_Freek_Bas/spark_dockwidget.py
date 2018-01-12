# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Spatial_decision_making_Freek_BasDockWidget
                                 A QGIS plugin
 Plugin for
                             -------------------
        begin                : 2017-12-05
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Bas van Tol Test2
        email                : bvantol3@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4 import QtGui, uic
from PyQt4.QtCore import pyqtSignal

from PyQt4 import QtGui, QtCore
from qgis.core import *
from qgis.networkanalysis import *

from pyspatialite import dbapi2 as sqlite
import psycopg2 as pgsql
import numpy as np
import math
import os.path

from . import utility_functions as uf


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'spark_dockwidget_base.ui'))


class Spatial_decision_making_Freek_BasDockWidget(QtGui.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, iface, parent=None):
        """Constructor."""
        super(Spatial_decision_making_Freek_BasDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.TabDestination.setEnabled(False)
        self.TabRating.setEnabled(False)
        self.TabAccount.setEnabled(True)
        self.EditButtonAccount.setEnabled(False)

        self.iface=iface
        self.plugin_dir = os.path.dirname(__file__)
        self.openScenario()
        #self.initCheckBoxes()
        #self.initComboBox()
        #self.initslider()

        #input
        self.ConfirmButtonAccount.clicked.connect(self.ConfirmAccount)
        self.ConfirmButtonDestination.clicked.connect(self.ConfirmDestination)
        self.ConfirmButtonRating.clicked.connect(self.ConfirmRating)
        self.EditButtonAccount.clicked.connect(self.EditAccount)

        self.logoLabel.setPixmap(QtGui.QPixmap(self.plugin_dir + '/icons/Spark.png'))





    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

#######
#   Data functions
#######
    def openScenario(self):
        scenario_file =  os.path.join(self.plugin_dir,'sample_data','start_project.qgs')
        self.iface.addProject(unicode(scenario_file))

    def ConfirmAccount(self):
        self.TabAccount.setEnabled(False)
        self.TabDestination.setEnabled(True)
        self.TabRating.setEnabled(False)
        self.EditButtonAccount.setEnabled(True)
        self.tabWidget.setCurrentIndex(1)

    def ConfirmDestination(self):
        self.TabAccount.setEnabled(False)
        self.TabDestination.setEnabled(False)
        self.TabRating.setEnabled(True)
        self.tabWidget.setCurrentIndex(2)

    def ConfirmRating(self):
        self.TabAccount.setEnabled(False)
        self.TabDestination.setEnabled(True)
        self.TabRating.setEnabled(False)
        self.tabWidget.setCurrentIndex(1)

    def EditAccount(self):
        self.TabAccount.setEnabled(True)
        self.TabDestination.setEnabled(False)
        self.TabRating.setEnabled(False)
        self.EditButtonAccount.setEnabled(False)
        self.tabWidget.setCurrentIndex(0)


    def getLayer(self, name):
        legend = self.iface.legendInterface()
        for layer in legend.layers():
            if layer.name() == name:
                return layer
        raise KeyError("layer does not exist")
