import bpy

class MainSettings(bpy.types.Panel):
    """Settings which apply generically to all other tools in this suite."""

    bl_label = "Main Settings"
    bl_idname = "OBJECT_PT_main_pnnel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Play Based Directive"
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        col = box.column()
        col.label(text="Export objects using:")
        row = box.row()
        row.scale_y = 1.6
        row.prop(context.scene.pbd_prop, "export_object_with", expand=True, emboss=True)

class TerrainTools(bpy.types.Panel):
    """Tools to create terrains for the Play Based Directive graphics engine"""

    bl_label = "Terrains Tools"
    bl_idname = "OBJECT_PT_terrain_pnnel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Play Based Directive"

    def draw(self, context):

        if context.scene.pbd_prop.export_object_with == 'collection':
            c_ob = context.collection.pbd_prop
            c = context.collection
        else:
            c_ob = context.scene.pbd_prop
            c = context.scene

        layout = self.layout
        box = layout.box()
        box.label(text="Terrain Creation")
        col = box.column()
        #col.operator("terrain.orientation_test", text="TEST")
        col.operator("terrain.create_starting", text="Create a starting terrain")
        col.scale_y = 1.3

        box = layout.box()
        box.label(text="Terrain Height Map Exporting")
        col = box.column()
        terrain_obj = None
        if c_ob.terrain_use_active_object:
            terrain_obj = context.active_object
        else:
            t_ob = c_ob.terrain_object.strip()
            if t_ob in c.objects:
                terrain_obj = c.objects[t_obj]

        has_terrain = terrain_obj is not None and terrain_obj.type == "MESH"
        #col.prop(context.scene.pbd_prop, "terrain_segment_count", text="Number of segments")
        row = box.row()
        row.prop(c_ob, "terrain_use_active_object", text="Use active object for terrain")
        if not c_ob.terrain_use_active_object:
            box.prop_search(c_ob, "terrain_object", c, "objects", text="Use terrain object")

        if has_terrain:
            col = box.column()
            col.separator()
            col.prop(terrain_obj.pbd_prop, "name", text="Name")
            col.prop(terrain_obj.pbd_prop, "terrain_segment_count", text="Rows/Columns", expand=False)
            col.separator()

            row = box.row()
            row.prop(c_ob, "terrain_use_mesh_modifiers", text="Apply mesh modifiers")
            row = box.row()
            row.active = False
            row.prop(c_ob, "terrain_use_normals", text="Export normals")

            col = box.column()
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

        c_ob = context.collection.pbd_prop if context.scene.pbd_prop.export_object_with == 'collection' else context.scene.pbd_prop
        layout = self.layout
        box = layout.box()
        box.label(text="Font-Text Creation")
        split = box.split(factor=0.29)
        split.operator("scene.pbd_reset_character")
        split.prop(c_ob, 'character_array', text="")
        col = box.column()
        col.operator("scene.pbd_create_text_curve", text="Create Text Curve")
        col.scale_y = 1.3

        box = layout.box()
        lbl = "Font-Object Creation"
        if context.active_object is not None and context.active_object.type == "FONT" and context.active_object.mode == "OBJECT":
            lbl += " - " + str(context.active_object.name)
        box.label(text=lbl)
        col = box.column()
        col.prop(c_ob, "label_prefix", text="Name prefix")
        row = box.row(align=True)
        row.prop(c_ob, "delete_after", text="Delete text after conversion")
        col = row.column()
        col.active = not c_ob.delete_after
        col.prop(c_ob, "hide_after", text="Hide text after conversion")

        col = box.column()
        col.operator("curve.convert_to_object", text="Convert Font to Objects")
        col.scale_y = 1.3

class ModelExport(bpy.types.Panel):
    """Tools for the Play Based Directive graphics engine"""

    bl_label = "Models, Widgets and Fonts"
    bl_idname = "OBJECT_PT_pbd_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Play Based Directive"

    def draw(self, context):

        c_ob = context.collection if context.scene.pbd_prop.export_object_with == 'collection' else context.scene

        layout = self.layout
        if context.active_object is not None and context.active_object.type == "MESH":
            box = layout.box()
            box.label(text="Object Properties")

            row = box.row(align=True)
            row.prop(context.active_object.pbd_prop, "cull_face", text="")
            row.prop(context.active_object.pbd_prop, "draw_index", text="Draw order index")

            row = box.row(align=True)
            row.prop(context.active_object.pbd_prop, "display", text="Display")
            row.prop(context.active_object.pbd_prop, "include_normals", text="Include normals")

            row = box.row(align=True)
            row.prop(context.active_object.pbd_prop, "mouse_region", text="Mouse detection")
            col = row.column()
            col.active = context.active_object.pbd_prop.mouse_region
            col.prop(context.active_object.pbd_prop, "mouse_bounding", text="Detect bounds only")

            row = box.row(align=True)
            row.prop(context.active_object.pbd_prop, "clip_region", text="Clip area")
            col = row.column()
            col.active = context.active_object.pbd_prop.clip_region
            col.prop(context.active_object.pbd_prop, "clip_bounding", text="Clip bounds only")

            row = box.row(align=True)
            row.prop(context.active_object.pbd_prop, "collision_detection", text="Collision detection")
            col = row.column()
            col.active = context.active_object.pbd_prop.collision_detection
            col.prop(context.active_object.pbd_prop, "collision_bounding", text="Collision bounds only")

            row = box.row(align=True)
            row.active = context.active_object.pbd_prop.collision_detection and not context.active_object.pbd_prop.collision_bounding
            row.prop_search(context.active_object.pbd_prop, "proxy_object",  c_ob, "objects", text="Collision proxy object")

        if context.active_object is not None and context.active_object.active_material is not None:
            box = layout.box()
            box.label(text="Material Properties")
            row = box.row(align=True)
            row.prop(context.active_object.active_material.pbd_prop, "cull_face", text="")
            row.prop(context.active_object.active_material.pbd_prop, "display", text="Display")

        box = layout.box()
        box.label(text="File Exporting")
        row = box.row()
        c_ob = c_ob.pbd_prop

        row = box.row(align=True)
        row.prop(c_ob, "use_draw_order", text="Use draw order index")
        row.prop(c_ob, "use_animation", text="Animation")
        row = box.row(align=True)
        row.prop(c_ob, "use_selection", text="Selected objects")
        row.prop(c_ob, "use_hidden", text="Include hidden")
        row = box.row(align=True)
        row.prop(c_ob, "model_use_mesh_modifiers", text="Apply modifiers")
        row.prop(c_ob, "scale", text="Scale")
        row = box.row(align=True)
        row.prop(c_ob, "ignore_normals", text="Ignore normals")
        row.prop(c_ob, "ignore_uv_map", text="Ignore UV maps")

        js_checked = " FIle"
        has_script = bool(len(context.preferences.addons["bracket_io_scene_pbd"].preferences.script_path))
        if has_script:
            col = box.column()
            col.separator()
            box.label(text="Javascript exporting")
            row = box.row()
            row.scale_y = 1.1
            row.prop(c_ob, "json_export_type", expand=True, emboss=True)

            if c_ob.json_export_type != "none":

                if not bool(len( c_ob.json_output_path.strip() )):
                    js_checked = " (output path required)"
                else:
                    js_checked = " and Javascript File"

                row = box.row()
                row.scale_y = 1.1
                row.prop(c_ob, "name", text="Export name")

                row = box.row()
                row.prop(c_ob, "json_ignore_normals", text="Ignore normals")
                row.prop(c_ob, "json_ignore_uv_map", text="Ignore UV maps")

                row = box.row()
                row.prop(c_ob, "json_force_texture", text="Overwrite textures")
                row.prop(c_ob, "json_ignore_meta", text="Ignore meta data")

                row = box.row()
                row.prop(c_ob, "json_precision", text="Data precision")
                row.prop(c_ob, "json_compressed", text="Compression level")

                col = box.column()
                col.separator()
                col.prop(c_ob, "json_additional_option", text="Additional options")
                col = box.column()
                col.scale_y = 1.1
                col.prop(c_ob, "json_asset_root", text="Assest server root")
                col.prop(c_ob, "json_texture_subdir", text="Textures sub-directory")

                col = box.column()
                col.scale_y = 1.2
                col.prop(c_ob, "json_output_path", text='Output directory')
                col.separator()
        else:
            col = box.column()
            col.separator()
            col.label(text="..add Batten Mesh convert.js to enable js exporting-")
            col.separator()

        col = box.column()
        col.active = c_ob.json_export_type == "none" or bool(len( c_ob.json_output_path.strip() ))
        col.separator()
        col.operator("export.pbd_file", text="Export an Obj"+js_checked, icon="EXPORT")
        col.scale_y = 1.5
        col.separator()

        if has_script:
            row = box.row()
            row.scale_y = 1.2
            row.operator("export.json_from_obj", text="Export Js from Obj", icon="EXPORT")
            row.prop(c_ob, "json_import_path", text=".obj:")

def register():

    bpy.utils.register_class(MainSettings)
    bpy.utils.register_class(TerrainTools)
    bpy.utils.register_class(FontCreation)
    bpy.utils.register_class(ModelExport)
    bpy.utils.register_class(ModelImport)

def unregister():

    bpy.utils.unregister_class(ModelImport)
    bpy.utils.unregister_class(ModelExport)
    bpy.utils.unregister_class(FontCreation)
    bpy.utils.unregister_class(TerrainTools)
    bpy.utils.unregister_class(MainSettings)
