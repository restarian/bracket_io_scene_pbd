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

# <pep8-80 compliant>

import bpy
from bpy.props import ( BoolProperty, FloatProperty, StringProperty, EnumProperty, IntProperty )
from bpy_extras.io_utils import ( ExportHelper, axis_conversion )

class ExportTerrain(bpy.types.Operator, ExportHelper):
    """Save a terrain file which conforms to the PBD engine"""

    bl_idname = "export.pbd_terrain_file"
    bl_label = 'Export'
    bl_options = {'PRESET'}

    filename_ext = ".js"
    filter_glob = StringProperty(
            default="*.js",
            options={'HIDDEN'},
            )

    check_extension = True

    def execute(self, context):

        from . import export_json
        from mathutils import Matrix

        global_matrix = (Matrix.Scale(context.scene.pbd_prop.world_scale, 4) @ axis_conversion(to_forward="Y", to_up="-Z", ).to_4x4())

        if context.scene.pbd_prop.terrain_use_active_object:
            terrain_obj = context.active_object
        else:
            terrain_obj = context.scene.objects[context.scene.pbd_prop.terrain_object.strip()]

        export_json.makeTerrain(context,
            filepath=self.filepath,
            output_path=context.scene.pbd_prop.json_output_path,
            object_name=terrain_obj.name,
            precision=context.scene.pbd_prop.json_precision,
            terrain_matrix=global_matrix,
            use_mesh_modifiers=context.scene.pbd_prop.terrain_use_mesh_modifiers,
            use_normals=context.scene.pbd_prop.terrain_use_normals,
            )

        return {"FINISHED"}

class ExportFile(bpy.types.Operator, ExportHelper):
    """Save a Wavefront OBJ File with some added features to conform to the PBD engine"""

    bl_idname = "export.pbd_file"
    bl_label = 'Export'
    bl_options = {'PRESET'}

    filename_ext = ".obj"
    filter_glob = StringProperty(
            default="*.obj;*.mtl",
            options={'HIDDEN'},
            )

    check_extension = True
    def execute(self, context):

        from . import export_json
        from . import export_obj
        from mathutils import Matrix

        global_matrix = (Matrix.Scale(context.scene.pbd_prop.world_scale, 4) @ axis_conversion(to_forward="Y", to_up="-Z", ).to_4x4())

        keywords = {}
        keywords["global_matrix"] = global_matrix
        keywords["use_selection"] = context.scene.pbd_prop.use_selection
        keywords["use_order"] = context.scene.pbd_prop.use_draw_order
        keywords["use_animation"] = context.scene.pbd_prop.use_animation
        keywords["use_mesh_modifiers"] = context.scene.pbd_prop.model_use_mesh_modifiers
        keywords["filepath"] = self.filepath

        export_obj.save(context, **keywords)
        if context.scene.pbd_prop.convert_to_json and len(context.preferences.addons["bracket_io_scene_pbd"].preferences.script_path):

            export_json.make(context,
                export_type=context.scene.pbd_prop.json_export_type,
                input_path=self.filepath,
                output_path=context.scene.pbd_prop.json_output_path,
                asset_root=context.scene.pbd_prop.json_asset_root,
                texture_subdir=context.scene.pbd_prop.json_texture_subdir,
                script_path=context.preferences.addons["bracket_io_scene_pbd"].preferences.script_path,
                precision=context.scene.pbd_prop.json_precision,
                ignore_normals=context.scene.pbd_prop.json_ignore_normals,
                ignore_uv=context.scene.pbd_prop.json_ignore_uv_map,
                include_meta=context.scene.pbd_prop.json_include_meta,
                force_texture=context.scene.pbd_prop.json_force_texture,
                compression_level=context.scene.pbd_prop.json_compressed,
                addition_option=context.scene.pbd_prop.json_additional_option,
           )

        return {"FINISHED"}

class ExportJSON(bpy.types.Operator):
    """Save a PBD javascript file using the input OBJ file instead of the exported scene objects"""

    bl_idname = "export.json_from_obj"
    bl_label = 'Export using existing OBJ'
    bl_options = {'PRESET'}

    @classmethod
    def poll(cls, context):
        return context.scene.pbd_prop.json_import_path and not context.scene.pbd_prop.json_import_path.isspace()

    def execute(self, context):

        export_json.make(context,
            export_type=context.scene.pbd_prop.json_export_type,
            input_path=context.scene.pbd_prop.json_import_path,
            output_path=context.scene.pbd_prop.json_output_path,
            asset_root=context.scene.pbd_prop.json_asset_root,
            texture_subdir=context.scene.pbd_prop.json_texture_subdir,
            script_path=context.preferences.addons["bracket_io_scene_pbd"].preferences.script_path,
            precision=context.scene.pbd_prop.json_precision,
            ignore_normals=context.scene.pbd_prop.json_ignore_normals,
            include_meta=context.scene.pbd_prop.json_include_meta,
            force_texture=context.scene.pbd_prop.json_force_texture,
            compression_level=context.scene.pbd_prop.json_compressed,
            addition_option=context.scene.pbd_prop.json_additional_option,
        )
        return {"FINISHED"}

def register():
    bpy.utils.register_class(ExportFile)
    bpy.utils.register_class(ExportTerrain)
    bpy.utils.register_class(ExportJSON)


def unregister():
    bpy.utils.unregister_class(ExportFile)
    bpy.utils.unregister_class(ExportTerrain)
    bpy.utils.unregister_class(ExportJSON)
