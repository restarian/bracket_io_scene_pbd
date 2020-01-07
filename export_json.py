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

import bpy, os, subprocess
from math import sqrt
from bpy_extras.wm_utils.progress_report import (
    ProgressReport,
    ProgressReportSubstep,
)

def ShowMessageBox(message = "", title = "PBD JSON Exporting", icon = 'INFO'):
    message = str(message).replace("\\t", "   ").replace("\t", "   ").replace("\\n", "\n")
    def draw(self, context):
        for m in message.splitlines():
            self.layout.label(text=m)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

def write_terrain_file(context, filepath, object, depsgraph, scene,
               EXPORT_APPLY_MODIFIERS=True,
               EXPORT_TERRAIN_MATRIX=None,
               EXPORT_PATH_MODE='AUTO',
               EXPORT_NORMALS=False,
               progress=ProgressReport(),
               ):
    """
    Basic write function. The context and options must be already set
    This can be accessed externaly
    eg.
    write( 'c:\\test\\foobar.obj', Blender.Object.GetSelected() ) # Using default options.
    """

    def name_compat(name):
        if name is None:
            return 'None'
        else:
            return name.replace(' ', '_')

    def veckey3d(v):
        return round(v.x, 4), round(v.y, 4), round(v.z, 4)

    def veckey2d(v):
        return round(v[0], 4), round(v[1], 4)

    with ProgressReport(context.window_manager) as progress1:
        with open(filepath, "w", encoding="utf8", newline="\n") as f:
            fw = f.write

            progress1.enter_substeps(1)

            obs = [(object, object.matrix_world)]
            if object.is_instancer:
                obs += [(dup.instance_object.original, dup.matrix_world.copy())
                        for dup in depsgraph.object_instances
                        if dup.parent and dup.parent.original == object]

            progress1.enter_substeps(len(obs))
            for ob, ob_mat in obs:
                with ProgressReportSubstep(progress1, 6) as subprogress2:
                    uv_unique_count = no_unique_count = 0

                    ob_for_convert = ob.evaluated_get(depsgraph) if EXPORT_APPLY_MODIFIERS else ob.original

                    try:
                        me = ob_for_convert.to_mesh()
                    except RuntimeError:
                        me = None

                    if me is None:
                        continue

                    me.transform(EXPORT_TERRAIN_MATRIX @ ob_mat)
                    # If negative scaling, we have to invert the normals...
                    if ob_mat.determinant() < 0.0:
                        me.flip_normals()

                    #me_verts = me.vertices[:]

                    sxfunc = lambda v: v[1].co[0]
                    szfunc = lambda v: v[1].co[2]
                    x_verts = [v for v in enumerate(me.vertices)]
                    z_verts = [v for v in enumerate(me.vertices)]
                    x_verts.sort(key=sxfunc)
                    z_verts.sort(key=szfunc)
                    smallest_x = x_verts[0][1].co[0]
                    largest_x = x_verts[-1][1].co[0]

                    row = round(sqrt( len(me.vertices) ))-1
                    quad_size = (largest_x-smallest_x)/row
                    segments = scene.pbd_prop.terrain_segment_count
                    resolution = round(row/segments)
                    fw("define([],function(){return{\"header\":{\"model_type\":\"height_map\",")
                    fw("\"row\":%d,\"column\":%d,\"quad_size\":%s,\"resolution\":%d},\"height_map\":[\n" % (segments, segments, quad_size, resolution))

                    # Make our own list so it can be sorted to reduce context switching
                    face_index_pairs = [(face, index) for index, face in enumerate(me.polygons)]

                    if not (len(face_index_pairs) + len(me.vertices)):  # Make sure there is something to write
                        # clean up
                        bpy.data.meshes.remove(me)
                        continue  # dont bother with this mesh.

                    subprogress2.step()

                    index = 0
                    for i, zv in z_verts:
                        index = 0
                        for w, xv in x_verts:
                            index += 1
                            if xv.co[2] == zv.co[2]:
                                #fw('%.5f %.5f %.5f\n' % (xv.co[:]))
                                fw('%.5f,' % (xv.co[1]))
                                break
                        x_verts.remove(x_verts[index-1])

                    subprogress2.step()
                    # Make the indices global rather then per mesh
                    # clean up
                    ob_for_convert.to_mesh_clear()

            fw("]}})")
            progress1.leave_substeps("Finished writing geometry of '%s'." % object.name)


def makeTerrain(context, filepath,
         output_path="",
         object_name="",
         precision=5,
         terrain_matrix=None,
         use_mesh_modifiers=False,
         use_normals=False,
         path_mode='AUTO',
         ):

    base_name, ext = os.path.splitext(filepath)
    context_name = [base_name, '', '', ext]  # Base name, scene name, frame number, extension
    depsgraph = context.evaluated_depsgraph_get()
    scene = context.scene

    # Exit edit mode before exporting, so current object states are exported properly.
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')

    object = scene.objects[object_name]
    if not object:
        ShowMessageBox("The terrain exporter must have a proper object set", "Unable to export terrain", 'ERROR')
        return False

    if object.parent and object.parent.instance_type in {'VERTS', 'FACES'}:
        ShowMessageBox("The terrain exporter must have a proper object set (is the one set a dupli child?)", "Unable to export terrain", 'ERROR')
        return False

    full_path = ''.join(context_name)

    with ProgressReport(context.window_manager) as p:
        write_terrain_file(context, full_path, object, depsgraph, scene,
                   EXPORT_APPLY_MODIFIERS=use_mesh_modifiers,
                   EXPORT_PATH_MODE=path_mode,
                   EXPORT_TERRAIN_MATRIX=terrain_matrix,
                   EXPORT_NORMALS=use_normals,
                   progress=p
                   )

def make(context,
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
         compression_level=2,
         addition_option="",
         ):

    if not script_path:
        ShowMessageBox("The obj to js conversion script path is not set in the addon preferences", "Cannot export json", 'ERROR')
        return False

    param = ["node", script_path, "-t", str(precision), "-CavP", "-i", input_path, "-o", output_path]

    if ignore_normals:
        param.append("-z")

    if force_texture:
        param.append("-f")

    if include_meta:
        param.append("-m")

    param.append("--compression-level")
    param.append(str(compression_level))

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

    if not compleated.stderr.isspace():
        ShowMessageBox(compleated.stderr, "Unable to run obj to json script", "ERROR")
        return False

    ShowMessageBox(compleated.stdout, "Batten mesh output", "INFO")
    return True
