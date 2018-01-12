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
        self.RateSpot.clicked.connect(self.ConfirmDestination)
        self.RateSpot.clicked.connect(self.deleteRoutes)
        self.ConfirmButtonRating.clicked.connect(self.ConfirmRating)
        self.EditButtonAccount.clicked.connect(self.EditAccount)
        self.ConfirmButtonDestination.clicked.connect(self.buildNetwork)
        self.ShowRoute.clicked.connect(self.calculateRoute)

        self.logoLabel.setPixmap(QtGui.QPixmap(self.plugin_dir + '/icons/Spark.png'))

        self.graph = QgsGraph()
        self.tied_points = []

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
        print(self.HomeAddressInput.text())
        if self.YesHome.isChecked() == True:
            print(True)
        else:
            print(False)
        if self.NoHome.isChecked() == True:
            print(True)
        else:
            print(False)
        if self.SharedHome.isChecked() == True:
            print(True)
        else:
            print(False)
        self.WorkAddress = self.WorkAddressInput.text()
        print(self.WorkAddress)
        if self.YesWork.isChecked() == True:
            print(True)
        else:
            print(False)
        if self.NoWork.isChecked() == True:
            print(True)
        else:
            print(False)
        if self.SharedWork.isChecked() == True:
            print(True)
        else:
            print(False)
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
        print(self.RatingList.currentItem())
        if self.checkBoxAccessability.isChecked() == True:
            print(True)
        else:
            print(False)
        if self.checkBoxQuantity.isChecked() == True:
            print(True)
        else:
            print(False)
        if self.checkBoxLocation.isChecked() == True:
            print(True)
        else:
            print(False)
        if self.checkBoxCondition.isChecked() == True:
            print(True)
        else:
            print(False)
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


    # def buildNetwork(self):
    #     self.network_layer = self.getNetwork()
    #     if self.network_layer:
    #         # get the points to be used as origin and destination
    #         # in this case gets the centroid of the selected features
    #         selected_sources = self.getSelectedLayer().selectedFeatures()
    #         source_points = [feature.geometry().centroid().asPoint() for feature in selected_sources]
    #         # build the graph including these points
    #         if len(source_points) > 1:
    #             self.graph, self.tied_points = uf.makeUndirectedGraph(self.network_layer, source_points)
    #             # the tied points are the new source_points on the graph
    #             if self.graph and self.tied_points:
    #                 text = "network is built for %s points" % len(self.tied_points)
    #                 self.insertReport(text)
    #     return
    #
    # def calculateRoute(self):
    #     # origin and destination must be in the set of tied_points
    #     options = len(self.tied_points)
    #     if options > 1:
    #         # origin and destination are given as an index in the tied_points list
    #         origin = 0
    #         destination = random.randint(1,options-1)
    #         # calculate the shortest path for the given origin and destination
    #         path = uf.calculateRouteDijkstra(self.graph, self.tied_points, origin, destination)
    #         # store the route results in temporary layer called "Routes"
    #         routes_layer = uf.getLegendLayerByName(self.iface, "Routes")
    #         # create one if it doesn't exist
    #         if not routes_layer:
    #             attribs = ['id']
    #             types = [QtCore.QVariant.String]
    #             routes_layer = uf.createTempLayer('Routes','LINESTRING',self.network_layer.crs().postgisSrid(), attribs, types)
    #             uf.loadTempLayer(routes_layer)
    #         # insert route line
    #         for route in routes_layer.getFeatures():
    #             print route.id()
    #         uf.insertTempFeatures(routes_layer, [path], [['testing',100.00]])
    #         buffer = processing.runandload('qgis:fixeddistancebuffer',routes_layer,10.0,5,False,None)
    #         #self.refreshCanvas(routes_layer)
    #
    # def deleteRoutes(self):
    #     routes_layer = uf.getLegendLayerByName(self.iface, "Routes")
    #     if routes_layer:
    #         ids = uf.getAllFeatureIds(routes_layer)
    #         routes_layer.startEditing()
    #         for id in ids:
    #             routes_layer.deleteFeature(id)
    #         routes_layer.commitChanges()
    #
    # def getNetwork(self):
    #     roads_layer = self.getSelectedLayer()
    #     if roads_layer:
    #         # see if there is an obstacles layer to subtract roads from the network
    #         obstacles_layer = uf.getLegendLayerByName(self.iface, "Obstacles")
    #         if obstacles_layer:
    #             # retrieve roads outside obstacles (inside = False)
    #             features = uf.getFeaturesByIntersection(roads_layer, obstacles_layer, False)
    #             # add these roads to a new temporary layer
    #             road_network = uf.createTempLayer('Temp_Network','LINESTRING',roads_layer.crs().postgisSrid(),[],[])
    #             road_network.dataProvider().addFeatures(features)
    #         else:
    #             road_network = roads_layer
    #         return road_network
    #     else:
    #         return
    #
    # def getSelectedLayer(self):
    #     layer_name = self.selectLayerCombo.currentText()
    #     layer = uf.getLegendLayerByName(self.iface,layer_name)
    #     return layer


