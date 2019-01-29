import bpy

class ResetCharacter(bpy.types.Operator):
    """vided"""

    bl_idname = "scene.pbd_reset_character"
    bl_label = "Reset text"
    bl_options = {"REGISTER"}

      #description = "All characters which are contained in the language. This is used for the reset button as well",
    def execute(self, context):
        context.scene.pbd_prop.character_array = context.user_preferences.addons["io_scene_json"].preferences.alphabet
        return {'FINISHED'}

class CreateTextCurve(bpy.types.Operator):
    """Create a text curve character array to use for converting to a mesh using the input characters provided"""

    bl_idname = "scene.pbd_create_text_curve"
    bl_label = "Created text curve"

    @classmethod
    def poll(cls, context):
        return context.object is None or context.object.mode == "OBJECT"

    def add_text_characters(self, context):
        bpy.ops.object.text_add()
        ob=bpy.context.object
        ob.data.body = context.scene.pbd_prop.character_array
        return len(ob.data.body)

    def execute(self, context):
        num = self.add_text_characters(context)
        self.report({'INFO'}, "Sucessfully added " + str(num) + " text curve characters.")
        return {'FINISHED'}

def register():

    bpy.utils.register_class(CreateTextCurve)
    bpy.utils.register_class(ResetCharacter)

def unregister():

    bpy.utils.unregister_class(CreateTextCurve)
    bpy.utils.unregister_class(ResetCharacter)

if __name__ == "__main__":
    register()
