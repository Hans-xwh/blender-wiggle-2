from .wiggle_core import reset_bone, build_list

import bpy
from bpy.types import Operator


class WiggleCopy(Operator):
    """Copy active wiggle settings to selected bones"""
    bl_idname = "wiggle.copy"
    bl_label = "Copy Settings to Selected"
    
    @classmethod
    def poll(cls,context):
        return context.mode in ['POSE'] and context.active_pose_bone and (len(context.selected_pose_bones)>1)
    
    def execute(self,context):
        b = context.active_pose_bone
        b.wiggle_mute = b.wiggle_mute
        b.wiggle_head = b.wiggle_head
        b.wiggle_tail = b.wiggle_tail
        b.wiggle_head_mute = b.wiggle_head_mute
        b.wiggle_tail_mute = b.wiggle_tail_mute
        
        b.wiggle_mass = b.wiggle_mass
        b.wiggle_stiff = b.wiggle_stiff
        b.wiggle_stretch = b.wiggle_stretch
        b.wiggle_damp = b.wiggle_damp
        b.wiggle_gravity = b.wiggle_gravity
        b.wiggle_wind_ob = b.wiggle_wind_ob
        b.wiggle_wind = b.wiggle_wind
        b.wiggle_collider_type = b.wiggle_collider_type
        b.wiggle_collider = b.wiggle_collider
        b.wiggle_collider_collection = b.wiggle_collider_collection
        b.wiggle_radius = b.wiggle_radius
        b.wiggle_friction = b.wiggle_friction
        b.wiggle_bounce = b.wiggle_bounce
        b.wiggle_sticky = b.wiggle_sticky
        b.wiggle_chain = b.wiggle_chain
        
        b.wiggle_mass_head = b.wiggle_mass_head
        b.wiggle_stiff_head = b.wiggle_stiff_head
        b.wiggle_stretch_head = b.wiggle_stretch_head
        b.wiggle_damp_head = b.wiggle_damp_head
        b.wiggle_gravity_head = b.wiggle_gravity_head
        b.wiggle_wind_ob_head = b.wiggle_wind_ob_head
        b.wiggle_wind_head = b.wiggle_wind_head
        b.wiggle_collider_type_head = b.wiggle_collider_type_head
        b.wiggle_collider_head = b.wiggle_collider_head
        b.wiggle_collider_collection_head = b.wiggle_collider_collection_head
        b.wiggle_radius_head = b.wiggle_radius_head
        b.wiggle_friction_head = b.wiggle_friction_head
        b.wiggle_bounce_head = b.wiggle_bounce_head
        b.wiggle_sticky_head = b.wiggle_sticky_head
        b.wiggle_chain_head = b.wiggle_chain_head
        return {'FINISHED'}

class WiggleReset(Operator):
    """Reset scene wiggle physics to rest state"""
    bl_idname = "wiggle.reset"
    bl_label = "Reset Physics"
    
    @classmethod
    def poll(cls,context):
        return context.scene.wiggle_enable and context.mode in ['OBJECT', 'POSE']
    
    def execute(self,context):
        context.scene.wiggle.reset = True
        context.scene.frame_set(context.scene.frame_current)
        context.scene.wiggle.reset = False
        rebuild = False
        for wo in context.scene.wiggle.list:
            ob = context.scene.objects.get(wo.name)
            if not ob:
                rebuild = True
                continue
            for wb in wo.list:
                b = ob.pose.bones.get(wb.name)
                if not b:
                    rebuild = True
                    continue
                reset_bone(b)
        context.scene.wiggle.lastframe = context.scene.frame_current
        if rebuild: build_list()
        return {'FINISHED'}

class WiggleSelect(Operator):
    """Select wiggle bones on selected objects in pose mode"""
    bl_idname = "wiggle.select"
    bl_label = "Select Enabled"

    @classmethod
    def poll(cls,context):
        return context.mode in ['POSE']

    def execute(self,context):
        bpy.ops.pose.select_all(action='DESELECT')
        rebuild = False
        for wo in context.scene.wiggle.list:
            ob = context.scene.objects.get(wo.name)
            if not ob:
                rebuild = True
                continue
            for wb in wo.list:
                b = ob.pose.bones.get(wb.name)
                if not b:
                    rebuild = True
                    continue
                b.select = True  # Select the pose bone directly
        if rebuild: build_list()
        return {'FINISHED'}
    
class WiggleBake(Operator):
    """Bake this object's visible wiggle bones to keyframes"""
    bl_idname = "wiggle.bake"
    bl_label = "Bake Wiggle"
    
    @classmethod
    def poll(cls,context):
        return context.object
    
    def execute(self,context):
        def push_nla():
            if context.scene.wiggle.bake_overwrite: return
            if not context.scene.wiggle.bake_nla: return
            if not context.object.animation_data: return
            if not context.object.animation_data.action: return
            action = context.object.animation_data.action
            track = context.object.animation_data.nla_tracks.new()
            track.name = action.name
            track.strips.new(action.name, int(action.frame_range[0]), action)
            
        push_nla()
        
        bpy.ops.wiggle.reset()
            
        #preroll
        duration = context.scene.frame_end - context.scene.frame_start
        preroll = context.scene.wiggle.preroll
        context.scene.wiggle.is_preroll = False
        bpy.ops.wiggle.select()
        bpy.ops.wiggle.reset()
        while preroll >= 0:
            if context.scene.wiggle.loop:
                frame = context.scene.frame_end - (preroll%duration)
                context.scene.frame_set(frame)
            else:
                context.scene.frame_set(context.scene.frame_start)
            context.scene.wiggle.is_preroll = True
            preroll -= 1

        #bake
        if bpy.app.version[0] >= 4 and bpy.app.version[1] > 0:
            # Before calling bpy.ops.nla.bake(), clear any conflicting IDProperties
            for obj in bpy.context.selected_objects:
                if obj.type == 'ARMATURE':
                    for bone in obj.pose.bones:
                        if "wiggle" in bone:  # Only clear properties starting with "wiggle"
                            del bone["wiggle"]  # Remove the 'wiggle' property
                
            bpy.ops.nla.bake(frame_start = context.scene.frame_start,
                            frame_end = context.scene.frame_end,
                            only_selected = True,
                            visual_keying = True,
                            use_current_action = context.scene.wiggle.bake_overwrite,
                            bake_types={'POSE'},
                            channel_types={'LOCATION','ROTATION','SCALE'})
        else:
            bpy.ops.nla.bake(frame_start = context.scene.frame_start,
                            frame_end = context.scene.frame_end,
                            only_selected = True,
                            visual_keying = True,
                            use_current_action = context.scene.wiggle.bake_overwrite,
                            bake_types={'POSE'})
        context.scene.wiggle.is_preroll = False
        context.object.wiggle_freeze = True
        if not context.scene.wiggle.bake_overwrite:
            context.object.animation_data.action.name = 'WiggleAction'
        return {'FINISHED'}

classes =[
    WiggleCopy,
    WiggleReset,
    WiggleSelect,
    WiggleBake
]

def register():
    for cl in classes:
        bpy.utils.register_class(cl)

def unregister():
    for cl in reversed(classes):
        bpy.utils.unregister_class(cl)