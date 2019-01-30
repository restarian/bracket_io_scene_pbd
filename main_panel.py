import bpy

class PBDPanel(bpy.types.Panel):
    """Tools for the Play Based Directive graphics engine"""

    bl_label = "Play Based Directive"
    bl_idname = "OBJECT_PT_pbd_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "PBD"

    def draw(self, context):

        layout = self.layout
        box = layout.box()
        box.label("Font Text Creation")
        split = box.split(percentage=0.29)
        split.operator("scene.pbd_reset_character")
        split.prop(context.scene.pbd_prop, 'character_array', text="")
        row = box.row()
        row.operator("scene.pbd_create_text_curve", text="Create text curve")


        box = layout.box()
        box.label("Font Object Creation")
        col = box.column()
        col.prop(context.scene.pbd_prop, "label_prefix", text="Name prefix")
        col.operator("curve.pbd_create_object", text="Convert font to objects")


        if context.active_object is not None and context.active_object.type == "MESH":
            box = layout.box()
            box.label("Object Properties")
            col = box.column()
            col.prop(context.active_object.pbd_prop, "draw_index")
            row = box.row()
            row.prop(context.active_object.pbd_prop, "do_not_draw")
            row.prop(context.active_object.pbd_prop, "set_hitbox")


        if context.active_object is not None and context.active_object.active_material is not None:
            box = layout.box()
            box.label("Material Properties")
            row = box.row()
            row.prop(context.active_object.active_material.pbd_prop, "do_not_draw")
            row.prop(context.active_object.active_material.pbd_prop, "set_hitbox")

        box = layout.box()
        box.label("File Exporting")
        col = box.column()

        if not context.scene.pbd_prop.json_input_path:
            col.prop(context.scene.pbd_prop, "use_draw_order", text="Use draw order index")
            col.prop(context.scene.pbd_prop, "use_selection")
            col.prop(context.scene.pbd_prop, "use_animation")

        col.prop(context.scene.pbd_prop, "display_conversion", text="JSON PBD Exporting",
            icon="TRIA_DOWN" if context.scene.pbd_prop.display_conversion else "TRIA_RIGHT",
            emboss=False
        )

        if context.scene.pbd_prop.display_conversion:
            col = box.column()
            col.prop(context.scene.pbd_prop, "convert_to_json", text="Export a JSON file")
            col.separator()

            row = box.row()
            row.active = context.scene.pbd_prop.convert_to_json
            row.prop(context.scene.pbd_prop, "json_ignore_normals", text="Ignore normals")
            row.prop(context.scene.pbd_prop, "json_include_meta", text="Include meta")

            row = box.row()
            row.active = context.scene.pbd_prop.convert_to_json

            row.prop(context.scene.pbd_prop, "json_force_texture", text="Overwrite textures")
            row.prop(context.scene.pbd_prop, "json_precision", text="Data precision")

            col = box.column()
            col.active = context.scene.pbd_prop.convert_to_json
            col.prop(context.scene.pbd_prop, "json_additional_option")

            #col.prop(context.scene.pbd_prop, "json_input_path", icon="IMPORT")
            col.separator()
            col.prop(context.scene.pbd_prop, "json_asset_root")
            row = box.row()
            row.active = context.scene.pbd_prop.convert_to_json
            row.prop(context.scene.pbd_prop, "json_export_type", expand=True, emboss=True)
            cola = box.column()

            if not context.scene.pbd_prop.convert_to_json:
                cola.active = False
            #elif context.scene.pbd_prop.json_export_type is not "1":
                #cola.active = False

            #if True and context.scene.pbd_prop.json_export_type is "widget" and context.active_object is not None and context.active_object.type == "MESH":
            cola.prop(context.scene.pbd_prop, "json_output_path", icon="SAVE_COPY")

        col = box.column()
        col.separator()
        col.operator("export.pbd_file", text="Export", icon="EXPORT")

        box = layout.box()
        box.label("PBD OBJ Importing")
        col = box.column()
        col.operator("import.pbd_obj_scene", text="Import", icon="IMPORT")



def register():

    bpy.utils.register_class(PBDPanel)

def unregister():

    bpy.utils.unregister_class(PBDPanel)
