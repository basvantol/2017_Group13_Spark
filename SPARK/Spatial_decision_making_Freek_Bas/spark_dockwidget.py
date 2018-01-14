# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Spatial_decision_making_Freek_BasDockWidget
                                 A QGIS plugin
 Plugin for
                             -------------------
        begin                : 2017-12-05
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Bas van Tol & Freek Akkermans
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

from PyQt4 import QtGui, QtCore, uic
from qgis.core import *
from qgis.networkanalysis import *
from qgis.gui import *
import processing

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

    def __init__(self, iface,  parent=None):
        """Constructor."""
        super(Spatial_decision_making_Freek_BasDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.TabLogin.setEnabled(True)
        self.TabDestination.setEnabled(False)
        self.TabRating.setEnabled(False)
        self.TabAccount.setEnabled(False)
        self.EditButtonAccount.setEnabled(False)

        self.iface=iface
        self.canvas = self.iface.mapCanvas()
        self.plugin_dir = os.path.dirname(__file__)
        self.openScenario()
        self.startingPoint = 0
        self.destinationPoint = 0

        self.layers_dic = self.getLayers()

        #clicking
        self.emitStartPoint = QgsMapToolEmitPoint(self.canvas)
        self.SelectStart.clicked.connect(self.enterStartPoi)
        self.emitStartPoint.canvasClicked.connect(self.getStartPoint)

        self.emitDestinationPoint = QgsMapToolEmitPoint(self.canvas)
        self.SelectDestination.clicked.connect(self.enterDestinationPoi)
        self.emitDestinationPoint.canvasClicked.connect(self.getDestinationPoint)



        #input
        self.LoginButton.clicked.connect(self.LoginAccount)
        self.RegisterButton.clicked.connect(self.RegisterAccount)
        self.ConfirmButtonAccount.clicked.connect(self.ConfirmAccount)
        self.RateSpot.clicked.connect(self.goToRate)
        self.ConfirmButtonRating.clicked.connect(self.ConfirmRating)
        self.EditButtonAccount.clicked.connect(self.EditAccount)

        self.ShowRoute.clicked.connect(self.buildNetwork)
        self.ShowRoute.clicked.connect(self.calculateRoute)

        self.logoLabel.setPixmap(QtGui.QPixmap(self.plugin_dir + '/icons/Spark.png'))
        self.logoLabel_2.setPixmap(QtGui.QPixmap(self.plugin_dir + '/icons/Spark.png'))
        self.logoLabel_3.setPixmap(QtGui.QPixmap(self.plugin_dir + '/icons/Spark.png'))
        self.logoLabel_4.setPixmap(QtGui.QPixmap(self.plugin_dir + '/icons/Spark.png'))

        self.graph = QgsGraph()
        self.tied_points = []

        self.LogList = []
        self.RatingList = []

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

#######
#   Data functions
#######
    def openScenario(self):
        scenario_file =  os.path.join(self.plugin_dir,'sample_data','start_project.qgs')
        self.iface.addProject(unicode(scenario_file))

    def getLayers(self):
        layers = uf.getLegendLayers(self.iface, 'all', 'all')
        if layers:
            layer_names = uf.getLayersListNames(layers)
        layers_dict = dict()
        layers_dict['route'] = layer_names[0]
        layers_dict['park'] = layer_names[1]
        layers_dict['neighborhood'] = layer_names[2]
        layers_dict['roads'] = layer_names[3]
        layers_dict['rating'] = layer_names[4]
        layers_dict['account'] = layer_names[5]
        return layers_dict

    def LoginAccount(self):
        self.TabLogin.setEnabled(False)
        self.TabAccount.setEnabled(False)
        self.TabDestination.setEnabled(True)
        self.TabRating.setEnabled(False)
        self.EditButtonAccount.setEnabled(True)
        self.tabWidget.setCurrentIndex(2)
        self.SelectStart.setEnabled(True)
        self.SelectDestination.setEnabled(False)
        self.ShowRoute.setEnabled(False)
        self.RateSpot.setEnabled(False)
        self.RegisterButton.setEnabled(False)
        self.LoginButton.setEnabled(False)

    def RegisterAccount(self):
        self.TabAccount.setEnabled(True)
        self.TabDestination.setEnabled(False)
        self.EditButtonAccount.setEnabled(False)
        self.tabWidget.setCurrentIndex(1)


    def ConfirmAccount(self):
        self.LogList = []
        self.LogList.append(self.HomeAddressInput.text())
        if self.YesHome.isChecked() == True:
            self.LogList.append("Yes")
        if self.NoHome.isChecked() == True:
            self.LogList.append("No")
        if self.SharedHome.isChecked() == True:
            self.LogList.append("Shared")
        self.LogList.append(self.WorkAddressInput.text())
        if self.YesWork.isChecked() == True:
            self.LogList.append("Yes")
        if self.NoWork.isChecked() == True:
            self.LogList.append("No")
        if self.SharedWork.isChecked() == True:
            self.LogList.append("Shared")
        self.LogList.append(self.NameInput.text())
        self.TabAccount.setEnabled(False)
        self.TabDestination.setEnabled(True)
        self.TabRating.setEnabled(False)
        self.EditButtonAccount.setEnabled(True)
        self.tabWidget.setCurrentIndex(2)
        self.SelectStart.setEnabled(True)
        self.SelectDestination.setEnabled(False)
        self.ShowRoute.setEnabled(False)
        self.RateSpot.setEnabled(False)

        uf.insertTempFeatures(uf.getLegendLayerByName(self.iface, "account layer"), [QgsPoint(0,0)], [self.LogList])


    def goToRate(self):
        self.TabAccount.setEnabled(False)
        self.TabDestination.setEnabled(False)
        self.TabRating.setEnabled(True)
        self.tabWidget.setCurrentIndex(3)
        self.RateSpot.setEnabled(False)


    def ConfirmRating(self):
        self.RatingList = []

        if self.ratingbutton1.isChecked() == True:
            self.RatingList.append(1)
        if self.ratingbutton2.isChecked() == True:
            self.RatingList.append(2)
        if self.ratingbutton3.isChecked() == True:
            self.RatingList.append(3)
        if self.ratingbutton4.isChecked() == True:
            self.RatingList.append(4)
        if self.ratingbutton5.isChecked() == True:
            self.RatingList.append(5)

        if self.checkBoxAccessability.isChecked() == True:
            self.RatingList.append(True)
        else:
            self.RatingList.append(False)
        if self.checkBoxQuantity.isChecked() == True:
            self.RatingList.append(True)
        else:
            self.RatingList.append(False)
        if self.checkBoxLocation.isChecked() == True:
            self.RatingList.append(True)
        else:
            self.RatingList.append(False)
        if self.checkBoxCondition.isChecked() == True:
            self.RatingList.append(True)
        else:
            self.RatingList.append(False)
        self.RatingList.append(self.NameInput.text() + self.LoginNameInput.text())
        self.TabAccount.setEnabled(False)
        self.TabDestination.setEnabled(True)
        self.TabRating.setEnabled(False)
        self.tabWidget.setCurrentIndex(2)
        self.SelectStart.setEnabled(True)

        uf.insertTempFeatures(uf.getLegendLayerByName(self.iface, "rating layer"), [self.destinationPoint], [self.RatingList])

    def EditAccount(self):
        self.TabAccount.setEnabled(True)
        self.TabDestination.setEnabled(False)
        self.TabRating.setEnabled(False)
        self.EditButtonAccount.setEnabled(False)
        self.tabWidget.setCurrentIndex(1)

    def enterStartPoi(self):
        # remember currently selected tool
        self.userTool = self.canvas.mapTool()
        # activate coordinate capture tool
        self.canvas.setMapTool(self.emitStartPoint)

    def getStartPoint(self, mapPoint, mouseButton):
        # change tool so you don't get more than one POI
        self.canvas.unsetMapTool(self.emitStartPoint)
        self.canvas.setMapTool(self.userTool)
        #Get the click
        if mapPoint:
            self.startingPoint = QgsPoint(mapPoint.x(), mapPoint.y())
            # here do something with the point
        self.SelectDestination.setEnabled(True)
        self.SelectStart.setEnabled(False)

    def enterDestinationPoi(self):
        # remember currently selected tool
        self.userTool = self.canvas.mapTool()
        # activate coordinate capture tool
        self.canvas.setMapTool(self.emitDestinationPoint)

    def getDestinationPoint(self, mapPoint, mouseButton):
        # change tool so you don't get more than one POI
        self.canvas.unsetMapTool(self.emitDestinationPoint)
        self.canvas.setMapTool(self.userTool)
        #Get the click
        if mapPoint:
            self.destinationPoint = QgsPoint(mapPoint.x(), mapPoint.y())
            # here do something with the point
        self.ShowRoute.setEnabled(True)
        self.SelectDestination.setEnabled(False)

    def calculateRoute(self):
        self.deleteRoutes()
        self.network_layer = uf.getLegendLayerByName(self.iface, "roads")
        source_points = [self.startingPoint, self.destinationPoint]
        self.graph, self.tied_points = uf.makeUndirectedGraph(self.network_layer, source_points)
        path = uf.calculateRouteDijkstra(self.graph, self.tied_points, 0, 1)
        routes_layer = uf.getLegendLayerByName(self.iface, "routing layer")
        uf.insertTempFeatures(routes_layer, [path], [])
        print("routing")
        self.refreshCanvas(routes_layer)
        self.RateSpot.setEnabled(True)
        self.ShowRoute.setEnabled(False)


    def deleteRoutes(self):
        routes_layer = uf.getLegendLayerByName(self.iface, "routing layer")
        if routes_layer:
            ids = uf.getAllFeatureIds(routes_layer)
            routes_layer.startEditing()
            for id in ids:
                routes_layer.deleteFeature(id)
            routes_layer.commitChanges()

    def getNetwork(self):
        roads_layer = self.layers_dic['roads']
        if roads_layer:
            # see if there is an obstacles layer to subtract roads from the network
            obstacles_layer = uf.getLegendLayerByName(self.iface, "Obstacles")
            if obstacles_layer:
                # retrieve roads outside obstacles (inside = False)
                features = uf.getFeaturesByIntersection(roads_layer, obstacles_layer, False)
                # add these roads to a new temporary layer
                road_network = uf.createTempLayer('Temp_Network','LINESTRING',roads_layer.crs().postgisSrid(),[],[])
                road_network.dataProvider().addFeatures(features)
            else:
                road_network = roads_layer
            return road_network
        else:
            return

    def buildNetwork(self):
        self.network_layer = self.getNetwork()
        if self.network_layer:
            # get the points to be used as origin and destination
            # in this case gets the centroid of the selected features
            selected_sources = uf.getLegendLayerByName(self.iface, "routing layer").selectedFeatures()
            source_points = [feature.geometry().centroid().asPoint() for feature in selected_sources]
            # build the graph including these points
            if len(source_points) > 1:
                self.graph, self.tied_points = uf.makeUndirectedGraph(self.network_layer, source_points)
                # the tied points are the new source_points on the graph
                if self.graph and self.tied_points:
                    text = "network is built for %s points" % len(self.tied_points)
                    self.insertReport(text)
        return

    # after adding features to layers needs a refresh (sometimes)
    def refreshCanvas(self, layer):
        if self.canvas.isCachingEnabled():
            layer.setCacheImage(None)
        else:
            self.canvas.refresh()



