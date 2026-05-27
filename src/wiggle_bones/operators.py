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

        for bone in context.selected_pose_bones:
            if not isinstance(bone, bpy.types.PoseBone) or bone == b: continue

            bone.wiggle.mute = b.wiggle.mute
            bone.wiggle.head = b.wiggle.head
            bone.wiggle.tail = b.wiggle.tail
            bone.wiggle.head_mute = b.wiggle.head_mute
            bone.wiggle.tail_mute = b.wiggle.tail_mute
        
            bone.wiggle.mass = b.wiggle.mass
            bone.wiggle.stiff = b.wiggle.stiff
            bone.wiggle.stretch = b.wiggle.stretch
            bone.wiggle.damp = b.wiggle.damp
            bone.wiggle.gravity = b.wiggle.gravity
            bone.wiggle.wind_ob = b.wiggle.wind_ob
            bone.wiggle.wind = b.wiggle.wind
            bone.wiggle.collider_type = b.wiggle.collider_type
            bone.wiggle.collider = b.wiggle.collider
            bone.wiggle.collider_collection = b.wiggle.collider_collection
            bone.wiggle.radius = b.wiggle.radius
            bone.wiggle.friction = b.wiggle.friction
            bone.wiggle.bounce = b.wiggle.bounce
            bone.wiggle.sticky = b.wiggle.sticky
            bone.wiggle.chain = b.wiggle.chain
        
            bone.wiggle.mass_head = b.wiggle.mass_head
            bone.wiggle.stiff_head = b.wiggle.stiff_head
            bone.wiggle.stretch_head = b.wiggle.stretch_head
            bone.wiggle.damp_head = b.wiggle.damp_head
            bone.wiggle.gravity_head = b.wiggle.gravity_head
            bone.wiggle.wind_ob_head = b.wiggle.wind_ob_head
            bone.wiggle.wind_head = b.wiggle.wind_head
            bone.wiggle.collider_type_head = b.wiggle.collider_type_head
            bone.wiggle.collider_head = b.wiggle.collider_head
            bone.wiggle.collider_collection_head = b.wiggle.collider_collection_head
            bone.wiggle.radius_head = b.wiggle.radius_head
            bone.wiggle.friction_head = b.wiggle.friction_head
            bone.wiggle.bounce_head = b.wiggle.bounce_head
            bone.wiggle.sticky_head = b.wiggle.sticky_head
            bone.wiggle.chain_head = b.wiggle.chain_head

        return {'FINISHED'}

class WiggleReset(Operator):
    """Reset scene wiggle physics to rest state"""
    bl_idname = "wiggle.reset"
    bl_label = "Reset Physics"
    
    @classmethod
    def poll(cls,context):
        return context.scene.wiggle.enable and context.mode in ['OBJECT', 'POSE']
    
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
        context.object.wiggle.freeze = True
        if not context.scene.wiggle.bake_overwrite:
            context.object.animation_data.action.name = 'WiggleAction'
        return {'FINISHED'}

class WiggleRebuild(Operator):
    """Rebuild scene Wiggle Bones list"""
    bl_idname = "wiggle.rebuild"
    bl_label = "Rebuild Wiggle World"
    
    @classmethod
    def poll(cls,context):
        return context.scene.wiggle.enable and context.mode in ['OBJECT', 'POSE']

classes =[
    WiggleCopy,
    WiggleReset,
    WiggleSelect,
    WiggleBake,
    WiggleRebuild
]

def register():
    for cl in classes:
        bpy.utils.register_class(cl)

def unregister():
    for cl in reversed(classes):
        bpy.utils.unregister_class(cl)