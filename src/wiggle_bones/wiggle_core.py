import bpy
from mathutils import Vector, Matrix

def relative_matrix(m1,m2):
    return (m2.inverted_safe() @ m1).inverted_safe()

def flatten(mat):
    dim = len(mat)
    return [mat[j][i] for i in range(dim) 
                      for j in range(dim)]

def reset_scene():
    for wo in bpy.context.scene.wiggle.list:
        reset_ob(bpy.data.objects.get(wo.name))
                              
def reset_ob(ob):
    wo = bpy.context.scene.wiggle.list.get(ob.name)
    for wb in wo.list:
        reset_bone(bpy.data.objects.get(wo.name).pose.bones.get(wb.name))

def reset_bone(b):
    b.wiggle.position = b.wiggle.position_last = (b.id_data.matrix_world @ Matrix.Translation(b.tail)).translation
    b.wiggle.position_head = b.wiggle.position_last_head = (b.id_data.matrix_world @ b.matrix).translation
    b.wiggle.velocity = b.wiggle.velocity_head = b.wiggle.collision_normal = b.wiggle.collision_normal_head = Vector((0,0,0))
    b.wiggle.matrix = flatten(b.id_data.matrix_world @ b.matrix)

def build_list():
    bpy.context.scene.wiggle.list.clear()
    for ob in bpy.context.scene.objects:
        if ob.type != 'ARMATURE': continue
        wigglebones = []
        for b in ob.pose.bones:
            if b.wiggle.tail or (b.wiggle.head and not b.bone.use_connect):
                wigglebones.append(b)
                b.wiggle.enable = True
            else:
                b.wiggle.enable = False
                
        if not wigglebones:
            ob.wiggle.enable = False
            continue
        
        ob.wiggle.enable = True                     #scene.wiggle.list: CollectionProperty(type=WiggleItem)
        wo = bpy.context.scene.wiggle.list.add()    #wo: WiggleItem

        wo.name = ob.name
        #wo.use_pin = ob.wiggle.use_pin
        if ob.wiggle.use_pin:
            wo.solver = ob.wiggle.solver
        else: wo.solver = 'FW'

        for b in wigglebones:
            wb = wo.list.add()      #wb:WiggleBoneItem
            wb.name = b.name
            reset_bone(b)
    bpy.context.scene.wiggle.syncing = False    #Just in case it crashes while syncing, flag will be cleared on rebuild.

def update_prop(self, context:bpy.types.Context, prop): 
    if context.scene.wiggle.auto_sync and context.mode == 'POSE' and context.active_pose_bone:
        if context.scene.wiggle.syncing == False:
            context.scene.wiggle.syncing = True

            b:bpy.types.PoseBone
            for b in context.selected_pose_bones:  #Still a bit unsafe but now works
                if b == context.active_pose_bone: continue
                if b.wiggle.mute or not (b.wiggle.head or b.wiggle.tail): continue   #Skips disabled bones

                setattr(b.wiggle, prop, getattr(self, prop))
            context.scene.wiggle.syncing = False

    #edge case where is_rendering gets stuck, the user fiddling with any setting should unstuck it!
    context.scene.wiggle.is_rendering = False
         
def get_parent(b):
    p = b.parent
    if not p: return None
    par = p if (p.wiggle.enable and (not p.wiggle.mute) and ((p.wiggle.head and not p.bone.use_connect) or p.wiggle.tail)) else get_parent(p)
    return par

def length_world(b):
    return (b.id_data.matrix_world @ b.head - b.id_data.matrix_world @ b.tail).length

def collider_poll(self, object):
    return object.type == 'MESH'

def wind_poll(self, object):
    return object.field and object.field.type =='WIND'