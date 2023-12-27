# -*- coding: utf-8 -*-
#
####################################################
#
# PRISM - Pipeline for animation and VFX projects
#
# www.prism-pipeline.com
#
# contact: contact@prism-pipeline.com
#
####################################################
#
#
# Copyright (C) 2016-2023 Richard Frangenberg
# Copyright (C) 2023 Prism Software GmbH
#
# Licensed under GNU LGPL-3.0-or-later
#
# This file is part of Prism.
#
# Prism is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Prism is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Prism.  If not, see <https://www.gnu.org/licenses/>.
#
####################################################
####################################################
#
#           SEND TO MENU PLUGIN
#           by Joshua Breckeen
#                Alta Arts
#
#   This PlugIn adds an additional tab to the Prism Settings menu to 
#   allow a user to choose a directory that contains scene presets.
#
####################################################


try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
except:
    from PySide.QtCore import *
    from PySide.QtGui import *

import os, json

from PrismUtils.Decorators import err_catcher_plugin as err_catcher


class Prism_ScenePresetsMenu_Functions(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin

        #   Global Settings File
        pluginLocation = os.path.dirname(os.path.dirname(__file__))
        global settingsFile
        settingsFile = os.path.join(pluginLocation, "ScenePresetsMenu_Config.json")

        #   Callbacks
        self.core.registerCallback("userSettings_loadUI", self.userSettings_loadUI, plugin=self)
        self.core.registerCallback("getPresetScenes", self.getPresetScenes, plugin=self)


    # if returns true, the plugin will be loaded by Prism
    @err_catcher(name=__name__)
    def isActive(self):
        return True


    #   Called with Callback
    @err_catcher(name=__name__)
    def getPresetScenes(self, presetScenes):

        presetDirs = self.loadSettings()

        #   Gets all files from the Dirs in the Global Settings File
        for presetDir in presetDirs:
            scenes = self.core.entities.getPresetScenesFromFolder(presetDir["Path"])
            presetScenes += scenes

        return


    #   Called with Callback
    @err_catcher(name=__name__)
    def userSettings_loadUI(self, origin):      #   ADDING "Scene Presets" TO SETTINGS

        #   Loads Settings File
        ScenePresetsList = self.loadSettings()
        headerLabels = ["Path"]

        # Create a Widget
        origin.w_ScenePresets = QWidget()
        origin.lo_ScenePresets = QVBoxLayout(origin.w_ScenePresets)

        #   Send To Menu UI List
        gb_ScenePresets = QGroupBox("Scene Presets Directory")
        lo_ScenePresets = QVBoxLayout()
        gb_ScenePresets.setLayout(lo_ScenePresets)

        tw_ScenePresets = QTableWidget()
        tw_ScenePresets.setColumnCount(len(headerLabels))
        tw_ScenePresets.setHorizontalHeaderLabels(headerLabels)
        tw_ScenePresets.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)

        #   Sets initial table size
        tw_ScenePresets.setMinimumHeight(300)  # Adjust the value as needed


        #   Adds Buttons
        w_ScenePresets = QWidget()
        lo_ScenePresetsButtons = QHBoxLayout()
        b_addScenePresets = QPushButton("Add")
        b_removeScenePresets = QPushButton("Remove")

        w_ScenePresets.setLayout(lo_ScenePresetsButtons)
        lo_ScenePresetsButtons.addStretch()
        lo_ScenePresetsButtons.addWidget(b_addScenePresets)
        lo_ScenePresetsButtons.addWidget(b_removeScenePresets)

        lo_ScenePresets.addWidget(tw_ScenePresets)
        lo_ScenePresets.addWidget(w_ScenePresets)
        origin.lo_ScenePresets.addWidget(gb_ScenePresets)

        #   Makes ReadOnly
        tw_ScenePresets.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Set resizing mode for the "Path" column to stretch
        tw_ScenePresets.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        #   Executes button actions
        b_addScenePresets.clicked.connect(lambda: self.addScenePresetsDir(origin, tw_ScenePresets))
        b_removeScenePresets.clicked.connect(lambda: self.removeScenePresetsDir(origin, tw_ScenePresets))

        #   Populates lists from Settings File Data
        for item in ScenePresetsList:
            rowPosition = tw_ScenePresets.rowCount()
            tw_ScenePresets.insertRow(rowPosition)
            tw_ScenePresets.setItem(rowPosition, 0, QTableWidgetItem(item.get("Path", "")))

        # Add Tab to User Settings
        origin.addTab(origin.w_ScenePresets, "Scene Presets")


    @err_catcher(name=__name__)
    def addScenePresetsDir(self, origin, tw_ScenePresets):

        # Open native file dialog to choose a directory
        directory = QFileDialog.getExistingDirectory(origin, "Select Scene Presets Directory", QDir.homePath())

        # Check if the user selected a directory
        if directory:
            rowPosition = tw_ScenePresets.rowCount()
            tw_ScenePresets.insertRow(rowPosition)
            tw_ScenePresets.setItem(rowPosition, 0, QTableWidgetItem(directory))

            # Save UI List to JSON file
            self.saveSettings(tw_ScenePresets)

    @err_catcher(name=__name__)
    def removeScenePresetsDir(self, origin, tw_ScenePresets):

        selectedRow = tw_ScenePresets.currentRow()

        if selectedRow != -1:
            tw_ScenePresets.removeRow(selectedRow)

            #   Saves UI List to JSON file
            self.saveSettings(tw_ScenePresets)


    @err_catcher(name=__name__)
    def loadSettings(self):

        #   Loads Global Settings File JSON
        try:
            with open(settingsFile, "r") as json_file:
                data = json.load(json_file)
                return data
            
        except FileNotFoundError:
            return []


    @err_catcher(name=__name__)
    def saveSettings(self, tw_ScenePresets):

        data = []

        #   Populates data[] from UI List
        for row in range(tw_ScenePresets.rowCount()):
            pathItem = tw_ScenePresets.item(row, 0)

            if pathItem:
                location = pathItem.text()

                data.append({"Path": location})

        #   Saves to Global JSON File
        with open(settingsFile, "w") as json_file:
            json.dump(data, json_file, indent=4)
