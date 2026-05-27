import bpy
from bpy.types import Panel, Operator

class WigglePanel:
    bl_category = 'Animation'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    @classmethod
    def poll(cls,context):
        return context.object
    
class WIGGLE_PT_Settings(WigglePanel, Panel):
    bl_label = 'Wiggle 2'
        
    def draw(self,context):
        row = self.layout.row()
        icon = 'HIDE_ON' if not context.scene.wiggle.wiggle_enable else 'SCENE_DATA'
        row.prop(context.scene.wiggle, "wiggle_enable", icon=icon, text="",emboss=False)
        if not context.scene.wiggle.wiggle_enable:
            row.label(text='Scene muted.')
            return
        if not context.object.type == 'ARMATURE':
            row.label(text = ' Select armature.')
            return
        if context.object.wiggle.wiggle.wiggle_freeze:
            row.prop(context.object.wiggle, 'wiggle_freeze',icon='FREEZE',icon_only=True,emboss=False)
            row.label(text = 'Wiggle Frozen after Bake.')
            return
        icon = 'HIDE_ON' if context.object.wiggle.wiggle_mute else 'ARMATURE_DATA'
        row.prop(context.object.wiggle, 'wiggle_mute',icon=icon,icon_only=True,invert_checkbox=True,emboss=False)
        if context.object.wiggle.wiggle_mute:
            row.label(text='Armature muted.')
            return
        if not context.active_pose_bone:
            row.label(text = ' Select pose bone.')
            return
        icon = 'HIDE_ON' if context.active_pose_bone.wiggle.wiggle_mute else 'BONE_DATA'
        row.prop(context.active_pose_bone.wiggle, 'wiggle_mute',icon=icon,icon_only=True,invert_checkbox=True,emboss=False)
        if context.active_pose_bone.wiggle.wiggle_mute:
            row.label(text='Bone muted.')
            return



classes = [
    #WIGGLE_PT_Settings
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)