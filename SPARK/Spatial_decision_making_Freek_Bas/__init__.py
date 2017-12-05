# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Spatial_decision_making_Freek_Bas
                                 A QGIS plugin
 Plugin for
                             -------------------
        begin                : 2017-12-05
        copyright            : (C) 2017 by Bas van Tol
        email                : bvantol3@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Spatial_decision_making_Freek_Bas class from file Spatial_decision_making_Freek_Bas.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .spark import Spatial_decision_making_Freek_Bas
    return Spatial_decision_making_Freek_Bas(iface)
