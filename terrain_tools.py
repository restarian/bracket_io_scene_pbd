import bpy, os
from math import (sqrt, pi)
from bpy.props import ( EnumProperty, BoolProperty, FloatProperty, StringProperty, EnumProperty, IntProperty )
from mathutils import Vector, Matrix
import bmesh

def ShowMessageBox(message = "", title = "Terrain Verification", icon = 'INFO'):
    message = str(message).replace("\\t", "   ").replace("\t", "   ").replace("\\n", "\n")
    def draw(self, context):
        for m in message.splitlines():
            self.layout.label(text=m)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

class CreateTerrain(bpy.types.Operator):
    """Create a simple terrain starting plane with the correct orientation"""

    bl_idname = "terrain.create_starting"
    bl_label = 'Create Starting Terrain'
    bl_options = {'PRESET'}

    def execute(self, context):

        #from mathutils import Matrix
        #from bpy_extras.io_utils import axis_conversion
        #global_matrix = (Matrix.Scale(context.scene.pbd_prop.world_scale, 4) @ axis_conversion(to_forward="Y", to_up="-Z", ).to_4x4())
        bpy.ops.mesh.primitive_plane_add(location=(0,0,0), rotation=(-90*(pi/180),0,0))
    #    me.transform(global_matrix @ ob_matrix)
        return {"FINISHED"}

def r(num):
    return round(num*10)/10


class VerifyTerrain(bpy.types.Operator):
    """Create a simple terrain starting plane with the correct orientation"""

    bl_idname = "terrain.verify"
    bl_label = 'Error Check Terrain'
    bl_options = {'PRESET'}

    def execute(self, context):

        if context.scene.pbd_prop.terrain_use_active_object:
            terrain_obj = context.active_object
        else:
            terrain_obj = context.scene.objects[context.scene.pbd_prop.terrain_object.strip()]

        if not context.scene.pbd_prop.terrain_use_mesh_modifiers and terrain_obj.type != "MESH":
            ShowMessageBox("An improper terrain object is in use. It should be a mesh object.", "Terrain has errors", "ERROR")
            return {"FINISHED"}

        depsgraph = context.evaluated_depsgraph_get()
        ob_for_convert = terrain_obj.evaluated_get(depsgraph) if context.scene.pbd_prop.terrain_use_mesh_modifiers else terrain_obj.original

        try:
            me = ob_for_convert.to_mesh()
        except RuntimeError:
            ShowMessageBox("An improper terrain object is in use. It should result in a mesh object after mesh modifiers are applied.", "Terrain has errors", "ERROR")
            return {"FINISHED"}

        ob_matrix = ob_for_convert.matrix_world

        from mathutils import Matrix
        from bpy_extras.io_utils import axis_conversion
        #global_matrix = (Matrix.Scale(context.scene.pbd_prop.world_scale, 4) @ axis_conversion(to_forward="Y", to_up="-Z", ).to_4x4())
        global_matrix = (Matrix.Scale(1, 4) @ axis_conversion(to_forward="Y", to_up="-Z", ).to_4x4())
        me.transform(global_matrix @ ob_matrix)

        # If negative scaling, we have to invert the normals...
        if ob_matrix.determinant() < 0.0:
            me.flip_normals()

        sfunc = lambda v: ( r(v.co[2]), r(v.co[0]) )
        verts = [v for q,v in enumerate(me.vertices)]
        verts.sort(key=sfunc)
        smallest_x = r(verts[0].co[0])
        largest_x = r(verts[-1].co[0])
        smallest_z = r(verts[0].co[2])
        largest_z = r(verts[-1].co[2])
        expected_quad_size = r(r(verts[1].co[0]) - r(verts[0].co[0]))
        last = smallest_x

        resolution = sqrt( len(verts) ) - 1
        if round(resolution) != sqrt( len(verts) ) - 1:
            ShowMessageBox("Terrain has an odd number of verticies.", "Terrain has errors", "ERROR")
            return {"FINISHED"}

        # Check for grid conformity and highlight all bad verticies
        bad_vert = []
        prev = verts[0].co
        for v in verts:
            if r(v.co[0]) == smallest_x:
                last = smallest_x
            elif r(v.co[0]) - last != expected_quad_size:
                bad_vert.append((prev))
            else:
                last = r(v.co[0])
            prev = v.co

        """
        for v in verts:
            if r(v.co[0]) == largest_x:
                last = r(v.co[2])
            if r(v.co[2]) == smallest_z:
                continue
            print(v.co[2], last)
            if r(v.co[2]) - last != expected_quad_size:
                bad_vert.append((v.co))
                """

        last_select = terrain_obj.select_get()
        terrain_obj.select_set(False)
        bpy.ops.object.mode_set(mode = 'OBJECT')

        #for em in context.scene.pbd_prop.emp:
            #em.select_set(True)
            #bpy.ops.object.delete()

        #context.scene.pbd_prop.emp = []
        if context.scene.pbd_prop.terrain_add_empty and (len(bad_vert) < 50 or len(bad_vert) < resolution):
            for v in bad_vert:
                bpy.ops.object.empty_add(type='SPHERE', radius=0.1, align='WORLD', location=(v[0], v[1], v[2]), rotation=(0, 0, 0))
                #context.scene.pbd_prop.emp.append(context.scene.active_object)

        #terrain_obj.select_set(True)

        if len(bad_vert):
            ShowMessageBox("Terrain verticies are not in a square grid along the X and Z axis.", "Terrain has errors", "ERROR")
            return {"FINISHED"}


        ShowMessageBox("Terrain object look good :)")
        return {"FINISHED"}

class GetTerrainOrientation(bpy.types.Operator):
    """Test Operator"""

    bl_idname = "terrain.orientation_test"
    bl_label = "Terrain orientation test"
    bl_options = {'PRESET'}

    @classmethod
    def poll(cls, context):
        # Check if the current view is a 3D View
        return bpy.context.area.type == "VIEW_3D"

    def execute(self, context):

        # Get the current object data
        object = bpy.context.object
        object_data = bpy.context.object.data
        object_bmesh = bmesh.from_edit_mesh(object_data)

        # Declare some variables
        verts_list = []
        verts_co_sum = Vector()

        # Get selected vertices in a list
        for vert in object_bmesh.verts:
            if vert.select == True:
                verts_list.append(vert)

        if len(verts_list) < 1:
            print ("Nothing is selected")

        else:
            # Get a sum of vertices location vectors
            for vert in verts_list:
                verts_co_sum += vert.co

            # Get an average location of the selected vertices
            verts_co_average = verts_co_sum / len(verts_list)

            # Get the transform orientation in the current view. GLOBAL, LOCAL, NORMAL etc.
            t_orientation = bpy.context.scene.transform_orientation_slots[0].type

            # Create an empty, link it to the scene and show its axis
            if bpy.data.objects.get("ManipulatorEmtpy"):
                bpy.data.objects.remove(bpy.data.objects["ManipulatorEmtpy"], do_unlink = True)

            manipulator_empty = bpy.data.objects.new("ManipulatorEmtpy", None)
            scene_collection = context.layer_collection.collection
            scene_collection.objects.link(manipulator_empty)
            manipulator_empty.show_axis = True

            # Set the location of the ManipulatorEmpty to the average vertex location
            # and orient it using the object orientation. Works for LOCAL and GLOBAL transform orientations
            # when pivot point settings are set to "Median Point" or "Individual Origins"

            if t_orientation == "LOCAL":
                new_matrix = object.matrix_world @ Matrix.Translation(verts_co_average)
                manipulator_empty.matrix_world = new_matrix

            elif t_orientation == "GLOBAL":
                new_matrix = object.matrix_world @ Matrix.Translation(verts_co_average)
                manipulator_empty.matrix_world = new_matrix
                manipulator_empty.rotation_euler = ( 0, 0, 0 )


        return {'FINISHED'}

classes = (
    GetTerrainOrientation,
    CreateTerrain,
    VerifyTerrain,
    )

register, unregister = bpy.utils.register_classes_factory(classes)
