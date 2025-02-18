# **ScenePresetsMenu plugin for Prism Pipeline 2**
A plugin to be used with version 2 of Prism Pipeline 

Prism automates and simplifies the workflow of animation and VFX projects.

You can find more information on the website:

https://prism-pipeline.com/

<br/>

**Tested up to Prism 2.0.15**

<br/>

## **Plugin Usage**

The ScenePresetsMenu plugin adds a menu to the Prism2 User Settings menu.  In this menu a user may add directories where Prism2 will search for scene file presets.  Any file in the selected directory will be displayed using "Create new version from preset" in the right-click menu of the Project Browser Scenefiles tab.  This enables "empty" scene files to be used across projects.

![Menu](https://github.com/AltaArts/ScenePresetsMenu--Prism-Plugin/assets/86539171/55b1acc5-4389-48c6-b243-5e52e09fb675)



Tip:  Preset Scenefiles may be organized in subfolders to help with organization.  For example several different DCC templates files under the DCC directory.

![RCL Menu](https://github.com/AltaArts/ScenePresetsMenu--Prism-Plugin/assets/86539171/6712b7f2-f158-427a-8a70-23ceba8e1da7)


Example locations: a shared network directory available to all users, or in the local Documents folder inside the Prism2 directory.

Scene files that are stored in each project's \\*project*\\*pipelineFolder*\PresetScenes will still show in the right-click menu in addition to the files in the directories specified in this plugin's menu. 

There is an added option in the Prism ScenePresetsMenu settings so a user may disable the display of the default scene presets that are included with DCC plugins.  This allows for Prism to display only the users custom presets from the added directory.


## **Installation**

This plugin is for Windows only, as Prism2 only supports Windows at this time.

You can either download the latest stable release version from: [Latest Release](https://github.com/AltaArts/ScenePresetsMenu--Prism-Plugin/releases/latest)

or download the current code zip file from the green "Code" button above or on [Github](https://github.com/JBreckeen/ScenePresetsMenu--Prism-Plugin/tree/main)

Copy the directory named "ScenePresetsMenu" to a directory of your choice, or a Prism2 plugin directory.

Prism's default plugin directories are: *{installation path}\Plugins\Apps* and *{installation Path}\Plugins\Custom*.

It is suggested to have all custom plugins in a seperate folder suchs as: *{drive}\ProgramData\Prism2\plugins\CustomPlugins*

You can add the additional plugin search paths in Prism2 settings.  Go to Settings->Plugins and click the gear icon.  This opens a dialogue and you may add additional search paths at the bottom.

Once added, you can either restart Prism2, or select the "Add existing plugin" (plus icon) and navigate to where you saved the ScenePresetsMenu folder.


## **Issues / Suggestions**

For any bug reports or suggestions, please add to the GitHub repo.
