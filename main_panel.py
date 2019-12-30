import bpy

class PBDPanel(bpy.types.Panel):
    """Tools for the Play Based Directive graphics engine"""

    bl_label = "Play Based Directive"
    bl_idname = "OBJECT_PT_pbd_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Play Based Directive"

    def draw(self, context):

        layout = self.layout
        box = layout.box()
        box.label(text="Font-Text Creation")
        split = box.split(factor=0.29)
        split.operator("scene.pbd_reset_character")
        split.prop(context.scene.pbd_prop, 'character_array', text="")
        row = box.row()
        row.operator("scene.pbd_create_text_curve", text="Create text curve")

        box = layout.box()
        lbl = "Font-Object Creation"
        if context.active_object is not None and context.active_object.type == "FONT" and context.active_object.mode == "OBJECT":
            lbl += " - " + str(context.active_object.name)
        box.label(text=lbl)
        col = box.column()
        col.prop(context.scene.pbd_prop, "label_prefix", text="Name prefix")
        col.prop(context.scene.pbd_prop, "delete_after")
        col.operator("curve.pbd_create_object", text="Convert font to objects")

        if context.active_object is not None and context.active_object.type == "MESH":
            box = layout.box()
            box.label(text="Object Properties")
            row = box.row()
            row.prop(context.active_object.pbd_prop, "cull_face", text="")
            row.prop(context.active_object.pbd_prop, "draw_index")
            row = box.row()
            row.prop(context.active_object.pbd_prop, "display", text="Display")

            row = box.row()
            row.prop(context.active_object.pbd_prop, "mouse_region", text="Mouse detection")
            col = row.column()
            row = col.row()
            row.active = context.active_object.pbd_prop.mouse_region
            row.prop(context.active_object.pbd_prop, "detect_bounding", text="Detect bounds only")

            row = box.row()
            row.prop(context.active_object.pbd_prop, "clip_region", text="Clip area")
            col = row.column()
            row = col.row()
            row.active = context.active_object.pbd_prop.clip_region
            row.prop(context.active_object.pbd_prop, "clip_bounding", text="Clip bounds only")

        if context.active_object is not None and context.active_object.active_material is not None:
            box = layout.box()
            box.label(text="Material Properties")
            row = box.row()
            split = box.split(factor=0.48)
            split.prop(context.active_object.active_material.pbd_prop, "cull_face", text="")
            row = box.row()
            row.prop(context.active_object.active_material.pbd_prop, "display", text="Display")

        box = layout.box()
        box.label(text="File Exporting")
        col = box.column()

        col.prop(context.scene.pbd_prop, "use_draw_order", text="Use draw order index")
        col.prop(context.scene.pbd_prop, "use_selection")
        col.prop(context.scene.pbd_prop, "use_animation")

        if len(context.preferences.addons["bracket_io_scene_pbd"].preferences.script_path):
            col.prop(context.scene.pbd_prop, "display_conversion", text="JSON PBD Exporting",
                icon="TRIA_DOWN" if context.scene.pbd_prop.display_conversion else "TRIA_RIGHT",
                emboss=False
            )

        if context.scene.pbd_prop.display_conversion and len(context.preferences.addons["bracket_io_scene_pbd"].preferences.script_path):
            col = box.column()
            col.prop(context.scene.pbd_prop, "convert_to_json", text="Export a JSON file")
            col.separator()

            row = box.row()
            row.active = context.scene.pbd_prop.convert_to_json
            row.prop(context.scene.pbd_prop, "json_export_type", expand=True, emboss=True)
            row = box.row()
            row.active = context.scene.pbd_prop.convert_to_json
            row.prop(context.scene.pbd_prop, "json_ignore_normals", text="Ignore normals")
            row.prop(context.scene.pbd_prop, "json_include_meta", text="Include meta")

            row = box.row()
            row.active = context.scene.pbd_prop.convert_to_json

            row.prop(context.scene.pbd_prop, "json_force_texture", text="Overwrite textures")
            row.prop(context.scene.pbd_prop, "json_precision", text="Data precision")
            row = box.row()
            row.active = context.scene.pbd_prop.convert_to_json
            row.prop(context.scene.pbd_prop, "json_compressed", text="Compression level")

            col = box.column()
            col.active = context.scene.pbd_prop.convert_to_json

            col.prop(context.scene.pbd_prop, "json_asset_root", text="Assest server root")
            col.prop(context.scene.pbd_prop, "json_texture_subdir", text="Textures sub-directory")
            col.prop(context.scene.pbd_prop, "json_output_path", text='JSON destination directory')

            col.separator()
            col.prop(context.scene.pbd_prop, "json_additional_option")
        else:
            col.separator()
            col.label(text="..add batten_mesh.js to enable json exporting..")


        col.separator()
        col = box.column()
        col.separator()
        col.operator("export.pbd_file", text="-- EXPORT --", icon="EXPORT")

        col.separator()
        col.separator()
        row = box.row()
        row.operator("export.json_from_obj", text="Export .js (pbd) from .obj", icon="EXPORT")
        row.prop(context.scene.pbd_prop, "json_import_path", text=".obj")

        box = layout.box()
        box.label(text="Importing")
        col = box.column()
        col.operator("import.pbd_obj_scene", text="Import from .obj", icon="IMPORT")

def register():

    bpy.utils.register_class(PBDPanel)

def unregister():

    bpy.utils.unregister_class(PBDPanel)
