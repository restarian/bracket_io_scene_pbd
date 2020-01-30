import bpy
import bpy, os, subprocess

def ShowMessageBox(message = "", title = "Batten Mesh Script path setting", icon = 'INFO'):
    message = str(message).replace("\\t", "   ").replace("\t", "   ").replace("\\n", "\n")
    def draw(self, context):
        for m in message.splitlines():
            self.layout.label(text=m)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

def check_for_script(self, context):
    """ Ensure that the convert.js script is valid"""

    ob = context.preferences.addons["bracket_io_scene_pbd"].preferences.script_path
    sane_path = lambda p: os.path.abspath(bpy.path.abspath(p))
    if ob.startswith('//'):
        path = sane_path(ob)
    else:
        path = ob

    if not len(path):
        return False

    param = ["node", path, "-D", "-C"]

    compleated = subprocess.run(param, timeout=4, capture_output=True)

    if len(compleated.stderr.decode("UTF-8")):
        ShowMessageBox(compleated.stderr.decode("UTF-8"), "Unable to run Batten Mesh script", "ERROR")
        return False

    if compleated.stdout.decode("UTF-8")[:78] != "[bin\\convert -> Batten Mesh - ERROR] A wavefront input file must be specified.":
        ShowMessageBox(compleated.stdout.decode("UTF-8"), "The set Batten Mesh script returned bad data (wrong verion maybe??)", "ERROR")
        return False

    ShowMessageBox("Successfully executed Batten Mesh script.", "Batten Mesh script set", "INFO")
    ob = path

class PBDAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = "bracket_io_scene_pbd"

    script_path = bpy.props.StringProperty(
        name="Batten mesh convert.js",
        description="The file path to the Batten Mesh cli script (convert.js)",
        default="",
        options={'HIDDEN'},
        update = lambda s,c: check_for_script(s, c),
        maxlen=1024,
        subtype='FILE_PATH'
        )

    alphabet = bpy.props.StringProperty(
        name="Text creation alphabet",
        default = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890-=!@#$%^&*()_+`~[]\\{}|;':\",./<>?",
        description="The characters which will populate the font creation text box when the reset button is clicked",
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
