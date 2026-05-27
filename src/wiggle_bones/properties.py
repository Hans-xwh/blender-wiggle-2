#type: ignore

from .wiggle_core import *  #sorry not sorry

import bpy
from bpy.types import PropertyGroup, Object, Collection
from bpy.props import StringProperty, BoolProperty, FloatProperty, CollectionProperty, PointerProperty, FloatVectorProperty, IntProperty, EnumProperty


#### Internal Props ####
class WiggleBoneItem(PropertyGroup):
    name: StringProperty(override={'LIBRARY_OVERRIDABLE'})    #type: ignore

class WiggleItem(PropertyGroup):
    name: StringProperty(override={'LIBRARY_OVERRIDABLE'})  
    list: CollectionProperty(type=WiggleBoneItem, override={'LIBRARY_OVERRIDABLE','USE_INSERTION'})    

#store properties for a bone. custom properties for user editable. property group for internal calculations
class WiggleBone(PropertyGroup):
    matrix: FloatVectorProperty(name = 'Matrix', size=16, subtype = 'MATRIX', override={'LIBRARY_OVERRIDABLE'})
    position: FloatVectorProperty(subtype='TRANSLATION', override={'LIBRARY_OVERRIDABLE'})
    position_last: FloatVectorProperty(subtype='TRANSLATION', override={'LIBRARY_OVERRIDABLE'})
    velocity: FloatVectorProperty(subtype='VELOCITY', override={'LIBRARY_OVERRIDABLE'})
    
    collision_point:FloatVectorProperty(subtype = 'TRANSLATION', override={'LIBRARY_OVERRIDABLE'})
    collision_ob: PointerProperty(type=Object, override={'LIBRARY_OVERRIDABLE'})
    collision_normal: FloatVectorProperty(subtype = 'TRANSLATION', override={'LIBRARY_OVERRIDABLE'})
    collision_col: PointerProperty(type=Collection,override={'LIBRARY_OVERRIDABLE'})
    
    position_head: FloatVectorProperty(subtype='TRANSLATION', override={'LIBRARY_OVERRIDABLE'})
    position_last_head: FloatVectorProperty(subtype='TRANSLATION', override={'LIBRARY_OVERRIDABLE'})
    velocity_head: FloatVectorProperty(subtype='VELOCITY', override={'LIBRARY_OVERRIDABLE'})
    
    collision_point_head:FloatVectorProperty(subtype = 'TRANSLATION', override={'LIBRARY_OVERRIDABLE'})
    collision_ob_head: PointerProperty(type=Object, override={'LIBRARY_OVERRIDABLE'})
    collision_normal_head: FloatVectorProperty(subtype = 'TRANSLATION', override={'LIBRARY_OVERRIDABLE'})
    
    position_tail: FloatVectorProperty(subtype='TRANSLATION', override={'LIBRARY_OVERRIDABLE'})
    position_last_tail: FloatVectorProperty(subtype='TRANSLATION', override={'LIBRARY_OVERRIDABLE'})    #Idk where this one is used
    velocity_tail: FloatVectorProperty(subtype='VELOCITY', override={'LIBRARY_OVERRIDABLE'})
    
    collision_point_tail:FloatVectorProperty(subtype = 'TRANSLATION', override={'LIBRARY_OVERRIDABLE'})
    collision_ob_tail: PointerProperty(type=Object, override={'LIBRARY_OVERRIDABLE'})
    collision_normal_tail: FloatVectorProperty(subtype = 'TRANSLATION', override={'LIBRARY_OVERRIDABLE'})  

class WiggleObject(PropertyGroup):
    list: CollectionProperty(type=WiggleItem, override={'LIBRARY_OVERRIDABLE'})

    #User
    wiggle_enable : BoolProperty(
        name = 'Enable Armature',
        description = 'Enable wiggle on this armature',
        default = False,
        options={'HIDDEN'},
        override={'LIBRARY_OVERRIDABLE'}
    )

    wiggle_mute : BoolProperty(
        name = 'Mute Armature',
        description = 'Mute wiggle on this armature.',
        default = False,
        override={'LIBRARY_OVERRIDABLE'},
        update=lambda s, c: update_prop(s, c, 'wiggle_mute')
    )

    wiggle_freeze : BoolProperty(
        name = 'Freeze Wiggle',
        description = 'Wiggle Calculation frozen after baking',
        default = False,
        override={'LIBRARY_OVERRIDABLE'}
    )

class FullBoneCollisionSettings(PropertyGroup):
    enable_fullbone_collision: BoolProperty(
        name='Enable Full Bone Collision',
        description='Enable collision detection for the entire wiggle bone in this scene',
        default=False
    )
    steps: IntProperty(
        name='Steps',
        description='Number of interpolation steps for collision detection along the bone',
        min=1, default=10, soft_max=64, max=100
    )
    collision_threshold: FloatProperty(
        name='Collision Threshold',
        description='Minimum movement distance to consider a collision',
        min=0.001, default=0.02, precision=4
    )
    dot_threshold: FloatProperty(
        name='Dot Threshold',
        description='Sensitivity threshold for the dot product check during collisions',
        min=0.01, max=1.0, default=0.1, precision=2
    )
   
class WiggleScene(PropertyGroup):
    dt: FloatProperty()
    lastframe: IntProperty()
    iterations: IntProperty(name='Quality', description='Constraint solver interations for chain physics', min=1, default=2, soft_max=10, max=100)
    loop: BoolProperty(name='Loop Physics', description='Physics continues as timeline loops', default=True)
    list: CollectionProperty(type=WiggleItem, override={'LIBRARY_OVERRIDABLE','USE_INSERTION'})
    preroll: IntProperty(name = 'Preroll', description='Frames to run simulation before bake', min=0, default=0)
    is_preroll: BoolProperty(default=False)
    bake_overwrite: BoolProperty(name='Overwrite Current Action', description='Bake wiggle into current action, instead of creating a new one', default = False)
    bake_nla: BoolProperty(name='Current Action to NLA', description='Move existing animation on the armature into an NLA strip', default = False) 
    is_rendering: BoolProperty(default=False)
    reset: BoolProperty(default=False)
    full_bone_collision: PointerProperty(type=FullBoneCollisionSettings)

    #User
    wiggle_enable : BoolProperty(
        name = 'Enable Scene',
        description = 'Enable wiggle on this scene',
        default = False,
        override={'LIBRARY_OVERRIDABLE'},
        update=lambda s, c: update_prop(s, c, 'wiggle_enable')
    )
#########################

#### User Toggles ####
class WiggleBoneSettings(PropertyGroup):
    #Base bone props
    wiggle_enable : BoolProperty(
        name = 'Enable Bone',
        description = "Enable wiggle on this bone",
        default = False,
        options={'HIDDEN'},
        override={'LIBRARY_OVERRIDABLE'}
    )

    wiggle_mute : BoolProperty(
        name = 'Mute Bone',
        description = "Mute wiggle for this bone.",
        default = False,
        override={'LIBRARY_OVERRIDABLE'},
        update=lambda s, c: update_prop(s, c, 'wiggle_mute')
    )

    wiggle_head : BoolProperty(
        name = 'Bone Head',
        description = "Enable wiggle on this bone's head",
        default = False,
        override={'LIBRARY_OVERRIDABLE'},
        options={'HIDDEN'},
        update=lambda s, c: update_prop(s, c, 'wiggle_head')
    )

    wiggle_tail : BoolProperty(
        name = 'Bone Tail',
        description = "Enable wiggle on this bone's tail",
        default = False,
        override={'LIBRARY_OVERRIDABLE'},
        options={'HIDDEN'},
        update=lambda s, c: update_prop(s, c, 'wiggle_tail')
    )

    wiggle_head_mute : BoolProperty(
        name = 'Bone Head Mute',
        description = "Mute wiggle on this bone's head",
        default = False,
        override={'LIBRARY_OVERRIDABLE'},
        update=lambda s, c: update_prop(s, c, 'wiggle_head_mute')
    )

    wiggle_tail_mute : BoolProperty(
        name = 'Bone Tail Mute',
        description = "Mute wiggle on this bone's tail",
        default = False,
        override={'LIBRARY_OVERRIDABLE'},
        update=lambda s, c: update_prop(s, c, 'wiggle_tail_mute')
    )

    ### Tail Properties ###
    wiggle_mass: FloatProperty(
        name = 'Mass',
        description = 'Mass of bone',
        min = 0.01,
        default = 1,
        override={'LIBRARY_OVERRIDABLE'},
        update=lambda s, c: update_prop(s, c, 'wiggle_mass')
    )

    wiggle_stiff : FloatProperty(
        name = 'Stiff',
        description = 'Spring stiffness coefficient, can be large numbers',
        min = 0,
        default = 400,
        override={'LIBRARY_OVERRIDABLE'},
        update=lambda s, c: update_prop(s, c, 'wiggle_stiff')
    )

    wiggle_stretch : FloatProperty(
        name = 'Stretch',
        description = 'Bone stretchiness factor, 0 to 1 range',
        min = 0,
        default = 0,
        max=1,
        override={'LIBRARY_OVERRIDABLE'},
        update=lambda s, c: update_prop(s, c, 'wiggle_stretch')
    )

    wiggle_damp : FloatProperty(
        name = 'Damp',
        description = 'Dampening coefficient, can be greater than 1',
        min = 0,
        default = 1,
        override={'LIBRARY_OVERRIDABLE'},
        update=lambda s, c: update_prop(s, c, 'wiggle_damp')
    )

    wiggle_gravity : FloatProperty(
        name = 'Gravity',
        description = 'Multiplier for scene gravity',
        default = 1,
        override={'LIBRARY_OVERRIDABLE'},
        update=lambda s, c: update_prop(s, c, 'wiggle_gravity')
    )

    wiggle_wind_ob : PointerProperty(
        name='Wind', 
        description='Wind force field object', 
        type=bpy.types.Object, 
        poll = wind_poll, 
        override={'LIBRARY_OVERRIDABLE'}, 
        update=lambda s, c: update_prop(s, c, 'wiggle_wind_ob')
    )

    wiggle_wind : FloatProperty(
        name = 'Wind Multiplier',
        description = 'Multiplier for wind forces',
        default = 1,
        override={'LIBRARY_OVERRIDABLE'},
        update=lambda s, c: update_prop(s, c, 'wiggle_wind')
    )

    wiggle_chain : BoolProperty(
        name = 'Chain',
        description = 'Bone affects its parent creating a physics chain',
        default = True,
        override={'LIBRARY_OVERRIDABLE'},
        update=lambda s, c: update_prop(s, c, 'wiggle_chain')
    )

    ### Head Properties ###
    wiggle_mass_head : FloatProperty(
        name = 'Mass',
        description = 'Mass of bone',
        min = 0.01,
        default = 1,
        override={'LIBRARY_OVERRIDABLE'},
        update=lambda s, c: update_prop(s, c, 'wiggle_mass_head')
    )

    wiggle_stiff_head : FloatProperty(
        name = 'Stiff',
        description = 'Spring stiffness coefficient, can be large numbers',
        min = 0,
        default = 400,
        override={'LIBRARY_OVERRIDABLE'},
        update=lambda s, c: update_prop(s, c, 'wiggle_stiff_head')
    )

    wiggle_stretch_head : FloatProperty(
        name = 'Stretch',
        description = 'Bone stretchiness factor, 0 to 1 range',
        min = 0,
        default = 0,
        max=1,
        override={'LIBRARY_OVERRIDABLE'},
        update=lambda s, c: update_prop(s, c, 'wiggle_stretch_head')
    )

    wiggle_damp_head : FloatProperty(
        name = 'Damp',
        description = 'Dampening coefficient, can be greater than 1',
        min = 0,
        default = 1,
        override={'LIBRARY_OVERRIDABLE'},
        update=lambda s, c: update_prop(s, c, 'wiggle_damp_head')
    )

    wiggle_gravity_head : FloatProperty(
        name = 'Gravity',
        description = 'Multiplier for scene gravity',
        default = 1,
        override={'LIBRARY_OVERRIDABLE'},
        update=lambda s, c: update_prop(s, c, 'wiggle_gravity_head')
    )

    wiggle_wind_ob_head : PointerProperty(
        name='Wind', 
        description='Wind force field object', 
        type=bpy.types.Object, 
        poll = wind_poll, 
        override={'LIBRARY_OVERRIDABLE'}, 
        update=lambda s, c: update_prop(s, c, 'wiggle_wind_ob_head')
    )

    wiggle_wind_head : FloatProperty(
        name = 'Wind',
        description = 'Multiplier for wind forces',
        default = 1,
        override={'LIBRARY_OVERRIDABLE'},
        update=lambda s, c: update_prop(s, c, 'wiggle_wind_head')
    )

    wiggle_chain_head : BoolProperty(
        name = 'Chain',
        description = 'Bone affects its parent creating a physics chain',
        default = True,
        override={'LIBRARY_OVERRIDABLE'},
        update=lambda s, c: update_prop(s, c, 'wiggle_chain_head')
    )

    ### Tail Colision ###
    wiggle_collider_type : EnumProperty(
        name='Collider Type',
        items=[('Object','Object','Collide with a selected mesh'),('Collection','Collection','Collide with all meshes in selected collection')],
        override={'LIBRARY_OVERRIDABLE'},
        update=lambda s, c: update_prop(s, c, 'wiggle_collider_type')
    )

    wiggle_collider : PointerProperty(
        name='Collider Object', 
        description='Mesh object to collide with', 
        type=bpy.types.Object, 
        poll = collider_poll, 
        override={'LIBRARY_OVERRIDABLE'}, 
        update=lambda s, c: update_prop(s, c, 'wiggle_collider')
    )

    wiggle_collider_collection : PointerProperty(
        name = 'Collider Collection', 
        description='Collection to collide with', 
        type=bpy.types.Collection, 
        override={'LIBRARY_OVERRIDABLE'}, 
        update=lambda s, c: update_prop(s, c, 'wiggle_collider_collection')
    )

    wiggle_radius : FloatProperty(
        name = 'Radius',
        description = 'Collision radius',
        min = 0,
        default = 0,
        override={'LIBRARY_OVERRIDABLE'},
        update=lambda s, c: update_prop(s, c, 'wiggle_radius')
    )

    wiggle_friction : FloatProperty(
        name = 'Friction',
        description = 'Friction when colliding',
        min = 0,
        default = 0.5,
        soft_max = 1,
        override={'LIBRARY_OVERRIDABLE'},
        update=lambda s, c: update_prop(s, c, 'wiggle_friction')
    )

    wiggle_bounce : FloatProperty(
        name = 'Bounce',
        description = 'Bounciness when colliding',
        min = 0,
        default = 0.5,
        soft_max = 1,
        override={'LIBRARY_OVERRIDABLE'},
        update=lambda s, c: update_prop(s, c, 'wiggle_bounce')
    )

    wiggle_sticky : FloatProperty(
        name = 'Sticky',
        description = 'Margin beyond radius to keep item stuck to surface',
        min = 0,
        default = 0,
        soft_max = 1,
        override={'LIBRARY_OVERRIDABLE'},
        update=lambda s, c: update_prop(s, c, 'wiggle_sticky')
    )

    ### Head Colision ###
    wiggle_collider_type_head : EnumProperty(
        name='Collider Type',
        items=[('Object','Object','Collide with a selected mesh'),('Collection','Collection','Collide with all meshes in selected collection')],
        override={'LIBRARY_OVERRIDABLE'},
        update=lambda s, c: update_prop(s, c, 'wiggle_collider_type_head')
    )

    wiggle_collider_head : PointerProperty(
        name='Collider Object', 
        description='Mesh object to collide with', 
        type=bpy.types.Object, 
        poll = collider_poll, 
        override={'LIBRARY_OVERRIDABLE'}, 
        update=lambda s, c: update_prop(s, c, 'wiggle_collider_head')
    )

    wiggle_collider_collection_head : PointerProperty(
        name = 'Collider Collection', 
        description='Collection to collide with', 
        type=bpy.types.Collection, 
        override={'LIBRARY_OVERRIDABLE'}, 
        update=lambda s, c: update_prop(s, c, 'wiggle_collider_collection_head')
    )

    wiggle_radius_head : FloatProperty(
        name = 'Radius',
        description = 'Collision radius',
        min = 0,
        default = 0,
        override={'LIBRARY_OVERRIDABLE'},
        update=lambda s, c: update_prop(s, c, 'wiggle_radius_head')
    )

    wiggle_friction_head : FloatProperty(
        name = 'Friction',
        description = 'Friction when colliding',
        min = 0,
        default = 0.5,
        soft_max = 1,
        override={'LIBRARY_OVERRIDABLE'},
        update=lambda s, c: update_prop(s, c, 'wiggle_friction_head')
    )

    wiggle_bounce_head : FloatProperty(
        name = 'Bounce',
        description = 'Bounciness when colliding',
        min = 0,
        default = 0.5,
        soft_max = 1,
        override={'LIBRARY_OVERRIDABLE'},
        update=lambda s, c: update_prop(s, c, 'wiggle_bounce_head')
    )

    wiggle_sticky_head : FloatProperty(
        name = 'Sticky',
        description = 'Margin beyond radius to keep item stuck to surface',
        min = 0,
        default = 0,
        soft_max = 1,
        override={'LIBRARY_OVERRIDABLE'},
        update=lambda s, c: update_prop(s, c, 'wiggle_sticky_head')
    )


classes = [
    WiggleBoneItem,
    WiggleItem,
    WiggleBone,
    WiggleBoneSettings,
    WiggleObject,
    FullBoneCollisionSettings,
    WiggleScene
]


def register():
    for cl in classes:
        bpy.utils.register_class(cl)

    bpy.types.Scene.wiggle = bpy.props.PointerProperty(type=WiggleScene, override={'LIBRARY_OVERRIDABLE'})
    bpy.types.Object.wiggle = bpy.props.PointerProperty(type=WiggleObject, override={'LIBRARY_OVERRIDABLE'})
    bpy.types.PoseBone.wiggle = bpy.props.PointerProperty(type=WiggleBone, override={'LIBRARY_OVERRIDABLE'})
    bpy.types.PoseBone.wiggle_settings = bpy.props.PointerProperty(type=WiggleBoneSettings, override={'LIBRARY_OVERRIDABLE'})

def unregister():
    for cl in reversed(classes):
        bpy.utils.unregister_class(cl)

    del bpy.types.Scene.wiggle
    del bpy.types.Object.wiggle
    del bpy.types.PoseBone.wiggle
    del bpy.types.PoseBone.wiggle_settings
