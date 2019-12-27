import bpy, os
from bpy.props import ( EnumProperty, BoolProperty, FloatProperty, StringProperty, EnumProperty, IntProperty )

class ExportPropMaterial(bpy.types.PropertyGroup):

    mouse_region = BoolProperty(
        default=True,
        description="Only applies to widget exports. Set a material as a hitbox area for widget mouse detection. This will not override object properties"
        )

    display = BoolProperty(
        default=True,
        description="Draw the material when rendering in the pbd engine. this can still be used as a mouse detection region however"
        )

    cull_face = EnumProperty(items= (('back', 'Cull Back Faces', 'Cull all back facing polygons'),
                                     ('front', 'Cull Front Faces', 'Cull all fron facing polygons'),
                                     ('back_font', 'Cull All Faces', 'Cull both front and back polygons'),
                                     ('none', 'Do not cull', 'Disable polygon culling'),
                                 ),
                                 name="Polygon culling",
                                 default = "back"
                             )

class ExportPropObject(bpy.types.PropertyGroup):

    draw_index = IntProperty(
        name="Draw order index",
        default=1,
        description="The draw index specifies what order the object will appear in the OBJ and JSON exports. This affects the order of drawing in the PBD engine as well"
        )

    mouse_region = BoolProperty(
        default=False,
        description="Only applies to widget exports. Set the current object as a mouse detection area for widgets."
        )

    detect_bounding = BoolProperty(
        default=False,
        description="This will use only the bounding rectangle of the object created from its meta data for mouse detection which is alot faster than checking all of the polygons"
        )

    clip_region = BoolProperty(
        default=False,
        description="Only applies to widget exports. Set the current object as a clipping region area for widgets."
        )

    clip_bounding = BoolProperty(
        default=False,
        description="This will use only the bounding rectangle of the object created from its meta data for clipping which is a little faster than checking all of the polygons"
        )

    cull_face = EnumProperty(items= (('back', 'Cull Back Faces', 'Cull all back facing polygons'),
                                     ('front', 'Cull Front Faces', 'Cull all fron facing polygons'),
                                     ('back_font', 'Cull All Faces', 'Cull both front and back polygons'),
                                     ('none', 'Do not cull', 'Disable polygon culling'),
                                 ),
                                 name="Polygon culling",
                                 default = "none"
                             )

    display = BoolProperty(
        default=True,
        name="Display",
        description="Draw the material when rendering in the PBD engine. This can still be used as a mouse detection region however"
        )

def make_path_absolute(key):
    """ Prevent Blender's relative paths of doom """
    props = bpy.context.scene.pbd_prop
    sane_path = lambda p: os.path.abspath(bpy.path.abspath(p))

    if key in props and props[key].startswith('//'):
        props[key] = sane_path(props[key])

class ExportPropScene(bpy.types.PropertyGroup):

    character_array = bpy.props.StringProperty (
        default = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890-=!@#$%^&*()_+`~[]\\{}|;':\",./<>?",
        description = "The character array to be used when generating a font text curve"
    )

    label_prefix = bpy.props.StringProperty (
      default = "f_",
      description = "The prefix of the created text object labels.",
    )

    delete_after = BoolProperty(
        name="Delete After Creation",
        description="Delete the selected text/font curve after it is converted to the mesh objects.",
        default=False,
    )

    use_selection = BoolProperty(
            name="Selection only",
            description="Export selected objects only. Otherwise, the entire scene will be exported",
            default=False,
            )

    use_draw_order = BoolProperty(
            name="Obey draw order",
            description="Use the draw order numbers to determine which object appear first in object file",
            default=True
            )

    use_animation = BoolProperty(
            name="Animation",
            description="Write out an OBJ for each frame",
            default=False,
            )

    display_conversion = BoolProperty(
            description="Show the json file exporting options",
            default=False,
            )

    convert_to_json = BoolProperty(
            name="Output json file",
            description="Write out a JSON file which conforms to the PBD standards when exporting",
            default=False,
            )

    json_export_type = EnumProperty(items= (('model', 'Model', 'A standard 3d model'),
                                                 ('widget', 'Widget', 'An orthographic model'),
                                                 ('font', 'Font', 'A font for use with PBD'),
                                                 ),
                                                 default = "model"
                                             )
    json_precision = IntProperty(
        name="JSON data precision",
        default=5,
        min=1,
        max=16,
        description="This will round anything greator than the specified amount as significant digits to reduce the exported JSON file size when possible"
        )

    json_as_widget = BoolProperty(
            name="Output as widget",
            description="Export the data using a zero value for the depth to conform to pbd standard",
            default=False,
            )

    json_ignore_normals = BoolProperty(
            name="Skip lighting normals",
            description="Do not include lighting normals in the exported JSON file",
            default=True,
            )

    json_include_meta = BoolProperty(
            name="Create meta",
            description="Create model meta data in the json file",
            default=True,
            )

    json_force_texture = BoolProperty(
            name="Overwrite textures",
            description="Overwrite all textures copied to the destination with the JSON file. Otherwise, textures are only copied if one with the same name is not in the destination already",
            default=True,
            )

    json_additional_option = StringProperty(
            name="Additional parameters",
            description="Any additional parameters to pass into the JSON exporting script",
            default="",
            maxlen=256
            )

    json_output_path = StringProperty(
            name="Destination",
            description="(Required) Choose a directory to create the json file. This should be within the project html structure",
            default="",
            maxlen=1024,
            update = lambda s,c: make_path_absolute('json_output_path'),
            subtype='DIR_PATH'
            )
    json_asset_root = StringProperty(
            name="Server root",
            description="(Optional) Choose the directory which serves as the base url for the network server. This is prepended to any asset urls created in the json file",
            default="",
            maxlen=1024,
            update = lambda s,c: make_path_absolute('json_asset_root'),
            subtype='DIR_PATH'
            )

    json_texture_subdir = StringProperty(
            name="Texture sub-directory",
            description="(Optional) Must be a relative path string. A relative path to the JSON destination path which will store all of the textures used within the JSON export. Note: Textures are copied from the input specified in the OBJ data to the destination (not moved)",
            default="Textures",
            maxlen=1024,
            subtype='DIR_PATH'
            )

    json_import_path = StringProperty(
            name="Input OBJ file",
            description="(Optional) A JSON file may be exported using an input OBJ file instead of the OBJ file exported from the scene",
            default="",
            maxlen=1024,
            update = lambda s,c: make_path_absolute('json_import_path'),
            subtype='FILE_PATH'
            )

def register():

    bpy.utils.register_class(ExportPropObject)
    bpy.utils.register_class(ExportPropScene)
    bpy.utils.register_class(ExportPropMaterial)
    bpy.types.Object.pbd_prop = bpy.props.PointerProperty(type=ExportPropObject)
    bpy.types.Scene.pbd_prop = bpy.props.PointerProperty(type=ExportPropScene)
    bpy.types.Material.pbd_prop = bpy.props.PointerProperty(type=ExportPropMaterial)

def unregister():

    bpy.utils.unregister_class(ExportPropMaterial)
    bpy.utils.unregister_class(ExportPropObject)
    bpy.utils.unregister_class(ExportPropScene)
    del bpy.types.Material.pbd_prop
    del bpy.types.Object.pbd_prop
    del bpy.types.Scene.pbd_prop
