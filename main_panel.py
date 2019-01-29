import bpy

class PBDPanel(bpy.types.Panel):
    """Tools for the Play Based Directive graphics engine"""

    bl_label = "Text and fonts"
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
        row.operator("scene.pbd_create_text_curve")

        box = layout.box()
        box.label("Font Object Creation")
        col = box.column()
        col.prop(context.scene.pbd_prop, "label_prefix", text="Name prefix")
        col.operator("curve.pbd_create_object")

        box = layout.box()
        box.label("Object Properties")
        col = box.column()
        if context.active_object is not None and context.active_object.type == "MESH":
            col.prop(context.active_object.pbd_prop, "draw_index")
            col.prop(context.active_object.pbd_prop, "json_do_not_draw")
            col.prop(context.active_object.pbd_prop, "json_set_hitbox")

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

        col = box.column()

        if context.scene.pbd_prop.display_conversion:
            col.prop(context.scene.pbd_prop, "convert_to_json", text="Export a JSON file")
            col.separator()
            col = box.column()
            col.active = context.scene.pbd_prop.convert_to_json
            col.prop(context.scene.pbd_prop, "json_precision", text="Data precision")
            col.prop(context.scene.pbd_prop, "json_input_path")
            col.separator()
            col.prop(context.scene.pbd_prop, "json_output_path")
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
            if context.scene.pbd_prop.json_export_type is "1":
                cola.prop(context.active_object.pbd_prop, "json_exact_hover")

        col = box.column()

        col.separator()
        col.operator("export.pbd_file", icon="EXPORT")

def register():

    bpy.utils.register_class(PBDPanel)

def unregister():

    bpy.utils.unregister_class(PBDPanel)
