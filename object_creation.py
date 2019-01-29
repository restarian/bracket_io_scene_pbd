import bpy

class ConvertToObject(bpy.types.Operator):
    """Converts a text curve to a mesh and renames the objects using the label prefix input"""

    bl_idname = "curve.pbd_create_object"
    bl_label = "Convert and label"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == "FONT" and context.active_object.mode == "OBJECT"

    def create_text_object(self, context):
        x = 0
        curve = context.active_object
        arr = curve.data.body
        for c in arr:
            bpy.ops.object.text_add()
            ob=context.object
            ob.data.body = c
            ob.data.offset = curve.data.offset
            ob.data.bevel_depth = curve.data.bevel_depth
            ob.data.extrude = curve.data.extrude
            ob.data.font = curve.data.font
            ob.data.shear = curve.data.shear
            ob.data.size = curve.data.size
            ob.data.align_y = curve.data.align_y
            ob.data.offset_x = curve.data.offset_x
            ob.data.offset_y = curve.data.offset_y
            ob.data.use_fill_deform = curve.data.use_fill_deform
            ob.data.small_caps_scale = curve.data.small_caps_scale

            bpy.ops.object.convert(target="MESH")
            ob=context.object
            ob.location.x += x
            ob.name = context.scene.pbd_prop.label_prefix+c
            x += 1

        bpy.ops.object.select_all(action='DESELECT')
        curve.select = True
        bpy.ops.object.delete()

        self.report({'INFO'}, "Sucessfully created " + str(len(arr)) + " character objects.")

    def execute(self, context):
        self.create_text_object(context)
        return {'FINISHED'}

def register():

    bpy.utils.register_class(ConvertToObject)

def unregister():

    bpy.utils.unregister_class(ConvertToObject)

if __name__ == "__main__":
    register()
