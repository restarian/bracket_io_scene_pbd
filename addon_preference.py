import bpy

class PBDAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = "io_scene_json"

    script_path = bpy.props.StringProperty(
        name="Path to the Batten Mesh cli script (convert.js)",
        default="",
        options={'HIDDEN'},
        maxlen=1024,
        subtype='FILE_PATH'
        )

    alphabet = bpy.props.StringProperty(
        name="Alphabet to use",
        default = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890-=!@#$%^&*()_+`~[]\\{}|;':\",./<>?"
        )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Options pertaining to the PBD tool shelf")
        layout.prop(self, "script_path")
        layout.prop(self, "alphabet")

def register():
    bpy.utils.register_class(PBDAddonPreferences)

def unregister():
    bpy.utils.unregister_class(PBDAddonPreferences)
