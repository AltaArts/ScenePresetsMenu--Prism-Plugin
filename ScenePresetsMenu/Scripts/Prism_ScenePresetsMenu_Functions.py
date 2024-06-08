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
import logging

from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *

from PrismUtils.Decorators import err_catcher_plugin as err_catcher

logger = logging.getLogger(__name__)



class Prism_ScenePresetsMenu_Functions(object):
    def __init__(self, core, plugin):
        self.core = core
        self.plugin = plugin

        #   Global Settings File
        pluginLocation = os.path.dirname(os.path.dirname(__file__))
        self.settingsFile = os.path.join(pluginLocation, "ScenePresetsMenu_Config.json")

        #   Callbacks
        logger.debug("Loading callbacks")
        self.core.registerCallback("userSettings_loadUI", self.userSettings_loadUI, plugin=self)
        self.core.registerCallback("getPresetScenes", self.getPresetScenes, plugin=self, priority=40)
        self.core.registerCallback("onUserSettingsSave", self.saveSettings, plugin=self)


    # if returns true, the plugin will be loaded by Prism
    @err_catcher(name=__name__)
    def isActive(self):
        return True


    #   Called with Callback
    @err_catcher(name=__name__)
    def getPresetScenes(self, presetScenes):
        try:
            logger.debug("Loading Scene Presets")

            pData = self.loadSettings()
            ignorePresets = pData["Ignore Default Presets"]
            presetDirs = pData["Paths"]

            #   If settings is checked, deletes list passed from Core
            if ignorePresets:
                # Clear the list in place
                del presetScenes[:]

                #   Adds presets from Project Directory
                presetDir = os.path.join(self.core.projects.getPipelineFolder(), "PresetScenes")
                scenes = self.core.entities.getPresetScenesFromFolder(presetDir)
                presetScenes.extend(scenes)

                # Reformats Project presets
                for scene in presetScenes:
                    # Split the label into directory part and basename part
                    directory, basename = os.path.split(scene["label"])
                    #   Adds slash if there is a subdirectory
                    if directory != "":
                        dirStr = f"{directory}/"
                    else:
                        dirStr = ""
                    # Add "PROJECT" prefix to display under Project folder
                    # and astrix before name to ensure it is at the top of the list
                    scene["label"] = f"PROJECT/{dirStr}*{basename}"

            # Convert the existing list of scenes to a set of labels for quick lookup
            existingLabels = {scene["label"] for scene in presetScenes}

            #   Gets all files from the Dirs in the Settings File
            for presetDir in presetDirs:
                scenes = self.core.entities.getPresetScenesFromFolder(presetDir)

                # Add items to the list in place if not already present
                for scene in scenes:
                    if scene["label"] not in existingLabels:
                        presetScenes.append(scene)
                        existingLabels.add(scene["label"])

            return presetScenes

        except Exception as e:
            logger.warning(f"Unable to load Scene Presets:\n{e}")


    #   Called with Callback
    @err_catcher(name=__name__)
    def userSettings_loadUI(self, origin):      #   ADDING "Scene Presets" TO SETTINGS

        headerLabels = ["Path"]

        # Create a Widget
        origin.w_scenePresets = QWidget()
        origin.lo_scenePresets = QVBoxLayout(origin.w_scenePresets)

        #   Send To Menu UI List
        gb_scenePresets = QGroupBox("Scene Presets Directory")
        lo_scenePresets = QVBoxLayout()
        gb_scenePresets.setLayout(lo_scenePresets)

        self.tw_scenePresets = QTableWidget()
        self.tw_scenePresets.setColumnCount(len(headerLabels))
        self.tw_scenePresets.setHorizontalHeaderLabels(headerLabels)
        self.tw_scenePresets.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)

        #   Sets initial table size
        self.tw_scenePresets.setMinimumHeight(300)  # Adjust the value as needed

        #   Adds Buttons
        w_scenePresets = QWidget()
        lo_scenePresetsButtons = QHBoxLayout()

        self.chb_defaultPresets = QCheckBox("  Disable default DCC plugin Scene Presets")
        b_addScenePresets = QPushButton("Add...")
        b_removeScenePresets = QPushButton("Remove")

        w_scenePresets.setLayout(lo_scenePresetsButtons)

        lo_scenePresetsButtons.addWidget(self.chb_defaultPresets)
        lo_scenePresetsButtons.addStretch()
        lo_scenePresetsButtons.addWidget(b_addScenePresets)
        lo_scenePresetsButtons.addWidget(b_removeScenePresets)

        lo_scenePresets.addWidget(self.tw_scenePresets)
        lo_scenePresets.addWidget(w_scenePresets)
        origin.lo_scenePresets.addWidget(gb_scenePresets)

        #   Makes ReadOnly
        self.tw_scenePresets.setEditTriggers(QAbstractItemView.NoEditTriggers)

        #   Configures table
        self.tw_scenePresets.setSelectionBehavior(QTableWidget.SelectRows)
        self.tw_scenePresets.setSelectionMode(QTableWidget.SingleSelection)

        # Set resizing mode for the "Path" column to stretch
        self.tw_scenePresets.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        #   Executes button actions
        b_addScenePresets.clicked.connect(lambda: self.addScenePresetsDir(origin))
        b_removeScenePresets.clicked.connect(lambda: self.removeScenePresetsDir())

        try:
            logger.debug("Loading Menu data")

            #   Loads Settings File
            pData = self.loadSettings()

            if "Ignore Default Presets" in pData:
                ignorePresets = pData["Ignore Default Presets"]
                self.chb_defaultPresets.setChecked(ignorePresets)

            if "Paths" in pData:
                scenePresetsList = pData["Paths"]

            #   Populates lists from Settings File Data
            for item in scenePresetsList:
                rowPosition = self.tw_scenePresets.rowCount()
                self.tw_scenePresets.insertRow(rowPosition)
                self.tw_scenePresets.setItem(rowPosition, 0, QTableWidgetItem(item))

        except Exception as e:
            logger.warning(f"Unable to load Scene Preset data:\n{e}")

        #   Tooltips
        tip = ("Directories that will hold Preset Scene Files.\n\n"
                "These will be available to all projects in addition to the ones\n"
                "included in the Project's Pipeline folder."
                )
        self.tw_scenePresets.setToolTip(tip)

        tip = ("Disables the default Prism scene presets that come with DCC plugins.\n"
               "This does not delete the presets from the plugin directories.\n"
               "Presets contained in each projects preset dir will still be visable.")
        self.chb_defaultPresets.setToolTip(tip)

        tip = "Opens dialogue to choose directory to add."
        b_addScenePresets.setToolTip(tip)

        tip = "Remove selected directory."
        b_removeScenePresets.setToolTip(tip)

        # Initialize button states
        self.updateButtonStates(b_removeScenePresets)

        # Connect item selection changed signal to the method
        self.tw_scenePresets.itemSelectionChanged.connect(lambda: self.updateButtonStates(b_removeScenePresets))

        # Add Tab to User Settings
        origin.addTab(origin.w_scenePresets, "Scene Presets")


    @err_catcher(name=__name__)
    def updateButtonStates(self, b_removeScenePresets):
        selectedItems = self.tw_scenePresets.selectedItems()
        hasSelection = bool(selectedItems)
        
        b_removeScenePresets.setEnabled(hasSelection)


    @err_catcher(name=__name__)
    def addScenePresetsDir(self, origin):
        # Open native file dialog to choose a directory
        directory = QFileDialog.getExistingDirectory(origin, "Select Scene Presets Directory", QDir.homePath())

        # Check if the user selected a directory
        if directory:
            rowPosition = self.tw_scenePresets.rowCount()
            self.tw_scenePresets.insertRow(rowPosition)
            self.tw_scenePresets.setItem(rowPosition, 0, QTableWidgetItem(directory))


    @err_catcher(name=__name__)
    def removeScenePresetsDir(self):

        selectedRow = self.tw_scenePresets.currentRow()

        if selectedRow != -1:
            self.tw_scenePresets.removeRow(selectedRow)


    @err_catcher(name=__name__)
    def loadSettings(self):
        #   Loads Global Settings File JSON
        try:
            with open(self.settingsFile, "r") as json_file:
                pData = json.load(json_file)
                return pData
            
        except FileNotFoundError:
            logger.debug("Settings File not found, creating new")
            pData = self.createSettings()
            return pData
        
        except Exception as e:
            logger.warning(f"Settings file is corrupt, creating new")
            pData = self.createSettings()
            return pData


    @err_catcher(name=__name__)
    def createSettings(self):
        #   Deletes settings file if corrupt
        if os.path.exists(self.settingsFile):
            os.remove(self.settingsFile)

        #   Makes default pData
        pData = {}
        pData["Ignore Default Presets"] = False

        paths = []
        pData["Paths"] = paths

        #   Saves to settings JSON File
        with open(self.settingsFile, "w") as json_file:
            json.dump(pData, json_file, indent=4)
        
        return pData


    @err_catcher(name=__name__)
    def saveSettings(self, origin=None):

        pData = {}

        ignorePresets = self.chb_defaultPresets.isChecked()

        pData["Ignore Default Presets"] = ignorePresets

        paths = []
        #   Populates data[] from UI List
        for row in range(self.tw_scenePresets.rowCount()):
            pathItem = self.tw_scenePresets.item(row, 0)

            if pathItem:
                location = pathItem.text()
                paths.append(location)

        pData["Paths"] = paths

        #   Saves to Global JSON File
        with open(self.settingsFile, "w") as json_file:
            json.dump(pData, json_file, indent=4)
