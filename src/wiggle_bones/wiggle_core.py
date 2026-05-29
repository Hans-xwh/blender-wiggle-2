import bpy
from mathutils import Vector, Matrix

def relative_matrix(m1,m2):
    return (m2.inverted() @ m1).inverted()

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
        
        ob.wiggle.enable = True
        wo = bpy.context.scene.wiggle.list.add()
        wo.name = ob.name
        for b in wigglebones:
            wb = wo.list.add()
            wb.name = b.name
            reset_bone(b)

def update_prop(self,context,prop): 
    if prop in ['mute','enable']:
        build_list()

    if not isinstance(self, (bpy.types.Object)):
        #for b in context.selected_pose_bones:  #Unsafe and doesnt work
        #    b[prop] = self[prop]
            
        if prop in ['head', 'tail']:
            build_list()
            for b in context.selected_pose_bones:
                reset_bone(b)
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