bl_info = {
    "name": "ECMA and OBJ exporting and importing tools",
    "author": "Robert Steckroth, Campbell Barton, Bastien Montagne",
    "version": (0, 4, 0),
    "blender": (2, 80, 0),
    "location": "File > Import-Export",
    "description": "Exports and imports OBJ and ECMA files which conform to the PBD standards.",
    "warning": "",
    "support": "TESTING",
    "category": "Import-Export"
}

from .lib import terrain_tools
from .lib import addon_preference
from .lib import addon_property
from .lib import text_creation
from .lib import object_creation
from .lib import file_export
from .lib import file_import
from .lib import main_panel

def register():
    terrain_tools.register()
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
    terrain_tools.unregister()

if __name__ == "__main__":
    register()
