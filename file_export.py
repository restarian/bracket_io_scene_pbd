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

import bpy, os
from bpy.props import ( BoolProperty, FloatProperty, StringProperty, EnumProperty, IntProperty )
from bpy_extras.io_utils import ( axis_conversion )

class CustomExportHelper:
    filepath: StringProperty(
        name="File Path",
        description="Filepath used for exporting the file",
        maxlen=1024,
        subtype='FILE_PATH',
    )
    check_existing: BoolProperty(
        name="Check Existing",
        description="Check and warn on overwriting existing files",
        default=True,
        options={'HIDDEN'},
    )

    # subclasses can override with decorator
    # True == use ext, False == no ext, None == do nothing.
    check_extension = True
    use_pbd_path = False
    is_pbd_terrain = False

    def check(self, _context):
        change_ext = False
        check_extension = self.check_extension

        if check_extension is not None:
            filepath = self.filepath
            if os.path.basename(filepath):
                filepath = bpy.path.ensure_ext(
                    filepath,
                    self.filename_ext
                    if check_extension
                    else "",
                )

                if filepath != self.filepath:
                    self.filepath = filepath
                    change_ext = True

        return change_ext

    def invoke(self, context, _event):

        path = ''
        if self.use_pbd_path:
            if context.scene.pbd_prop.export_object_with == 'scene':
                c_ob = context.scene.pbd_prop
            else:
                c_ob = context.collection.pbd_prop

            if self.is_pbd_terrain:
                if c_ob.terrain_use_active_object:
                    terrain_obj = context.active_object
                else:
                    t_ob = c_ob.terrain_object.strip()
                    if t_ob in c.objects:
                        terrain_obj = c.objects[t_obj]

                c_ob = terrain_obj.pbd_prop

            path = os.path.join(os.path.dirname(context.blend_data.filepath), c_ob.name)

        if not self.filepath:
            blend_filepath = path or context.blend_data.filepath
            if not blend_filepath:
                blend_filepath = "untitled"
            else:
                blend_filepath = os.path.splitext(blend_filepath)[0]

            self.filepath = blend_filepath + self.filename_ext

        else:
            if self.use_pbd_path:
                self.filepath = os.path.join(path, os.path.splitext(os.path.basename(path))[0] + self.filename_ext)

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class ExportTerrain(bpy.types.Operator, CustomExportHelper):
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
    use_pbd_path = True
    is_pbd_terrain = True

    def execute(self, context):

        from . import export_json
        from mathutils import Matrix

        if context.scene.pbd_prop.export_object_with == 'scene':
            c = context.scene
            c_ob = c.pbd_prop
        else:
            c = context.collection
            c_ob = c.pbd_prop

        global_matrix = (Matrix.Scale(c_ob.scale, 4) @ axis_conversion(to_forward="Y", to_up="-Z", ).to_4x4())

        if c_ob.terrain_use_active_object:
            terrain_obj = context.active_object
        else:
            terrain_obj = c.objects[c_ob.terrain_object.strip()]

        export_json.makeTerrain(context,
            filepath=self.filepath,
            output_path=c_ob.json_output_path,
            object_name=terrain_obj.name,
            precision=c_ob.json_precision,
            terrain_matrix=global_matrix,
            use_mesh_modifiers=c_ob.terrain_use_mesh_modifiers,
            use_normals=c_ob.terrain_use_normals,
            )

        return {"FINISHED"}

def exportJson(self, context):

    from . import export_json
    if context.scene.pbd_prop.export_object_with == 'scene':
        c_ob = context.scene.pbd_prop
    else:
        c_ob = context.collection.pbd_prop

    export_json.make(context,
        export_type=c_ob.json_export_type,
        input_path=self.filepath,
        output_path=c_ob.json_output_path,
        asset_root=c_ob.json_asset_root,
        texture_subdir=c_ob.json_texture_subdir,
        script_path=context.preferences.addons["bracket_io_scene_pbd"].preferences.script_path,
        precision=c_ob.json_precision,
        ignore_normals=c_ob.json_ignore_normals,
        ignore_uv=c_ob.json_ignore_uv_map,
        ignore_meta=c_ob.json_ignore_meta,
        force_texture=c_ob.json_force_texture,
        compression_level=c_ob.json_compressed,
        addition_option=c_ob.json_additional_option,
   )

class ExportFile(bpy.types.Operator, CustomExportHelper):
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
    use_pbd_path = True

    def execute(self, context):

        from . import export_obj
        from mathutils import Matrix

        if context.scene.pbd_prop.export_object_with == 'scene':
            c_ob = context.scene.pbd_prop
        else:
            c_ob = context.collection.pbd_prop

        to_foward = "-Y"
        if c_ob.json_export_type == "model":
            to_forward = "Y"

        global_matrix = (Matrix.Scale(c_ob.scale, 4) @ axis_conversion(to_forward=to_foward, to_up="-Z", ).to_4x4())

        keywords = {}
        keywords["global_matrix"] = global_matrix
        keywords["use_selection"] = c_ob.use_selection
        keywords["use_collection"] = context.scene.pbd_prop.export_object_with == 'collection'
        keywords["use_hidden"] = c_ob.use_hidden
        keywords["use_order"] = c_ob.use_draw_order
        keywords["use_animation"] = c_ob.use_animation
        keywords["use_mesh_modifiers"] = c_ob.model_use_mesh_modifiers
        keywords["use_normals"] = c_ob.ignore_normals,
        keywords["use_uvs"] = c_ob.ignore_uv_map,
        keywords["filepath"] = self.filepath

        export_obj.save(context, **keywords)
        if c_ob.json_export_type != "none" and len(context.preferences.addons["bracket_io_scene_pbd"].preferences.script_path.strip()):
            exportJson(self, context)

        return {"FINISHED"}

class ExportJsFromObj(bpy.types.Operator):
    """Save a PBD javascript file using the input OBJ file instead of the exported scene objects"""

    bl_idname = "export.json_from_obj"
    bl_label = 'Export using existing OBJ'
    bl_options = {'PRESET'}

    @classmethod
    def poll(cls, context):
        if context.scene.pbd_prop.export_object_with == 'scene':
            c_ob = context.scene.pbd_prop
        else:
            c_ob = context.collection.pbd_prop
        return bool(len(c_ob.json_import_path.strip()))

    def execute(self, context):

        if len(context.preferences.addons["bracket_io_scene_pbd"].preferences.script_path.strip()):
            exportJson(self, context)

        return {"FINISHED"}

def register():
    bpy.utils.register_class(ExportFile)
    bpy.utils.register_class(ExportTerrain)
    bpy.utils.register_class(ExportJsFromObj)


def unregister():
    bpy.utils.unregister_class(ExportFile)
    bpy.utils.unregister_class(ExportTerrain)
    bpy.utils.unregister_class(ExportJsFromObj)
