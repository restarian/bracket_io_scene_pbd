bl_info = {
    "name": "ECMA and OBJ exporting and importing tools",
    "author": "Robert Steckroth, Campbell Barton, Bastien Montagne",
    "version": (0, 3, 0),
    "blender": (2, 80, 0),
    "location": "File > Import-Export",
    "description": "Exports and imports OBJ and ECMA files which conform to the PBD standards.",
    "warning": "",
    "support": "TESTING",
    "category": "Import-Export"
}

moduleNames = ["addon_preference", "main_panel", "addon_property", "text_creation", "object_creation", "file_export", "file_import" ]

from . import addon_preference
from . import addon_property
from . import text_creation
from . import object_creation
from . import file_export
from . import file_import
from . import main_panel

def register():
    addon_preference.register()
    addon_property.register()
    text_creation.register()
    object_creation.register()
    main_panel.register()
    file_export.register()
    file_import.register()

def unregister():
    addon_preference.unregister()
    addon_property.unregister()
    text_creation.unregister()
    object_creation.unregister()
    main_panel.unregister()
    file_export.unregister()
    file_import.unregister()

if __name__ == "__main__":
    register()
