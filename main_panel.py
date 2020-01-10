import bpy


class TerrianExport(bpy.types.Panel):
    """Tools for the Play Based Directive graphics engine"""

    bl_label = "Terrain Tools"
    bl_idname = "OBJECT_PT_terrain_pnnel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Play Based Directive"

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Terrain height Map exporting")
        col = box.column()
        #col.prop(context.scene.pbd_prop, "terrain_segment_count", text="Number of segments")
        box.prop_search(context.scene.pbd_prop, "terrain_object",  context.scene, "objects")
        col = box.column()
        col.active = not not context.scene.pbd_prop.terrain_object
        col.prop(context.scene.pbd_prop, "terrain_segment_count", expand=False)
        col.prop(context.scene.pbd_prop, "terrain_name", text="Terrain name")

        col.separator()
        col = box.column()
        col.operator("export.pbd_terrain_file", text="Export Terrain Javascript File", icon="EXPORT")
        col.scale_y = 1.3

class ModelImport(bpy.types.Panel):
    """Tools for the Play Based Directive graphics engine"""

    bl_label = "Model Importing"
    bl_idname = "OBJECT_PT_import_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Play Based Directive"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Import Obj with PBD properties.")
        col = box.column()
        col.operator("import.pbd_obj", text="Import From Obj", icon="IMPORT")


class FontCreation(bpy.types.Panel):
    """Tools for the Play Based Directive graphics engine"""

    bl_label = "Font Tools"
    bl_idname = "OBJECT_PT_font_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Play Based Directive"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):

        layout = self.layout
        box = layout.box()
        box.label(text="Font-Text Creation")
        split = box.split(factor=0.29)
        split.operator("scene.pbd_reset_character")
        split.prop(context.scene.pbd_prop, 'character_array', text="")
        col = box.column()
        col.operator("scene.pbd_create_text_curve", text="Create Text Curve")
        col.scale_y = 1.3

        box = layout.box()
        lbl = "Font-Object Creation"
        if context.active_object is not None and context.active_object.type == "FONT" and context.active_object.mode == "OBJECT":
            lbl += " - " + str(context.active_object.name)
        box.label(text=lbl)
        col = box.column()
        col.prop(context.scene.pbd_prop, "label_prefix", text="Name prefix")
        col.prop(context.scene.pbd_prop, "delete_after", text="Delete text curve after conversion")
        col = box.column()
        col.operator("curve.pbd_create_object", text="Convert Font to Objects")
        col.scale_y = 1.3

class ModelExport(bpy.types.Panel):
    """Tools for the Play Based Directive graphics engine"""

    bl_label = "Model Exporting"
    bl_idname = "OBJECT_PT_pbd_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Play Based Directive"

    def draw(self, context):

        layout = self.layout
        if context.active_object is not None and context.active_object.type == "MESH":
            box = layout.box()
            box.label(text="Object Properties")
            row = box.row()
            row.prop(context.active_object.pbd_prop, "cull_face", text="")
            row.prop(context.active_object.pbd_prop, "draw_index")
            row = box.row()
            row.prop(context.active_object.pbd_prop, "display", text="Display")
            row.prop(context.active_object.pbd_prop, "include_normals", text="Include normals")

            row = box.row()
            row.prop(context.active_object.pbd_prop, "mouse_region", text="Mouse detection")
            col = row.column()
            row = col.row()
            row.active = context.active_object.pbd_prop.mouse_region
            row.prop(context.active_object.pbd_prop, "mouse_bounding", text="Detect bounds only")

            row = box.row()
            row.prop(context.active_object.pbd_prop, "clip_region", text="Clip area")
            col = row.column()
            row = col.row()
            row.active = context.active_object.pbd_prop.clip_region
            row.prop(context.active_object.pbd_prop, "clip_bounding", text="Clip bounds only")

            row = box.row(align=True)
            row.prop(context.active_object.pbd_prop, "collision_detection", text="Collision detection")
            box.prop_search(context.active_object.pbd_prop, "proxy_object",  context.scene, "objects", text="Collision proxy object")

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
        col.prop(context.scene.pbd_prop, "model_type", text="Model Name")

        js_checked = " FIle"
        has_script = bool(len(context.preferences.addons["bracket_io_scene_pbd"].preferences.script_path))
        if has_script:
            col = box.column()
            col.prop(context.scene.pbd_prop, "convert_to_json", text="Export Javascript File")
            col.separator()

            if context.scene.pbd_prop.convert_to_json:
                js_checked = " and Javascript File"

                type = bool(context.scene.pbd_prop.json_export_type)

                row = box.row()
                row.active = type
                row.prop(context.scene.pbd_prop, "json_export_type", expand=True, emboss=True)

                row = box.row()
                row.active = type
                row.prop(context.scene.pbd_prop, "json_ignore_normals", text="Ignore all normals")
                row.prop(context.scene.pbd_prop, "json_include_meta", text="Include meta")

                row = box.row()
                row.active = type
                row.prop(context.scene.pbd_prop, "json_force_texture", text="Overwrite textures")
                row.prop(context.scene.pbd_prop, "json_precision", text="Data precision")

                col = box.column()
                col.active = type
                col.prop(context.scene.pbd_prop, "json_compressed", text="Compression level")
                col.separator()
                col.prop(context.scene.pbd_prop, "json_additional_option")
                col.prop(context.scene.pbd_prop, "json_asset_root", text="Assest server root")
                col.prop(context.scene.pbd_prop, "json_texture_subdir", text="Textures sub-directory")

                col = box.column()
                col.active = type
                col.scale_y = 1.5
                col.prop(context.scene.pbd_prop, "json_output_path", text='Js destination directory')

        if not has_script:
            col = box.column()
            col.separator()
            col.label(text="..add Batten_mesh convert.js to enable js exporting-")

        col = box.column()
        col.separator()
        col.operator("export.pbd_file", text="Export Obj"+js_checked, icon="EXPORT")
        col.scale_y = 1.5
        col.separator()
        col.separator()

        if has_script:
            row = box.row()
            row.operator("export.json_from_obj", text="Export Js from Obj", icon="EXPORT")
            row.prop(context.scene.pbd_prop, "json_import_path", text=".obj")

def register():

    bpy.utils.register_class(FontCreation)
    bpy.utils.register_class(ModelExport)
    bpy.utils.register_class(TerrianExport)
    bpy.utils.register_class(ModelImport)

def unregister():

    bpy.utils.unregister_class(ModelImport)
    bpy.utils.unregister_class(TerrianExport)
    bpy.utils.unregister_class(ModelExport)
    bpy.utils.unregister_class(FontCreation)
