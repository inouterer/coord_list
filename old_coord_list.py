# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CoordList
                                 A QGIS plugin
 CoordList
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-04-04
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Lebedev
        email                : lebedev77@gmail.com
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
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5.QtGui import QIcon

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .coord_list_dialog import CoordListDialog
import os.path
#My
from PyQt5.QtWidgets import QAction, QMessageBox
from PyQt5.QtCore import QVariant
from qgis.core import *
from qgis import *
from qgis.utils import iface


class CoordList:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'CoordList_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Coord List')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('CoordList', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/coord_list/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'CoordList'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Coord List'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = CoordListDialog()

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            #from qgis.core import *


            # Define sourse layer features
            layer = self.iface.activeLayer()
            dest_crs = self.dlg.mQgsProjectionSelectionWidget.crs()
            QMessageBox.warning(None, "Warning!", str(dest_crs))
            if layer is None:
                QMessageBox.warning(None, "Warning!", "No selected layer")
                return None
            if (layer.type() != 0):
                QMessageBox.warning(None, "Warning!", "Layer selected is not vector")
                return None
            if layer.selectedFeatureCount() == 0:
                QMessageBox.warning(None, "Warning!", "No feature selected")
                return None
            if layer.selectedFeatureCount() > 1:
                QMessageBox.warning(None, "Warning!", "More than one feature is selected")
                return None
            crs = layer.crs().toWkt()
            #Create layer with destination CRS
            vl = QgsVectorLayer('Point?crs='+ crs, 'LC', 'memory')
            from qgis.PyQt.QtCore import QVariant
            pr = vl.dataProvider()
            pr.addAttributes([QgsField("pid", QVariant.Int),
                              QgsField("x",  QVariant.Double),
                              QgsField("y", QVariant.Double),
                              QgsField("len", QVariant.Double),
                              QgsField("azmt", QVariant.Double)])
            vl.updateFields()

            #Define selected obj
            feat = layer.selectedFeatures()
            geom = feat[0].geometry()

            #Find out type o geometry
            sngl=0
            geomSingleType = QgsWkbTypes.isSingleType(geom.wkbType())
            if geom.type() == QgsWkbTypes.PointGeometry:
                # the geometry type can be of single or multi type
                if geomSingleType:
                    coords = geom.asPoint()
                    sngl=1
                    print ("Point")
                else:
                    coords = geom.asMultiPoint()
                    print ("MultiPoint")
            elif geom.type() == QgsWkbTypes.LineGeometry:
                if geomSingleType:
                    coords = geom.asPolyline()
                    sngl=1
                    print ("Polyline")
                else:
                    coords = geom.asMultiPolyline()
                    print ("MultiPolyline")
            elif geom.type() == QgsWkbTypes.PolygonGeometry:
                if geomSingleType:
                    coords = geom.asPolygon()
                    sngl=0
                    print ("Polygon")
                else:
                    coords = geom.asMultiPolygon()
                    print ("MultiPolygon")
            else:
                QMessageBox.warning(None, "Warning!", "Unknown or invalid geometry")
            #print (sngl)
            #Make a list of points
            pnts = []
            pid=0
            if sngl==0:
                for z in coords:
                    for x, y in z:
                        pid+=1
                        pnts.append(QgsPointXY(x,y))
            else:
                #print (coords)
                for x, y in coords:
                    pid+=1
                    pnts.append(QgsPointXY(x,y))
            numpnt = pid #Num points
            #Process
            crs = layer.crs()
            pid=0

            for x, y in pnts:
                pid+=1
                point1 = QgsPointXY(x,y)
                if pid==numpnt:
                    point2 = pnts[0]
                else:
                    point2 = pnts[pid]
                #Create a measure object
                distance = QgsDistanceArea()
                if crs.postgisSrid()==4326:
                    distance.setEllipsoid('WGS84')
                    len = distance.measureLine(point1, point2)
                else:
                    len = QgsPointXY.distance(point1, point2)
                #distance.setEllipsoidalMode(True)
                angl = QgsPointXY.azimuth(point1, point2)
                #Insert in layer
                f = QgsFeature()
                f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x,y)))
                f.setAttributes([pid, x, y, len, angl])
                pr.addFeature(f)

            #Commit new layer and add to map
            vl.updateExtents()
            QgsProject.instance().addMapLayer(vl)

            #Labeling
            settings = QgsPalLayerSettings()
            settings.fieldName = 'pid'
            labeling = QgsVectorLayerSimpleLabeling(settings)
            lv = self.iface.activeLayer()
            lv.setLabeling(labeling)
            lv.setLabelsEnabled(True)
            lv.triggerRepaint()
            #Show attribute Table
            if self.dlg.checkBox.isChecked():
                iface.showAttributeTable(iface.activeLayer())
            else:
                pass
