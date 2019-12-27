# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

import bpy
import subprocess

def ShowMessageBox(message = "", title = "PBD JSON Exporting", icon = 'INFO'):
    message = str(message).replace("\\t", "   ").replace("\t", "   ").replace("\\n", "\n")
    def draw(self, context):
        for m in message.splitlines():
            self.layout.label(text=m)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

def save(context,
         export_type="model",
         input_path="",
         output_path="",
         asset_root="",
         texture_subdir="",
         script_path="",
         precision=5,
         ignore_normals=True,
         include_meta=True,
         force_texture=True,
         addition_option="",
         ):

    if not script_path:
        ShowMessageBox("The obj to json conversion script path is not set in the addon preferences", "Cannot export json", 'ERROR')
        return False

    param = ["node", script_path, "-t", str(precision), "-CavP", "-i", input_path, "-o", output_path]

    if ignore_normals:
        param.append("-z")

    if force_texture:
        param.append("-f")

    if include_meta:
        param.append("-m")

    if export_type == "widget":
        param.append("--shift-origin")
        param.append("0,span,0")
    elif export_type == "font":
        param.append("--set-origin")
        param.append("0,null,0")
        param.append("--shift-origin")
        param.append("null,span,0")

    if asset_root:
        param.append("--asset-root")
        param.append(asset_root)

    if texture_subdir:
        param.append("--texture-path")
        param.append(texture_subdir)

    if addition_option:
        param += addition_option.split()

    print(param)
    compleated = subprocess.run(param, timeout=12, capture_output=True)
    # popenobj = subprocess.Popen(param, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    if not compleated.stderr.isspace():
        ShowMessageBox(compleated.stderr, "Unable to run obj to json script", "ERROR")
        return False

    ShowMessageBox(compleated.stdout, "Batten mesh output", "INFO")
    return True
