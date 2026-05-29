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
        icon = 'HIDE_ON' if not context.scene.wiggle.enable else 'SCENE_DATA'
        row.prop(context.scene.wiggle, "enable", icon=icon, text="",emboss=False)

        if not context.scene.wiggle.enable:
            row.label(text='Scene muted.')
            return
        
        if not context.object.type == 'ARMATURE':
            row.label(text = ' Select armature.')
            return
        
        if context.object.wiggle.freeze:
            row.prop(context.object.wiggle, 'freeze',icon='FREEZE',icon_only=True,emboss=False)
            row.label(text = 'Wiggle Frozen after Bake.')
            return
        
        icon = 'HIDE_ON' if context.object.wiggle.mute else 'ARMATURE_DATA'
        row.prop(context.object.wiggle, 'mute', icon=icon, icon_only=True, invert_checkbox=True, emboss=False)
        if context.object.wiggle.mute:
            row.label(text='Armature muted.')
            return
        
        if not context.active_pose_bone:
            row.label(text = ' Select pose bone.')
            return
        
        icon = 'HIDE_ON' if context.active_pose_bone.wiggle.mute else 'BONE_DATA'
        row.prop(context.active_pose_bone.wiggle, 'mute', icon=icon,icon_only=True,invert_checkbox=True,emboss=False)
        if context.active_pose_bone.wiggle.mute:
            row.label(text='Bone muted.')
            return

class WIGGLE_PT_Head(WigglePanel, bpy.types.Panel):
    bl_label = ''
    bl_parent_id = 'WIGGLE_PT_Settings'
    bl_options = {'HEADER_LAYOUT_EXPAND'}
    
    @classmethod
    def poll(cls, context):
        return context.scene.wiggle.enable and context.object and not context.object.wiggle.mute and context.active_pose_bone and not context.active_pose_bone.wiggle.mute and not context.active_pose_bone.bone.use_connect
    
    def draw_header(self, context):
        row = self.layout.row(align=True)
        row.prop(context.active_pose_bone.wiggle, 'head')
    
    def draw(self, context):
        b = context.active_pose_bone
        if not b.wiggle.head: 
            return
        
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        def drawprops(layout, b, props):
            for p in props:
                layout.prop(b, p)
        
        # Get all selected bones
        selected_bones = context.selected_pose_bones

        # Function to set properties for all selected bones
        #def set_props_for_selected(attr, value):
        #    for bone in selected_bones:
        #        setattr(bone, attr, value)
        
        col = layout.column(align=True)
        drawprops(col, b.wiggle, ['mass_head', 'stiff_head', 'stretch_head', 'damp_head'])
        col.separator()
        col.prop(b.wiggle, 'gravity_head')
        
        # Wind Object
        row = col.row(align=True)
        row.prop(b.wiggle, 'wind_ob_head')
        
        # Apply wind object to all selected bones if changed
        #if b.wiggle_wind_ob_head:
        #    set_props_for_selected('wiggle_wind_ob_head', b.wiggle_wind_ob_head)
        
        sub = row.row(align=True)
        sub.ui_units_x = 5
        sub.prop(b.wiggle, 'wind_head', text='')
        col.separator()
        
        # Collision settings
        col.prop(b.wiggle, 'collider_type_head', text='Collisions')

        collision = False
        
        if b.wiggle.collider_type_head == 'Object':
            row = col.row(align=True)
            row.prop_search(b.wiggle, 'collider_head', context.scene, 'objects', text=' ')
            
            # Apply collider to all selected bones if changed
            if b.wiggle.collider_head:
                #set_props_for_selected('wiggle_collider_head', b.wiggle_collider_head)
                
                if b.wiggle.collider_head.name in context.scene.objects:
                    collision = True
                else:
                    row.label(text='', icon='UNLINKED')
        else:
            row = col.row(align=True)
            row.prop_search(b.wiggle, 'collider_collection_head', bpy.data, 'collections', text=' ')
            
            # Apply collider collection to all selected bones if changed
            if b.wiggle.collider_collection_head:
                #set_props_for_selected('wiggle_collider_collection_head', b.wiggle_collider_collection_head)
                
                if b.wiggle.collider_collection_head in context.scene.collection.children_recursive:
                    collision = True
                else:
                    row.label(text='', icon='UNLINKED')

        if collision:
            col = layout.column(align=True)
            drawprops(col, b.wiggle, ['radius_head', 'friction_head', 'bounce_head', 'sticky_head'])
        
        layout.prop(b.wiggle, 'chain_head')

class WIGGLE_PT_Tail(WigglePanel, bpy.types.Panel):
    bl_label = ''
    bl_parent_id = 'WIGGLE_PT_Settings'
    bl_options = {'HEADER_LAYOUT_EXPAND'}
    
    @classmethod
    def poll(cls, context):
        return context.scene.wiggle.enable and context.object and not context.object.wiggle.mute and context.active_pose_bone and not context.active_pose_bone.wiggle.mute
    
    def draw_header(self, context):
        row = self.layout.row(align=True)
        row.prop(context.active_pose_bone.wiggle, 'tail')
        
    def draw(self, context):
        b = context.active_pose_bone
        if not b.wiggle.tail: 
            return
        
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        def drawprops(layout, b, props):
            for p in props:
                layout.prop(b, p)

        # Get all selected bones
        selected_bones = context.selected_pose_bones

        # Function to set properties for all selected bones
        #Draw context is read only so uhhhh this cant go here -xwh
        #def set_props_for_selected(attr, value):
        #    for bone in selected_bones:
        #        setattr(bone, attr, value)
        
        col = layout.column(align=True)
        drawprops(col, b.wiggle, ['mass', 'stiff', 'stretch', 'damp'])
        col.separator()
        col.prop(b.wiggle, 'gravity')
        
        # Wind Object
        row = col.row(align=True)
        row.prop(b.wiggle, 'wind_ob')

        # Apply wind object to all selected bones if changed
        #if b.wiggle_wind_ob:
        #    set_props_for_selected('wiggle_wind_ob', b.wiggle_wind_ob)
        
        sub = row.row(align=True)
        sub.ui_units_x = 5
        sub.prop(b.wiggle, 'wind', text='')
        col.separator()
        
        # Collision settings
        col.prop(b.wiggle, 'collider_type', text='Collisions')

        collision = False
        
        if b.wiggle.collider_type == 'Object':
            row = col.row(align=True)
            row.prop_search(b.wiggle, 'collider', context.scene, 'objects', text=' ')
            
            # Apply to all selected bones if changed
            if b.wiggle.collider:
                #set_props_for_selected('wiggle_collider', b.wiggle_collider)
                
                if b.wiggle.collider.name in context.scene.objects:
                    collision = True
                else:
                    row.label(text='', icon='UNLINKED')
        else:
            row = col.row(align=True)
            row.prop_search(b.wiggle, 'collider_collection', bpy.data, 'collections', text=' ')
            
            # Apply to all selected bones if changed
            if b.wiggle.collider_collection:
                #set_props_for_selected('wiggle_collider_collection', b.wiggle_collider_collection)
                
                if b.wiggle.collider_collection in context.scene.collection.children_recursive:
                    collision = True
                else:
                    row.label(text='', icon='UNLINKED')

        if collision:
            col = layout.column(align=True)
            drawprops(col, b.wiggle, ['radius', 'friction', 'bounce', 'sticky'])
        
        layout.prop(b.wiggle, 'chain')

class WIGGLE_PT_Utilities(WigglePanel,bpy.types.Panel):
    bl_label = 'Global Wiggle Utilities'
    bl_parent_id = 'WIGGLE_PT_Settings'
    bl_options = {"DEFAULT_CLOSED"}
    
    @classmethod
    def poll(cls,context):
        return context.scene.wiggle.enable
    
    def draw(self,context):
        layout = self.layout
        layout.use_property_split=True
        layout.use_property_decorate=False
        col = layout.column(align=True)

        if context.object.wiggle.enable and context.mode == 'POSE':
            col.operator('wiggle.copy')
            col.operator('wiggle.select')
        col.operator('wiggle.reset')

        layout.prop(context.scene.wiggle, 'loop')
        layout.prop(context.scene.wiggle, 'iterations')

        layout.separator()
        layout.operator('wiggle.cleanup')

class WIGGLE_PT_Bake(WigglePanel,bpy.types.Panel):
    bl_label = 'Bake Wiggle'
    bl_parent_id = 'WIGGLE_PT_Utilities'
    bl_options = {"DEFAULT_CLOSED"}
    
    @classmethod
    def poll(cls,context):
        return context.scene.wiggle.enable and context.object.wiggle.enable and context.mode == 'POSE'
    
    def draw(self,context):
        layout = self.layout
        layout.use_property_split=True
        layout.use_property_decorate=False
        layout.prop(context.scene.wiggle, 'preroll')
        layout.prop(context.scene.wiggle, 'bake_overwrite')
        row = layout.row()
        row.enabled = not context.scene.wiggle.bake_overwrite
        row.prop(context.scene.wiggle, 'bake_nla')
        layout.operator('wiggle.bake')

class WIGGLE_PT_Fullbone_Collision(bpy.types.Panel):
    bl_label = "Full Bone Collision Settings"
    bl_idname = "WIGGLE_PT_Fullbone_Collision"
    bl_parent_id = "WIGGLE_PT_Utilities"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI' 
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        fullbone = context.scene.wiggle.full_bone_collision

        layout.prop(fullbone, "enable_fullbone_collision")
        if fullbone.enable_fullbone_collision:
            layout.prop(fullbone, "steps")
            layout.prop(fullbone, "collision_threshold")
            layout.prop(fullbone, "dot_threshold")

classes = [
    WIGGLE_PT_Settings,
    WIGGLE_PT_Head,
    WIGGLE_PT_Tail,
    WIGGLE_PT_Utilities,
    WIGGLE_PT_Bake,
    WIGGLE_PT_Fullbone_Collision
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)