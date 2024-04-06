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
#        SCENE PRESETS MENU PLUGIN
#           by Joshua Breckeen
#                Alta Arts
#
#   This PlugIn adds an additional tab to the Prism Settings menu to 
#   allow a user to choose a directory that contains scene presets.
#
####################################################


import os
import json

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

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
        scenePresetsList = self.loadSettings()
        headerLabels = ["Path"]

        # Create a Widget
        origin.w_scenePresets = QWidget()
        origin.lo_scenePresets = QVBoxLayout(origin.w_scenePresets)

        #   Send To Menu UI List
        gb_scenePresets = QGroupBox("Scene Presets Directory")
        lo_scenePresets = QVBoxLayout()
        gb_scenePresets.setLayout(lo_scenePresets)

        tw_scenePresets = QTableWidget()
        tw_scenePresets.setColumnCount(len(headerLabels))
        tw_scenePresets.setHorizontalHeaderLabels(headerLabels)
        tw_scenePresets.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)

        #   Sets initial table size
        tw_scenePresets.setMinimumHeight(300)  # Adjust the value as needed


        #   Adds Buttons
        w_scenePresets = QWidget()
        lo_scenePresetsButtons = QHBoxLayout()
        b_addScenePresets = QPushButton("Add")
        b_removeScenePresets = QPushButton("Remove")

        w_scenePresets.setLayout(lo_scenePresetsButtons)
        lo_scenePresetsButtons.addStretch()
        lo_scenePresetsButtons.addWidget(b_addScenePresets)
        lo_scenePresetsButtons.addWidget(b_removeScenePresets)

        lo_scenePresets.addWidget(tw_scenePresets)
        lo_scenePresets.addWidget(w_scenePresets)
        origin.lo_scenePresets.addWidget(gb_scenePresets)

        #   Makes ReadOnly
        tw_scenePresets.setEditTriggers(QAbstractItemView.NoEditTriggers)

        #   Configures table
        tw_scenePresets.setSelectionBehavior(QTableWidget.SelectRows)
        tw_scenePresets.setSelectionMode(QTableWidget.SingleSelection)

        # Set resizing mode for the "Path" column to stretch
        tw_scenePresets.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        #   Executes button actions
        b_addScenePresets.clicked.connect(lambda: self.addScenePresetsDir(origin, tw_scenePresets))
        b_removeScenePresets.clicked.connect(lambda: self.removeScenePresetsDir(origin, tw_scenePresets))

        #   Populates lists from Settings File Data
        for item in scenePresetsList:
            rowPosition = tw_scenePresets.rowCount()
            tw_scenePresets.insertRow(rowPosition)
            tw_scenePresets.setItem(rowPosition, 0, QTableWidgetItem(item.get("Path", "")))

        #   Tooltip
        tip = ("Directories that will hold Preset Scene Files.\n\n"
                "These will be available to all projects in addition to the ones\n"
                "included in the Project's Pipeline folder."
                )
        tw_scenePresets.setToolTip(tip)

        # Add Tab to User Settings
        origin.addTab(origin.w_scenePresets, "Scene Presets")


    @err_catcher(name=__name__)
    def addScenePresetsDir(self, origin, tw_scenePresets):

        # Open native file dialog to choose a directory
        directory = QFileDialog.getExistingDirectory(origin, "Select Scene Presets Directory", QDir.homePath())

        # Check if the user selected a directory
        if directory:
            rowPosition = tw_scenePresets.rowCount()
            tw_scenePresets.insertRow(rowPosition)
            tw_scenePresets.setItem(rowPosition, 0, QTableWidgetItem(directory))

            # Save UI List to JSON file
            self.saveSettings(tw_scenePresets)

    @err_catcher(name=__name__)
    def removeScenePresetsDir(self, origin, tw_scenePresets):

        selectedRow = tw_scenePresets.currentRow()

        if selectedRow != -1:
            tw_scenePresets.removeRow(selectedRow)

            #   Saves UI List to JSON file
            self.saveSettings(tw_scenePresets)


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
    def saveSettings(self, tw_scenePresets):

        data = []

        #   Populates data[] from UI List
        for row in range(tw_scenePresets.rowCount()):
            pathItem = tw_scenePresets.item(row, 0)

            if pathItem:
                location = pathItem.text()

                data.append({"Path": location})

        #   Saves to Global JSON File
        with open(settingsFile, "w") as json_file:
            json.dump(data, json_file, indent=4)
