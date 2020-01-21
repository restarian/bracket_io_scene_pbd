import bpy
#from mathutils import Vector, Matrix
from math import pi

class CreateTerrain(bpy.types.Operator):
    """Create a simple terrain starting plane with the correct orientation"""

    bl_idname = "terrain.create_starting"
    bl_label = 'Create Starting Terrain'
    bl_options = {'PRESET'}

    def execute(self, context):

        #from mathutils import Matrix
        #from bpy_extras.io_utils import axis_conversion
        #global_matrix = (Matrix.Scale(context.scene.pbd_prop.world_scale, 4) @ axis_conversion(to_forward="Y", to_up="-Z", ).to_4x4())

        c_ob = context.collection.pbd_prop if context.scene.pbd_prop.export_object_with == 'collection' else context.scene.pbd_prop

        bpy.ops.mesh.primitive_plane_add(location=(0,0,0), rotation=(-90*(pi/180),0,0))

        if c_ob.terrain_add_multires:
            bpy.ops.object.modifier_add(type='MULTIRES')

        return {"FINISHED"}


classes = (
    CreateTerrain,
    )

register, unregister = bpy.utils.register_classes_factory(classes)
