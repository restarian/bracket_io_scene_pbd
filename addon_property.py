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

    terrain_name = StringProperty(
        default = "",
        description = "The name of the terrain set to the header type",
        )

    terrain_segment_count = EnumProperty(
        description="The amount of world segments which will be created when the terrain is imported into the engine.",
        items=lambda s,c: get_terrain_sqrt("terrain_segment_count", s, c),
        )

    draw_index = IntProperty(
        name="Draw order index",
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
        name="Include normals",
        description="Include lighting normals this object",
        default=True,
        )

    cull_face = EnumProperty(items= (('back', 'Cull Back Faces', 'Cull all back facing polygons'),
                                     ('front', 'Cull Front Faces', 'Cull all fron facing polygons'),
                                     ('back_font', 'Cull All Faces', 'Cull both front and back polygons'),
                                     ('none', 'Do not Cull', 'Disable polygon culling'),
                                     ('unused', 'Ignore Culling', 'Ignore culling and use whatever is set'),
                                 ),
                                 default = "back"
                             )

    display = BoolProperty(
        default=True,
        name="Display",
        description="Draw the material when rendering in the PBD engine. This can still be used as a mouse detection region however"
        )


def make_path_absolute(key, self, context):
    """ Prevent Blender's relative paths of doom """

    if context.scene.pbd_prop.export_object_with == 'collection':
        props = context.collection.pbd_prop
    else:
        props = context.scene.pbd_prop

    sane_path = lambda p: os.path.abspath(bpy.path.abspath(p))

    if key in props and props[key].startswith('//'):
        props[key] = sane_path(props[key])

def get_terrain_sqrt(key, self, context):
    """ Get the square roots of the terrain """

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

    export_object_with = EnumProperty(items= (
            ('scene', 'Current Scene', 'Use the entrire scene for exporting objects.'),
            ('collection', 'Current Collection', 'Use only the current collection for exporting objects.'),
        ),
        default = "collection"
        )

    scale = IntProperty(
        min = 1, max = 100000,
        default = 230,
        name = "Scale",
        description = "The exporting scale of the object.",
        )

    terrain_use_normals = BoolProperty(
        description="Export one normal per vertex and per face, to represent flat faces and sharp edges",
        default=False,
        )

    terrain_use_mesh_modifiers = BoolProperty(
        description="Apply any modifiers to the terrain before exporting it",
        default=True,
        )

    model_use_mesh_modifiers = BoolProperty(
        name="Apply modifiers",
        description="Apply any modifiers to the model before exporting it",
        default=True,
        )

    terrain_use_active_object = BoolProperty(
        name = "Use Active Object",
        description = "Use the active object for the terrain exporting",
        )

    terrain_object = StringProperty(
        name = "Terrain object",
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
        name="Delete After Creation",
        description="Delete the selected text/font curve after it is converted to the mesh objects.",
        default=False,
    )

    use_selection = BoolProperty(
        description="Export selected objects only. Otherwise, the entire scene or collections will be exported",
        default=False,
        )

    use_hidden = BoolProperty(
        description="Export objects which are hidden as well. Otherwise, no hidden objects will be exported (even if they are selected)",
        default=False,
        )

    use_draw_order = BoolProperty(
        description="Use the draw order numbers to determine which object appear first in object file",
        default=True
        )

    use_animation = BoolProperty(
        description="Write out an OBJ for each frame",
        default=False,
        )

    json_export_type = EnumProperty(items= (
            ('none', 'None', 'Do not export a PBD javascript file'),
            ('model', 'Model', 'A standard 3d model for PBD'),
            ('widget', 'Widget', 'An orthographic data model for PBD'),
            ('font', 'Font', 'A font data model for use with PBD'),
        ),
        default = "model"
        )

    model_name = StringProperty(
        default = "blender_export",
        description = "The name of the model as a type",
        )

    json_precision = IntProperty(
        default=5,
        min=1,
        max=16,
        description="This will round anything greator than the specified amount as significant digits to reduce the exported js file size when possible"
        )

    json_compressed = IntProperty(
        default=2,
        min=1,
        max=5,
        description="Higher values will result in less white space and lesser size"
        )

    json_as_widget = BoolProperty(
        description="Export the data using a zero value for the depth to conform to pbd standard",
        default=False,
        )

    ignore_normals = BoolProperty(
        description="Do not include lighting normals in the exported obj file for any objects",
        default=False,
        )

    ignore_uv_map = BoolProperty(
        description="Do not include UV mapping coordinates in the exported obj file for any objects",
        default=False,
        )

    json_ignore_normals = BoolProperty(
        description="Do not include lighting normals in the exported js file for any objects",
        default=False,
        )

    json_ignore_uv_map = BoolProperty(
        description="Do not include UV mapping coordinates in the exported js file for any objects",
        default=False,
        )

    json_ignore_meta = BoolProperty(
        description="Do not create the model meta data in the json file",
        default=True,
        )

    json_force_texture = BoolProperty(
        description="Overwrite all textures copied to the destination with the js file. Otherwise, textures are only copied if one with the same name is not in the destination already",
        default=True,
        )

    json_additional_option = StringProperty(
        description="(Optional) Any additional parameters to pass into the js exporting script",
        default="",
        maxlen=256
        )

    json_output_path = StringProperty(
        description="(Required) Choose a directory to create the json file. This should be within the project html structure",
        default="",
        maxlen=1024,
        update = lambda s,c: make_path_absolute('json_output_path', s, c),
        subtype='DIR_PATH'
        )
    json_asset_root = StringProperty(
        description="(Optional) Choose the directory which serves as the base url for the network server. This is prepended to any asset urls created in the json file",
        default="",
        maxlen=1024,
        update = lambda s,c: make_path_absolute('json_asset_root', s, c),
        subtype='DIR_PATH'
        )

    json_texture_subdir = StringProperty(
        description="(Optional) Must be a relative path string. A relative path to the js destination path which will store all of the textures used within the js export. Note: Textures are copied from the input specified in the OBJ data to the destination (not moved)",
        default="Textures",
        maxlen=1024,
        subtype='DIR_PATH'
        )

    json_import_path = StringProperty(
        description="(Optional) A js file may be exported using an input OBJ file instead of the OBJ file exported from the scene",
        default="",
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
