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

def write_file(context, filepath, objects, depsgraph, scene,
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


            #if scene.pbd_prop:
                #if not scene.pbd_prop.model_type.isspace():
                    #fw('header_model_type %s\n' % scene.pbd_prop.model_type)
            totverts = totuvco = totno = 1
            face_vert_index = 1
            copy_set = set()

            s_obj = objects

            # Get all meshes
            progress1.enter_substeps(len(objects))
            for i, ob_main in enumerate(s_obj):
                # ignore dupli children
                if ob_main.parent and ob_main.parent.instance_type in {'VERTS', 'FACES'}:
                    progress1.step("Ignoring %s, dupli child..." % ob_main.name)
                    continue

                obs = [(ob_main, ob_main.matrix_world)]
                if ob_main.is_instancer:
                    obs += [(dup.instance_object.original, dup.matrix_world.copy())
                            for dup in depsgraph.object_instances
                            if dup.parent and dup.parent.original == ob_main]
                    # ~ print(ob_main.name, 'has', len(obs) - 1, 'dupli children')

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

                        faceuv = False

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
                        fw("define([],function(){return{\"header\":{\"model_type\":\"terrain\",")
                        fw("\"row\":%d,\"column\":%d,\"quad_size\":%s},\"height_map\":[" % (row, row, quad_size))

                        me_verts = []
                        #me_verts = [v for k,v in ]

                        # Make our own list so it can be sorted to reduce context switching
                        face_index_pairs = [(face, index) for index, face in enumerate(me.polygons)]

                        if not (len(face_index_pairs) + len(me.vertices)):  # Make sure there is something to write
                            # clean up
                            bpy.data.meshes.remove(me)
                            continue  # dont bother with this mesh.

                        if EXPORT_NORMALS and face_index_pairs:
                            me.calc_normals_split()
                            # No need to call me.free_normals_split later, as this mesh is deleted anyway!

                        loops = me.loops

                        smooth_groups_tot = (), 0

                        materials = me.materials[:]
                        material_names = [m.name if m else None for m in materials]

                        # avoid bad index errors
                        if not materials:
                            materials = [None]
                            material_names = [name_compat(None)]


                        # Set the default mat to no material and no image.
                        contextMat = 0, 0  # Can never be this, so we will label a new material the first chance we get.
                        contextSmooth = None  # Will either be true or false,  set bad to force initialization switch.

                        name1 = ob.name
                        subprogress2.step()

                        # Vert
                        bb = len(x_verts)
                        bb = round(bb / 2)

                        for a in range(bb):
                            fw('%.5f,' % (x_verts[a][1].co[1]))
                            fw('%.5f,' % (z_verts[a][1].co[1]))

                        subprogress2.step()

                        # UV
                        if faceuv:
                            # in case removing some of these dont get defined.
                            uv = f_index = uv_index = uv_key = uv_val = uv_ls = None

                            uv_face_mapping = [None] * len(face_index_pairs)

                            del uv, f_index, uv_index, uv_ls, uv_key, uv_val

                        subprogress2.step()

                        # NORMAL, Smooth/Non smoothed.
                        if EXPORT_NORMALS:
                            no_key = no_val = None
                            normals_to_idx = {}
                            no_get = normals_to_idx.get
                            loops_to_normals = [0] * len(loops)
                            for f, f_index in face_index_pairs:
                                for l_idx in f.loop_indices:
                                    no_key = veckey3d(loops[l_idx].normal)
                                    no_val = no_get(no_key)
                                    if no_val is None:
                                        no_val = normals_to_idx[no_key] = no_unique_count
                                        fw('vn %.4f %.4f %.4f\n' % no_key)
                                        no_unique_count += 1
                                    loops_to_normals[l_idx] = no_val
                            del normals_to_idx, no_get, no_key, no_val
                        else:
                            loops_to_normals = []

                        # Make the indices global rather then per mesh
                        totverts += len(me_verts)
                        totuvco += uv_unique_count
                        totno += no_unique_count

                        # clean up
                        ob_for_convert.to_mesh_clear()

            fw("]}})")
            progress1.leave_substeps("Finished writing geometry of '%s'." % ob_main.name)


def makeTerrain(context, filepath,
         output_path="",
         use_selection=False,
         precision=5,
         compression_level=2,
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

    if use_selection:
        objects = context.selected_objects
    else:
        objects = scene.objects

    full_path = ''.join(context_name)

    with ProgressReport(context.window_manager) as p:
        write_file(context, full_path, objects, depsgraph, scene,
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
