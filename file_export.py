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
from bpy_extras.io_utils import ( ExportHelper, ImportHelper, orientation_helper_factory, path_reference_mode, axis_conversion )

from . import export_obj
from . import export_json

IOOBJOrientationHelper = orientation_helper_factory("IOOBJOrientationHelper", axis_forward='-Y', axis_up='-Z')

class ExportFile(bpy.types.Operator, ExportHelper, IOOBJOrientationHelper):
    """Save a Wavefront OBJ File with some added features to conform to the PBD engine"""

    bl_idname = "export.pbd_file"
    bl_label = 'Export'
    #bl_options = {'PRESET'}

    filename_ext = ".obj"
    filter_glob = StringProperty(
            default="*.obj;*.mtl",
            options={'HIDDEN'},
            )

    # object group
    use_mesh_modifiers = BoolProperty(
            name="Apply Modifiers",
            description="Apply modifiers",
            default=True,
            )
    use_mesh_modifiers_render = BoolProperty(
            name="Use Modifiers Render Settings",
            description="Use render settings when applying modifiers to mesh objects",
            default=False,
            )

    # extra data group
    use_edges = BoolProperty(
            name="Include Edges",
            description="",
            default=True,
            )
    use_smooth_groups = BoolProperty(
            name="Smooth Groups",
            description="Write sharp edges as smooth groups",
            default=False,
            )
    use_smooth_groups_bitflags = BoolProperty(
            name="Bitflag Smooth Groups",
            description="Same as 'Smooth Groups', but generate smooth groups IDs as bitflags "
                        "(produces at most 32 different smooth groups, usually much less)",
            default=False,
            )
    use_normals = BoolProperty(
            name="Write Normals",
            description="Export one normal per vertex and per face, to represent flat faces and sharp edges",
            default=True,
            )
    use_uvs = BoolProperty(
            name="Include UVs",
            description="Write out the active UV coordinates",
            default=True,
            )
    use_materials = BoolProperty(
            name="Write Materials",
            description="Write out the MTL file",
            default=True,
            )
    use_triangles = BoolProperty(
            name="Triangulate Faces",
            description="Convert all faces to triangles",
            default=True,
            )
    use_nurbs = BoolProperty(
            name="Write Nurbs",
            description="Write nurbs curves as OBJ nurbs rather than "
                        "converting to geometry",
            default=False,
            )

    # grouping group
    use_blen_objects = BoolProperty(
            name="Objects as OBJ Objects",
            description="",
            default=True,
            )
    keep_vertex_order = BoolProperty(
            name="Keep Vertex Order",
            description="",
            default=False,
            )

    global_scale = FloatProperty(
            name="Scale",
            min=0.01, max=1000.0,
            default=1.0,
            )

    path_mode = path_reference_mode

    check_extension = True
    def execute(self, context):

        from mathutils import Matrix
        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "global_scale",
                                            "check_existing",
                                            "filter_glob",
                                            ))


        keywords["use_selection"] = context.scene.pbd_prop.use_selection
        keywords["use_order"] = context.scene.pbd_prop.use_draw_order
        keywords["use_animation"] = context.scene.pbd_prop.use_animation

        global_matrix = (Matrix.Scale(self.global_scale, 4) *
                         axis_conversion(to_forward=self.axis_forward,
                                         to_up=self.axis_up,
                                         ).to_4x4())

        keywords["global_matrix"] = global_matrix

        input_path = keywords["filepath"]
        export_obj.save(context, **keywords)

        if context.scene.pbd_prop.convert_to_json:

            export_json.save(context,
                export_type=context.scene.pbd_prop.json_export_type,
                input_path=input_path,
                output_path=context.scene.pbd_prop.json_output_path,
                asset_root=context.scene.pbd_prop.json_asset_root,
                texture_subdir=context.scene.pbd_prop.json_texture_subdir,
                script_path=context.user_preferences.addons["bracket_io_scene_pbd"].preferences.script_path,
                precision=context.scene.pbd_prop.json_precision,
                ignore_normals=context.scene.pbd_prop.json_ignore_normals,
                include_meta=context.scene.pbd_prop.json_include_meta,
                force_texture=context.scene.pbd_prop.json_force_texture,
                addition_option=context.scene.pbd_prop.json_additional_option,
           )

        return {"FINISHED"}

class ExportJSON(bpy.types.Operator):
    """Save a JSON File using the input OBJ file instead of the exported scene objectse"""

    bl_idname = "export.json_from_obj"
    bl_label = 'Export using existing OBJ'
    #bl_options = {'PRESET'}

    @classmethod
    def poll(cls, context):
        return context.scene.pbd_prop.json_import_path and not context.scene.pbd_prop.json_import_path.isspace()

    def execute(self, context):

        export_json.save(context,
            export_type=context.scene.pbd_prop.json_export_type,
            input_path=context.scene.pbd_prop.json_import_path,
            output_path=context.scene.pbd_prop.json_output_path,
            asset_root=context.scene.pbd_prop.json_asset_root,
            texture_subdir=context.scene.pbd_prop.json_texture_subdir,
            script_path=context.user_preferences.addons["bracket_io_scene_pbd"].preferences.script_path,
            precision=context.scene.pbd_prop.json_precision,
            ignore_normals=context.scene.pbd_prop.json_ignore_normals,
            include_meta=context.scene.pbd_prop.json_include_meta,
            force_texture=context.scene.pbd_prop.json_force_texture,
            addition_option=context.scene.pbd_prop.json_additional_option,
       )

        return {"FINISHED"}

def register():
    bpy.utils.register_class(ExportFile)
    bpy.utils.register_class(ExportJSON)


def unregister():
    bpy.utils.unregister_class(ExportFile)
    bpy.utils.unregister_class(ExportJSON)
