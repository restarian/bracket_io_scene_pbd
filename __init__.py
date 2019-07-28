bl_info = {
    "name": "PBD, JSON and OBJ inporting and exporting tools",
    "author": "Robert Steckroth, Campbell Barton, Bastien Montagne",
    "version": (0, 1, 3),
    "blender": (2, 80, 0),
    "location": "File > Import-Export",
    "description": "Exports and imports OBJ and JSON files which conform to the PBD standards. Provides tools which aid PBD model data",
    "warning": "",
    "support": "COMMUNITY",
    "category": "Import-Export"
}

modulesNames = ["addon_preference", "main_panel", "addon_property", "text_creation", "object_creation", "file_export", "file_import" ]

import sys
import importlib
import bpy

modulesFullNames = {}
for currentModuleName in modulesNames:
    modulesFullNames[currentModuleName] = ('{}.{}'.format(__name__, currentModuleName))

for currentModuleFullName in modulesFullNames.values():
    if currentModuleFullName in sys.modules:
        importlib.reload(sys.modules[currentModuleFullName])
    else:
        globals()[currentModuleFullName] = importlib.import_module(currentModuleFullName)
        setattr(globals()[currentModuleFullName], 'modulesNames', modulesFullNames)

def register():
    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'register'):
                sys.modules[currentModuleName].register()

def unregister():
    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'unregister'):
                sys.modules[currentModuleName].unregister()

if __name__ == "__main__":
    register()
