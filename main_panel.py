import bpy

class WorldSettings(bpy.types.Panel):
    """Seeting which apply generically to all other tools in this suite."""

    bl_label = "World Settings"
    bl_idname = "OBJECT_PT_world_pnnel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Play Based Directive"

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="World Settings")
        row = box.row()
        row.prop(context.scene.pbd_prop, "world_scale", text="World scale")
        box.prop_search(context.scene.pbd_prop, "corralate_terrain_name",  context.scene, "objects")

class TerrainTools(bpy.types.Panel):
    """Tools to create terrains for the Play Based Directive graphics engine"""

    bl_label = "Terrains Tools"
    bl_idname = "OBJECT_PT_terrain_pnnel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Play Based Directive"

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Terrain Creation")
        col = box.column()
        col.operator("terrain.create_starting", text="Create a starting terrain")
        col.scale_y = 1.3

        box = layout.box()
        box.label(text="Terrain Height Map Exporting")
        col = box.column()
        terrain_obj = None
        if context.scene.pbd_prop.terrain_use_active_object:
            terrain_obj = context.active_object
        elif len(context.scene.pbd_prop.terrain_object.strip()):
            terrain_obj = context.scene.objects[context.scene.pbd_prop.terrain_object.strip()]

        has_terrain = terrain_obj is not None and terrain_obj.type == "MESH"
        #col.prop(context.scene.pbd_prop, "terrain_segment_count", text="Number of segments")
        row = box.row()
        row.prop(context.scene.pbd_prop, "terrain_use_active_object", text="Use active object for terrain")
        if not context.scene.pbd_prop.terrain_use_active_object:
            box.prop_search(context.scene.pbd_prop, "terrain_object",  context.scene, "objects")

        if has_terrain:

            col = box.column()
            col.separator()
            col.prop(terrain_obj.pbd_prop, "terrain_name", text="Terrain name")
            col.prop(terrain_obj.pbd_prop, "terrain_segment_count", expand=False)
            col.separator()

            row = box.row()
            row.prop(context.scene.pbd_prop, "terrain_use_mesh_modifiers", text="Apply mesh modifiers")
            row = box.row()
            row.active = False
            row.prop(context.scene.pbd_prop, "terrain_use_normals", text="Export normals")

            col = box.column()
            col.separator()
            col.operator("terrain.verify", text="Check terrain for errors")
            col.separator()
            col.operator("export.pbd_terrain_file", text="Export Terrain Javascript File", icon="EXPORT")
            col.scale_y = 1.3

class ModelImport(bpy.types.Panel):
    """Tools for the Play Based Directive graphics engine"""

    bl_label = "Importing"
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

    bl_label = "Fonts and Text"
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

    bl_label = "Models, Widgets and Fonts"
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

            row = box.row(align=True)
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
            col = row.column()
            row = col.row()
            row.active = context.active_object.pbd_prop.collision_detection
            row.prop(context.active_object.pbd_prop, "collision_bounding", text="Collision bounds only")
            row = box.row(align=True)
            row.active = context.active_object.pbd_prop.collision_detection and not context.active_object.pbd_prop.collision_bounding
            row.prop_search(context.active_object.pbd_prop, "proxy_object",  context.scene, "objects", text="Collision proxy object")

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

        row = box.row()
        row.prop(context.scene.pbd_prop, "use_draw_order", text="Use draw order index")
        row.prop(context.scene.pbd_prop, "use_animation")
        row = box.row()
        row.prop(context.scene.pbd_prop, "use_selection")
        row.prop(context.scene.pbd_prop, "model_use_mesh_modifiers", text="Apply modifiers")
        row = box.row()
        row.active = bool(len(context.scene.pbd_prop.corralate_terrain_name.strip()))
        row.prop(context.scene.pbd_prop, "corralate_model_terrain", text="World Corralatation")


        js_checked = " FIle"
        has_script = bool(len(context.preferences.addons["bracket_io_scene_pbd"].preferences.script_path))
        if has_script:
            col = box.column()
            col.prop(context.scene.pbd_prop, "convert_to_json", text="Export Javascript File")
            col.separator()

            if context.scene.pbd_prop.convert_to_json:
                js_checked = " and Javascript File"

                row = box.row()
                row.prop(context.scene.pbd_prop, "json_export_type", expand=True, emboss=True)

                row = box.row()
                row.prop(context.scene.pbd_prop, "model_name", text="Model Name")

                row = box.row()
                row.prop(context.scene.pbd_prop, "json_ignore_normals", text="Ignore all normals")
                row.prop(context.scene.pbd_prop, "json_ignore_uv_map", text="Ignore UV maps")

                row = box.row()
                row.prop(context.scene.pbd_prop, "json_force_texture", text="Overwrite textures")
                row.prop(context.scene.pbd_prop, "json_include_meta", text="Include meta")

                row = box.row()
                row.prop(context.scene.pbd_prop, "json_precision", text="Data precision")
                row.prop(context.scene.pbd_prop, "json_compressed", text="Compression level")


                col = box.column()
                col.separator()
                col.prop(context.scene.pbd_prop, "json_additional_option")
                col.prop(context.scene.pbd_prop, "json_asset_root", text="Assest server root")
                col.prop(context.scene.pbd_prop, "json_texture_subdir", text="Textures sub-directory")

                col = box.column()
                col.scale_y = 1.5
                col.prop(context.scene.pbd_prop, "json_output_path", text='Destination directory')

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

    bpy.utils.register_class(WorldSettings)
    bpy.utils.register_class(TerrainTools)
    bpy.utils.register_class(FontCreation)
    bpy.utils.register_class(ModelExport)
    bpy.utils.register_class(ModelImport)

def unregister():

    bpy.utils.unregister_class(ModelImport)
    bpy.utils.unregister_class(ModelExport)
    bpy.utils.unregister_class(FontCreation)
    bpy.utils.unregister_class(TerrainTools)
    bpy.utils.unregister_class(WorldSettings)
