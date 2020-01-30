import bpy, os
from math import sqrt
from bpy.props import ( BoolProperty, FloatProperty, StringProperty, EnumProperty, IntProperty )

class ExportPropMaterial(bpy.types.PropertyGroup):

    mouse_region = BoolProperty(
        default=True,
        description="Only usefull to widget model types. Set a material as a hitbox area for widget mouse detection. This will not override object properties"
        )

    display = BoolProperty(
        default=True,
        description="Draw the material when rendering in the pbd engine. this can still be used as a mouse detection region however"
        )

    cull_face = EnumProperty(items= (('back', 'Cull Back Faces', 'Cull all back facing polygons'),
                                     ('front', 'Cull Front Faces', 'Cull all fron facing polygons'),
                                     ('back_font', 'Cull All Faces', 'Cull both front and back polygons'),
                                     ('none', 'Do not Cull', 'Disable polygon culling'),
                                     ('unused', 'Ignore Culling', 'Ignore culling and use whatever is set'),
                                 ),
                                 default = "unused"
                             )

class ExportPropObject(bpy.types.PropertyGroup):

    name = StringProperty(
        default = "blender_exported_terrain",
        description = "The name of the terrain set to the header type",
    )

    terrain_segment_count = EnumProperty(
        description="The amount of world segments which will be created when the terrain is imported into the engine.",
        items=lambda s,c: get_terrain_factors("terrain_segment_count", s, c),
    )

    draw_index = IntProperty(
        default=1,
        description="The draw index specifies what order the object will appear in the OBJ and js exports. This affects the order of drawing in the PBD engine as well"
    )

    mouse_region = BoolProperty(
        default=False,
        description="Only usefull to widget model types. Set the current object as a mouse detection area for widgets."
    )

    mouse_bounding = BoolProperty(
        default=False,
        description="This will use only the bounding rectangle of the object created from its meta data for mouse detection which is alot faster than checking all of the polygons"
    )

    clip_region = BoolProperty(
        default=False,
        description="Only usefull to widget model types. Set the current object as a clipping region area for widgets."
    )

    clip_bounding = BoolProperty(
        default=False,
        description="This will use only the bounding rectangle of the object created from its meta data for clipping which is a little faster than checking all of the polygons"
    )

    collision_detection = BoolProperty(
        default=False,
        description="Use the object as a collision detection object in the PBD engine. This still needs to the checked when using a proxy object as a collsion object"
    )

    collision_bounding  = BoolProperty(
        default=False,
        description="Use only the bounding box of the object for collision detection."
    )

    proxy_object = StringProperty(
        default="",
        description="Use this object for the collision detection instead of the actuall mesh data. It should have the collision detection box unchecked so that it is not collision detected checked twice."
    )

    include_normals = BoolProperty(
        default=True,
        description="Include lighting normals this object",
    )

    cull_face = EnumProperty(items= (('back', 'Cull Back Faces', 'Cull all back facing polygons'),
                                     ('front', 'Cull Front Faces', 'Cull all fron facing polygons'),
                                     ('back_font', 'Cull All Faces', 'Cull both front and back polygons'),
                                     ('none', 'Do not Cull', 'Disable polygon culling'),
                                     ('unused', 'Ignore Culling', 'Ignore culling and use whatever is set'),
                                 ),
                                 default = "none"
                             )

    display = BoolProperty(
        default=True,
        description="Draw the material when rendering in the PBD engine. This can still be used as a mouse detection region however"
    )

def make_path_absolute(key, self, context):
    """ Prevent Blender's relative paths of doom """

    c_ob = context.collection.pbd_prop if context.scene.pbd_prop.export_object_with == 'collection' else context.scene.pbd_prop
    sane_path = lambda p: os.path.abspath(bpy.path.abspath(p))
    if key in c_ob and c_ob[key].startswith('//'):
        c_ob[key] = sane_path(c_ob[key])

def get_terrain_factors(key, self, context):
    """ Get all the unique factors of the terrain """

    item = []
    deps = context.evaluated_depsgraph_get()
    t = None
    if context.scene.pbd_prop.terrain_use_active_object:
        t = context.active_object
    elif len(context.scene.pbd_prop.terrain_object.strip()):
        t = context.scene.objects[context.scene.pbd_prop.terrain_object.strip()]

    if t is not None and t.type == "MESH":
        ob = t.evaluated_get(deps)
        c = round(sqrt(len(ob.data.vertices)))-1
        for i in range(1, c + 1):
            if c % i == 0:
                item.append((str(c/i), "( "+str(i) +" X "+str(i) + " )  " + str(round(c/i))+" total segments", "Rows and colums") )
        item.append(("1", "( 1 X 1 )  "+str(c)+" total segments", "Rows and colums" ))

    return item

class ExportProp(bpy.types.PropertyGroup):

    export_object_with = EnumProperty(
        items= (
            ('scene', 'Current Scene', 'Use the entrire scene for exporting objects.'),
            ('collection', 'Current Collection', 'Use only the current collection for exporting objects.'),
        ),
        default = "collection"
    )

    scale = IntProperty(
        default = 100,
        min = 1, max = 100000,
        description = "The exporting scale of the object.",
    )

    terrain_add_multires = BoolProperty(
        default=True,
        description="Also add a multi resolution modifier to the terrain plane after creation.",
    )

    terrain_use_mesh_modifiers = BoolProperty(
        default=True,
        description="Apply any modifiers to the terrain before exporting it",
    )

    model_use_mesh_modifiers = BoolProperty(
        default=True,
        description="Apply any modifiers to the model before exporting it",
    )

    terrain_use_active_object = BoolProperty(
        default=True,
        description = "Use the active object for the terrain exporting",
    )

    terrain_object = StringProperty(
        description = "Object to use as the terrain export data",
    )

    character_array = StringProperty (
        default = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890-=!@#$%^&*()_+`~[]\\{}|;':\",./<>?",
        description = "The character array to be used when generating a font text curve"
    )

    label_prefix = StringProperty (
      default = "f_",
      description = "The prefix of the created text object labels.",
    )

    delete_after = BoolProperty(
        default=False,
        description="Delete the selected text/font curve after it is converted to the mesh objects.",
    )

    hide_after = BoolProperty(
        default=True,
        description="Hide the selected text/font curve after it is converted to the mesh objects.",
    )

    use_selection = BoolProperty(
        default=False,
        description="Export selected objects only. Otherwise, the entire scene or collections will be exported",
    )

    use_hidden = BoolProperty(
        default=False,
        description="Export objects which are hidden as well. Otherwise, no hidden objects will be exported (even if they are selected)",
    )

    use_draw_order = BoolProperty(
        default=True,
        description="Use the draw order numbers to determine which object appear first in object file",
    )

    use_animation = BoolProperty(
        default=False,
        description="Write out an OBJ for each frame",
    )

    json_export_type = EnumProperty(
        items= (
            ('none', 'None', 'Do not export a PBD javascript file'),
            ('model', 'Model', 'A standard 3d model for PBD'),
            ('widget', 'Widget', 'An orthographic data model for PBD'),
            ('font', 'Font', 'A font data model for use with PBD'),
        ),
        default = "model"
    )

    name = StringProperty(
        default = "blender_export",
        description = "The name of the model as a type",
    )

    json_precision = IntProperty(
        default=5,
        min=1, max=16,
        description="This will round anything greator than the specified amount as significant digits to reduce the exported js file size when possible"
    )

    json_compressed = IntProperty(
        default=5,
        min=1, max=5,
        description="Higher values will result in less white space and lesser size"
    )

    ignore_normals = BoolProperty(
        default=False,
        description="Do not include lighting normals in the exported obj file for any objects",
    )

    ignore_uv_map = BoolProperty(
        default=False,
        description="Do not include UV mapping coordinates in the exported obj file for any objects",
    )

    json_ignore_normals = BoolProperty(
        default=False,
        description="Do not include lighting normals in the exported js file for any objects",
    )

    json_ignore_uv_map = BoolProperty(
        default=False,
        description="Do not include UV mapping coordinates in the exported js file for any objects",
    )

    json_ignore_meta = BoolProperty(
        default=True,
        description="Do not create the model meta data in the json file",
    )

    export_data_format = EnumProperty(
        items= (
            ('json', 'JSON file', 'A parsable JSON data object with a .json extention.'),
            ('amd', 'AMD wrapped JS file', 'Wrapped with the asynchronouse module definition syntax with a .js extention.'),
        ),
        default = "amd",
        description="The format of the outputed data file.",
    )

    json_force_texture = BoolProperty(
        default=True,
        description="Overwrite all textures copied to the destination with the js file. Otherwise, textures are only copied if one with the same name is not in the destination already",
    )

    json_additional_option = StringProperty(
        default="",
        maxlen=256,
        description="(Optional) Any additional parameters to pass into the js exporting script",
    )

    json_output_path = StringProperty(
        default="",
        description="(Required) Choose a directory to create the json file. This should be within the project html structure",
        maxlen=1024,
        update = lambda s,c: make_path_absolute('json_output_path', s, c),
        subtype='DIR_PATH'
    )
    json_asset_root = StringProperty(
        default="",
        description="(Optional) Choose the directory which serves as the base url for the network server. This is prepended to any asset urls created in the json file",
        maxlen=1024,
        update = lambda s,c: make_path_absolute('json_asset_root', s, c),
        subtype='DIR_PATH'
    )

    json_texture_subdir = StringProperty(
        default="Textures",
        description="(Optional) Must be a relative path string. A relative path to the js destination path which will store all of the textures used within the js export. Note: Textures are copied from the input specified in the OBJ data to the destination (not moved)",
        maxlen=1024,
        subtype='DIR_PATH'
    )

    json_import_path = StringProperty(
        default="",
        description="(Optional) A js file may be exported using an input OBJ file instead of the OBJ file exported from the scene",
        maxlen=1024,
        update = lambda s,c: make_path_absolute('json_import_path', s, c),
        subtype='FILE_PATH'
    )

def register():

    bpy.utils.register_class(ExportPropObject)
    bpy.utils.register_class(ExportProp)
    bpy.utils.register_class(ExportPropMaterial)
    bpy.types.Object.pbd_prop = bpy.props.PointerProperty(type=ExportPropObject)
    bpy.types.Collection.pbd_prop = bpy.props.PointerProperty(type=ExportProp)
    bpy.types.Scene.pbd_prop = bpy.props.PointerProperty(type=ExportProp)
    bpy.types.Material.pbd_prop = bpy.props.PointerProperty(type=ExportPropMaterial)

def unregister():

    bpy.utils.unregister_class(ExportPropMaterial)
    bpy.utils.unregister_class(ExportPropObject)
    bpy.utils.unregister_class(ExportProp)
    del bpy.types.Material.pbd_prop
    del bpy.types.Object.pbd_prop
    del bpy.types.Scene.pbd_prop
    del bpy.types.Collection.pbd_prop
