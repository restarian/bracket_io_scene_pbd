import bpy, os
from math import sqrt
from bpy.props import ( EnumProperty, BoolProperty, FloatProperty, StringProperty, EnumProperty, IntProperty )

def ShowMessageBox(message = "", title = "Terrain Verification", icon = 'INFO'):
    message = str(message).replace("\\t", "   ").replace("\t", "   ").replace("\\n", "\n")
    def draw(self, context):
        for m in message.splitlines():
            self.layout.label(text=m)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

class CreateTerrain(bpy.types.Operator):
    """Create a simple terrain starting plane with the correct orientation"""

    bl_idname = "terrain.create_starting"
    bl_label = 'Create Starting Terrain'
    bl_options = {'PRESET'}

    def execute(self, context):

        return {"FINISHED"}

def r(num):
    return round(num*10)/10


class VerifyTerrain(bpy.types.Operator):
    """Create a simple terrain starting plane with the correct orientation"""

    bl_idname = "terrain.verify"
    bl_label = 'Error Check Terrain'
    bl_options = {'PRESET'}

    def execute(self, context):

        if context.scene.pbd_prop.terrain_use_active_object:
            terrain_obj = context.active_object
        else:
            terrain_obj = context.scene.objects[context.scene.pbd_prop.terrain_object.strip()]

        depsgraph = context.evaluated_depsgraph_get()
        ob_for_convert = terrain_obj.evaluated_get(depsgraph) if context.scene.pbd_prop.terrain_use_mesh_modifiers else terrain_obj.original

        try:
            me = ob_for_convert.to_mesh()
        except RuntimeError:
            ShowMessageBox("An improper terrain object is in use", "Terrain has errors", "ERROR")
            return {"FINISHED"}

        ob_matrix = ob_for_convert.matrix_world

        from mathutils import Matrix
        from bpy_extras.io_utils import axis_conversion
        global_matrix = (Matrix.Scale(context.scene.pbd_prop.world_scale, 4) @ axis_conversion(to_forward="Y", to_up="-Z", ).to_4x4())
        me.transform(global_matrix @ ob_matrix)

        # If negative scaling, we have to invert the normals...
        if ob_matrix.determinant() < 0.0:
            me.flip_normals()

        sfunc = lambda v: ( r(v.co[2]), r(v.co[0]) )
        verts = [v for q,v in enumerate(me.vertices)]
        verts.sort(key=sfunc)
        smallest_x = r(verts[0].co[0])
        largest_x = r(verts[-1].co[0])
        smallest_z = r(verts[0].co[2])
        largest_z = r(verts[-1].co[2])
        expected_quad_size = r(r(verts[1].co[0]) - r(verts[0].co[0]))
        last = smallest_x
        bad_vert = []

        # Check for grid conformity and highlight all bad verticies
        for v in verts:
            if r(v.co[0]) == smallest_x:
                last = smallest_x
            elif r(v.co[0]) - last != expected_quad_size:
                bad_vert.append((v.co))
            else:
                last = r(v.co[0])

        for v in verts:
            if r(v.co[0]) == largest_x:
                last = r(v.co[2])
            if r(v.co[2]) == smallest_z:
                continue
            print(v.co[2], last)
            if r(v.co[2]) - last != expected_quad_size:
                bad_vert.append((v.co))

        # TODO highlight all of the bad vertices.
        if len(bad_vert):
            ShowMessageBox("Terrain verticies are not in a square grid along the X and Z axis. The bad verties have been highlighted.", "Terrain has errors", "ERROR")
            return {"FINISHED"}

        resolution = sqrt( len(verts) ) - 1
        if round(resolution) != sqrt( len(verts) ) - 1:
            ShowMessageBox("Terrain has an odd number of verticies.", "Terrain has errors", "ERROR")
            return {"FINISHED"}

        ShowMessageBox("Terrain object look good :)")
        return {"FINISHED"}

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
                                 name="Polygon culling",
                                 default = "unused"
                             )

class ExportPropObject(bpy.types.PropertyGroup):

    terrain_name = StringProperty(
        default = "",
        description = "The name of the terrain set to the header type",
        )

    terrain_segment_count = EnumProperty(
        name="Rows and columns",
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
        default=True,
        description="Use the object as a collision detection object in the PBD engine. This still needs to the checked when using a proxy object as a collsion object"
        )
    collision_bounding  = BoolProperty(
        default=True,
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
                                 name="Polygon culling",
                                 default = "back"
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

class ExportPropScene(bpy.types.PropertyGroup):

    world_scale = IntProperty(
        min = 1, max = 100000,
        default = 10000,
        name = "World scale",
        description = "This only affects how large the numbers used in the calculations are",
        )

    corralate_terrain_name = StringProperty(
        name = "Corralate to terrain",
        description = "Export the model geometry according to its position the set terrain object",
        )

    corralate_model_terrain = BoolProperty (
        name = "Corralate to world",
        description = "Export the model geometry according to its position of the set world corralate object.",
        default=True
        )

    terrain_use_normals = BoolProperty(
        name="Write Normals",
        description="Export one normal per vertex and per face, to represent flat faces and sharp edges",
        default=False,
        )

    terrain_use_mesh_modifiers = BoolProperty(
        name="Apply modifiers",
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

    convert_to_json = BoolProperty(
            name="Output javscrtipt file",
            description="Write out a javascript file which conforms to the PBD standards when exporting",
            default=False,
            )

    json_export_type = EnumProperty(items= (('model', 'Model', 'A standard 3d model for PBD'),
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
        name="JS data precision",
        default=5,
        min=1,
        max=16,
        description="This will round anything greator than the specified amount as significant digits to reduce the exported js file size when possible"
        )

    json_compressed = IntProperty(
        name="Compression level",
        default=2,
        min=1,
        max=5,
        description="Higher values will result in less white space and lesser size"
        )

    json_as_widget = BoolProperty(
            name="Output as widget",
            description="Export the data using a zero value for the depth to conform to pbd standard",
            default=False,
            )

    json_ignore_normals = BoolProperty(
            name="Skip lighting normals",
            description="Do not include lighting normals in the exported js file for any objects",
            default=False,
            )

    json_ignore_uv_map = BoolProperty(
            name="Skip UV mapping",
            description="Do not include UV mapping coordinates in the exported js file for any objects",
            default=False,
            )

    json_include_meta = BoolProperty(
            name="Create meta",
            description="Create model meta data in the json file",
            default=True,
            )

    json_force_texture = BoolProperty(
            name="Overwrite textures",
            description="Overwrite all textures copied to the destination with the js file. Otherwise, textures are only copied if one with the same name is not in the destination already",
            default=True,
            )

    json_additional_option = StringProperty(
            name="Additional parameters",
            description="Any additional parameters to pass into the js exporting script",
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
            description="(Optional) Must be a relative path string. A relative path to the js destination path which will store all of the textures used within the js export. Note: Textures are copied from the input specified in the OBJ data to the destination (not moved)",
            default="Textures",
            maxlen=1024,
            subtype='DIR_PATH'
            )

    json_import_path = StringProperty(
            name="Input OBJ file",
            description="(Optional) A js file may be exported using an input OBJ file instead of the OBJ file exported from the scene",
            default="",
            maxlen=1024,
            update = lambda s,c: make_path_absolute('json_import_path'),
            subtype='FILE_PATH'
            )


def register():

    bpy.utils.register_class(CreateTerrain)
    bpy.utils.register_class(VerifyTerrain)
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
    bpy.utils.register_class(VerifyTerrain)
    bpy.utils.unregister_class(CreateTerrain)
    del bpy.types.Material.pbd_prop
    del bpy.types.Object.pbd_prop
    del bpy.types.Scene.pbd_prop
