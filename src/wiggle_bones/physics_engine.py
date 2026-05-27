from .wiggle_core import build_list, relative_matrix, flatten, get_parent, length_world, reset_scene, reset_ob, reset_bone

import bpy
from mathutils import Vector, Matrix, Quaternion
from bpy.app.handlers import persistent


def collide(b, dg, head=False):
    dt = bpy.context.scene.wiggle.dt
    
    if head:
        pos = b.wiggle.position_head
        vel = b.wiggle.velocity_head
        cp = b.wiggle.collision_point_head
        co = b.wiggle.collision_ob_head
        cn = b.wiggle.collision_normal_head
        
        collider_type = b.wiggle.collider_type_head
        wiggle_collider = b.wiggle.collider_head
        wiggle_collection = b.wiggle.collider_collection_head
        
        radius = b.wiggle.radius_head
        sticky = b.wiggle.sticky_head
        bounce = b.wiggle.bounce_head
        friction = b.wiggle.friction_head
    else:
        pos = b.wiggle.position
        vel = b.wiggle.velocity
        cp = b.wiggle.collision_point
        co = b.wiggle.collision_ob
        cn = b.wiggle.collision_normal
        
        collider_type = b.wiggle.collider_type
        wiggle_collider = b.wiggle.collider
        wiggle_collection = b.wiggle.collider_collection
        
        radius = b.wiggle.radius
        sticky = b.wiggle.sticky
        bounce = b.wiggle.bounce
        friction = b.wiggle.friction
        
    colliders = []
    if collider_type == 'Object' and wiggle_collider:
        if wiggle_collider.name in bpy.context.scene.objects:
            colliders = [wiggle_collider]
    if collider_type == 'Collection' and wiggle_collection:
        if wiggle_collection in bpy.context.scene.collection.children_recursive:
            colliders = [ob for ob in wiggle_collection.objects if ob.type == 'MESH']
            
    col = False
    for collider in colliders:
        cmw = collider.matrix_world
        p = collider.closest_point_on_mesh(cmw.inverted() @ pos, depsgraph=dg)
        n = (cmw.to_quaternion().to_matrix().to_4x4() @ p[2]).normalized()
        i = cmw @ p[1]
        v = i-pos
        
        if (n.dot(v.normalized()) > 0.01) or (v.length < radius) or (co and (v.length < (radius+sticky))):
            if n.dot(v.normalized()) > 0: #vec is below
                nv = v.normalized()
            else: #normal is opposite dir to vec
                nv = -v.normalized()
            pos = i + nv*radius
            
            if co:
                collision_point = co.matrix_world @ cp
                pos = pos.lerp(collision_point, friction) # min(1,friction*60*dt))
            col = True
            co = collider
            cp = relative_matrix(cmw, Matrix.Translation(pos)).translation
            cn = nv
    if not col:
        co = None
    
    if head:
        b.wiggle.position_head = pos
        b.wiggle.collision_point_head = cp
        b.wiggle.collision_ob_head = co  
        b.wiggle.collision_normal_head = cn
    else:
        b.wiggle.position = pos
        b.wiggle.collision_point = cp
        b.wiggle.collision_ob = co  
        b.wiggle.collision_normal = cn

def collide_full_bone(b, dg):
    dt = bpy.context.scene.wiggle.dt

    # Lists for head and tail positions
    pos_head = b.wiggle.position_head
    vel_head = b.wiggle.velocity_head
    cp_head = b.wiggle.collision_point_head
    co_head = b.wiggle.collision_ob_head
    cn_head = b.wiggle.collision_normal_head

    pos_tail = b.wiggle.position_tail
    vel_tail = b.wiggle.velocity_tail
    cp_tail = b.wiggle.collision_point_tail
    co_tail = b.wiggle.collision_ob_tail
    cn_tail = b.wiggle.collision_normal_tail

    steps = bpy.context.scene.wiggle.full_bone_collision.steps
    collision_occurred = False
    collision_data = []
    collision_threshold = bpy.context.scene.wiggle.full_bone_collision.collision_threshold  # Minimum movement to count as a collision
    dot_threshold = bpy.context.scene.wiggle.full_bone_collision.dot_threshold  # Dot product sensitivity
    previous_cp = None  # Track the last collision point to avoid duplicates

    colliders = []
    if b.wiggle.collider_type == 'Object' and b.wiggle.collider:
        if b.wiggle.collider.name in bpy.context.scene.objects:
            colliders = [b.wiggle.collider]
    elif b.wiggle.collider_type == 'Collection' and b.wiggle.collider_collection:
        if b.wiggle.collider_collection in bpy.context.scene.collection.children_recursive:
            colliders = [ob for ob in b.wiggle.collider_collection.objects if ob.type == 'MESH']

    for i in range(steps + 1):
        t = i / steps
        pos = pos_head.lerp(pos_tail, t)
        vel = vel_head.lerp(vel_tail, t)

        for collider in colliders:
            cmw = collider.matrix_world
            p = collider.closest_point_on_mesh(cmw.inverted() @ pos, depsgraph=dg)
            n = (cmw.to_quaternion().to_matrix().to_4x4() @ p[2]).normalized()
            i = cmw @ p[1]
            v = i - pos

            if v.length < collision_threshold:
                continue  # Skip if the movement is too small

            dot_check = abs(n.dot(v.normalized())) > dot_threshold
            radius_check = v.length < b.wiggle.radius

            # Skip duplicate points by checking proximity to last collision point
            if previous_cp and (previous_cp - i).length < collision_threshold:
                continue

            if dot_check or radius_check:
                nv = v.normalized() if n.dot(v.normalized()) > 0 else -v.normalized()
                pos = i + nv * (b.wiggle.radius * 0.5)
                if co_head:
                    collision_point = co_head.matrix_world @ cp_head
                    pos = pos.lerp(collision_point, b.wiggle.friction * 0.5)

                collision_occurred = True
                co_head = collider
                cp_head = relative_matrix(cmw, Matrix.Translation(pos)).translation
                cn_head = nv
                collision_data.append({
                    'position': pos,
                    'collider': collider,
                    'normal': cn_head,
                    'point': cp_head
                })

                previous_cp = cp_head  # Update last collision point

    if collision_occurred:
        b.wiggle.position_head = pos_head.lerp(pos, 0.5)
        b.wiggle.collision_point_head = cp_head
        b.wiggle.collision_ob_head = co_head
        b.wiggle.collision_normal_head = cn_head
        b.wiggle.position_tail = pos_tail.lerp(pos, 0.5)
        b.wiggle.collision_point_tail = cp_head
        b.wiggle.collision_ob_tail = co_head
        b.wiggle.collision_normal_tail = cn_head

def update_matrix(b,last=False):
    loc = Matrix.Translation(Vector((0,0,0)))
    p = get_parent(b)
    if p:
        mat = p.wiggle.matrix @ relative_matrix(p.matrix, b.matrix)
        if b.bone.inherit_scale == 'FULL':
            m2 = mat
        else:
            diff = relative_matrix(p.matrix, b.matrix)
            lo = Matrix.Translation((p.wiggle.matrix @ diff).translation)
            ro = p.wiggle.matrix.to_quaternion().to_matrix().to_4x4() @ diff.to_quaternion().to_matrix().to_4x4()
            sc = Matrix.LocRotScale(None,None,(b.id_data.matrix_world @ b.matrix).decompose()[2])
            m2 = lo @ ro @ sc
            
    else:
        mat = b.id_data.matrix_world @ b.matrix
        m2 = mat
            
    if b.wiggle.head and not b.bone.use_connect:
        m2 = Matrix.Translation(b.wiggle.position_head - m2.translation) @ m2
        loc = Matrix.Translation(relative_matrix(mat, Matrix.Translation(b.wiggle.position_head)).translation)
        mat = m2
    vec = relative_matrix(m2, Matrix.Translation(b.wiggle.position)).translation
    rxz = vec.to_track_quat('Y','Z')
    rot = rxz.to_matrix().to_4x4()
    
    if b.bone.inherit_scale == 'FULL':
        l0 = b.bone.length
        l1=relative_matrix(mat, Matrix.Translation(b.wiggle.position)).translation.length
        sy = l1/l0
    else:
        par = b.parent
        if par:
            sy=(b.id_data.matrix_world @ par.matrix @ relative_matrix(par.matrix, b.matrix).translation - b.wiggle.position).length/length_world(b)
            if p:
                sy = (p.wiggle.matrix @ relative_matrix(p.matrix, b.matrix).translation - b.wiggle.position).length/length_world(b)
        else:
            sy = (b.id_data.matrix_world @ b.matrix.translation - b.wiggle.position).length/length_world(b)
    
    if b.wiggle.head and not b.bone.use_connect:
        sy = (b.wiggle.position_head - b.wiggle.position).length/length_world(b)
            
    scale = Matrix.Scale(sy,4,Vector((0,1,0)))
    
    if last:
        const = False
        for c in b.constraints:
            if c.enabled: # and not (c.type in ['DAMPED_TRACK', 'TRACK_TO']):
                const = True 
        if const:
            b.matrix = b.bone.matrix_local @ b.matrix_basis @ loc @ rot @ scale
        else:
            b.matrix = b.matrix @ loc @ rot @ scale
    b.wiggle.matrix = flatten(m2 @ rot @ scale)

def get_pin(b):
    for c in b.constraints:
        if c.type in ['DAMPED_TRACK','TRACK_TO','LOCKED_TRACK'] and c.target and not c.mute:
            return c
    return None

def pin(b):
    c = get_pin(b)
    if c:
        goal = c.target.matrix_world
        if c.subtarget:
            goal = goal @ c.target.pose.bones[c.subtarget].matrix
        b.wiggle.position = b.wiggle.position*(1-c.influence) + goal.translation*c.influence

#can include gravity, wind, etc    
def move(b,dg):
    dt = bpy.context.scene.wiggle.dt
    dt2 = dt * dt
    if dt:
        if b.wiggle.tail:
            damp = max(min(1 - b.wiggle.damp * dt, 1), 0) 
            b.wiggle.velocity = b.wiggle.velocity * damp
            F = bpy.context.scene.gravity * b.wiggle.gravity
            if b.wiggle.wind_ob:
                dir = b.wiggle.wind_ob.matrix_world.to_quaternion().to_matrix().to_4x4() @ Vector((0, 0, 1))
                fac = 1 - b.wiggle.wind_ob.field.wind_factor * abs(dir.dot((b.wiggle.position - b.wiggle.matrix.translation).normalized()))
                F += dir * fac * b.wiggle.wind_ob.field.strength * b.wiggle.wind / b.wiggle.mass
            b.wiggle.position += b.wiggle.velocity + F * dt2
            pin(b)
            if bpy.context.scene.wiggle.full_bone_collision.enable_fullbone_collision:
                collide_full_bone(b, dg)
            else:
                collide(b, dg)

        if b.wiggle.head and not b.bone.use_connect:
            damp = max(min(1 - b.wiggle.damp_head * dt, 1), 0)
            b.wiggle.velocity_head = b.wiggle.velocity_head * damp
            F = bpy.context.scene.gravity * b.wiggle.gravity_head
            if b.wiggle.wind_ob_head:
                dir = b.wiggle.wind_ob_head.matrix_world.to_quaternion().to_matrix().to_4x4() @ Vector((0, 0, 1))
                F += dir * b.wiggle.wind_ob_head.field.strength * b.wiggle.wind_head / b.wiggle.mass_head
            b.wiggle.position_head += b.wiggle.velocity_head + F * dt2
            if bpy.context.scene.wiggle.full_bone_collision.enable_fullbone_collision:
                collide_full_bone(b, dg)
            else:
                collide(b, dg, True)

        update_matrix(b)

def constrain(b,i,dg):
    dt = bpy.context.scene.wiggle.dt
    
    def get_fac(mass1,mass2):
        return 0.5 if mass1 == mass2 else mass1/(mass1+mass2)
    
    def spring(target, position, stiff):
        s = target - position
        Fs = s * stiff / bpy.context.scene.wiggle.iterations
        if (Fs*dt*dt).length > s.length:
            return s
        return Fs*dt*dt
    
    def stretch(target, position, fac):
        s = target - position
        return s*(1-fac)

    if dt:
        
        p=get_parent(b)
        if p:
            mat = p.wiggle.matrix @ relative_matrix(p.matrix, b.matrix)
        else:
            mat = b.id_data.matrix_world @ b.matrix
        update_p = False  
        
        #spring
        if b.wiggle.head and not b.bone.use_connect:
            target = mat.translation
            s = spring(target, b.wiggle.position_head, b.wiggle.stiff_head)
            if p and b.wiggle.chain_head:
                if p.wiggle.tail:
                    fac = get_fac(b.wiggle.mass_head, p.wiggle.mass) if i else p.wiggle.stretch
                    p.wiggle.position -= s*fac
                else:
                    fac = get_fac(b.wiggle.mass_head, p.wiggle.mass_head)
                    p.wiggle.position_head -= s*fac
                b.wiggle.position_head += s*(1-fac)
            else:
                b.wiggle.position_head += s

            mat = Matrix.LocRotScale(b.wiggle.position_head, mat.decompose()[1], b.matrix.decompose()[2])
            target = mat @ Vector((0,b.bone.length,0))
            if b.wiggle.tail:
                s = spring(target, b.wiggle.position, b.wiggle.stiff)
                if b.wiggle.chain:
                    fac = get_fac(b.wiggle.mass, b.wiggle.mass_head)
                    b.wiggle.position_head -= s*fac
                    b.wiggle.position += s*(1-fac)
                else:
                    b.wiggle.position += s
            else:
                b.wiggle.position = target
        else:
            mat = Matrix.LocRotScale(mat.decompose()[0], mat.decompose()[1],b.matrix.decompose()[2])
            target = mat @ Vector((0, b.bone.length,0))
            s = spring(target, b.wiggle.position, b.wiggle.stiff)
            if p and b.wiggle.chain and p.wiggle.tail: # and b.bone.use_connect:
                fac = get_fac(b.wiggle.mass, p.wiggle.mass)# if i else p.wiggle.stretch
                if get_pin(b): fac = 1 - b.wiggle.stretch
                if i == 0: fac = p.wiggle.stretch
                if p == b.parent and b.bone.use_connect: #direct parent optimization
                    p.wiggle.position -= s*fac
                else:
                    tailpos = b.wiggle.matrix @ Vector((0,b.bone.length,0))
                    midpos = (b.wiggle.matrix.translation + tailpos)/2
                    v1 = midpos-p.wiggle.matrix.translation
                    tailpos -= s*fac
                    midpos = (b.wiggle.matrix.translation + tailpos)/2
                    v2 = midpos-p.wiggle.matrix.translation
                    sc = v2.length/v1.length
                    q = v1.rotation_difference(v2)
                    v3 = q @ (p.wiggle.position - p.wiggle.matrix.translation)
                    p.wiggle.position = p.wiggle.matrix.translation + v3*sc
                    
                b.wiggle.position += s*(1-fac)
                update_p = True
            else:
                b.wiggle.position += s
                
        #stretch
        if b.wiggle.head and not b.bone.use_connect:
            if p:
                if b.parent == p and p.wiggle.tail:
                    target = p.wiggle.position + (b.wiggle.position_head - p.wiggle.position).normalized()*(b.id_data.matrix_world @ b.head - b.id_data.matrix_world @ p.tail).length
                else: #indirect
                    targetpos = p.wiggle.matrix @ relative_matrix(p.matrix, b.parent.matrix) @ Vector((0,b.parent.length,0))
                    target = targetpos + (b.wiggle.position_head - targetpos).normalized()*(b.id_data.matrix_world @ b.head - b.id_data.matrix_world @ b.parent.tail).length
            elif b.parent:
                ptail = b.id_data.matrix_world @ b.parent.tail
                target = ptail + (b.wiggle.position_head - ptail).normalized() * (b.id_data.matrix_world @ b.head - b.id_data.matrix_world @ b.parent.tail).length
            else:
                target = mat.translation
            s = stretch(target, b.wiggle.position_head, b.wiggle.stretch_head)
            if p and b.wiggle.chain_head:
                if p.wiggle.tail:
                    fac = get_fac(b.wiggle.mass_head, p.wiggle.mass) if i else p.wiggle.stretch
                    tailpos = p.wiggle.matrix @ relative_matrix(p.matrix, b.parent.matrix) @ Vector((0,b.parent.length,0))
                    ratio = (p.wiggle.matrix.translation - p.wiggle.position).length/(p.wiggle.matrix.translation - tailpos).length
                    tailpos -= s*fac
                    p.wiggle.position -= s*ratio*fac
                else: #DOES THIS ASSUME ANYTHING? (No, head only translates, no bone stretching)
                    fac = get_fac(b.wiggle.mass_head, p.wiggle.mass_head) if i else p.wiggle.stretch_head
                    p.wiggle.position_head -= s*fac
                b.wiggle.position_head += s*(1-fac)
            else:
                b.wiggle.position_head += s
                
            target = b.wiggle.position_head + (b.wiggle.position - b.wiggle.position_head).normalized()*length_world(b)
            if b.wiggle.tail: #tail stretch only relative to head
                s = stretch(target, b.wiggle.position, b.wiggle.stretch)
                if b.wiggle.chain:
                    fac = get_fac(b.wiggle.mass, b.wiggle.mass_head) if i else b.wiggle.stretch_head
                    b.wiggle.position_head -= s*fac
                    b.wiggle.position += s*(1-fac)
                else:
                    b.wiggle.position += s
            else: b.wiggle.position = target
        else: #tail stretch relative to parent or none
            target = mat.translation + (b.wiggle.position - mat.translation).normalized()*length_world(b)
            s = stretch(target, b.wiggle.position, b.wiggle.stretch)
            if p and b.wiggle.chain and p.wiggle.tail: #ASSUMES P IS DIRECT PARENT?
                fac = get_fac(b.wiggle.mass, p.wiggle.mass)
                if get_pin(b): fac = 1 - b.wiggle.stretch
                if i == 0: fac = p.wiggle.stretch
                if (p == b.parent and b.bone.use_connect): #optimization with direct parent tail
                    p.wiggle.position -= s*fac
                else:
                    headpos = b.wiggle.matrix.translation
                    v1 = headpos - p.wiggle.matrix.translation
                    headpos -= s*fac
                    v2 = headpos - p.wiggle.matrix.translation
                    sc = v2.length/v1.length
                    q = v1.rotation_difference(v2)
                    v3 = q @ (p.wiggle.position - p.wiggle.matrix.translation)
                    p.wiggle.position = p.wiggle.matrix.translation + v3*sc
                b.wiggle.position += s*(1-fac)
                update_p = True
            else:
                b.wiggle.position += s

        if update_p:
            collide(p,dg) #would only be tail changing
            update_matrix(p)
        if b.wiggle.tail:
            pin(b)
            if bpy.context.scene.wiggle.full_bone_collision.enable_fullbone_collision:
                collide_full_bone(b, dg)
            else:
                collide(b, dg)
        if b.wiggle.head:
            if bpy.context.scene.wiggle.full_bone_collision.enable_fullbone_collision:
                collide_full_bone(b, dg)
            else:
                collide(b, dg, True)
    update_matrix(b)

@persistent
def wiggle_pre(scene):
    if (scene.wiggle.lastframe == scene.frame_current) and not scene.wiggle.reset: return
    if scene.wiggle.is_rendering: return
    if not scene.wiggle.enable:
        reset_scene()
        return

    for wo in scene.wiggle.list:
        if wo.name not in scene.objects:
            build_list()
            return
        ob = scene.objects[wo.name]
        if ob.wiggle.mute or ob.wiggle.freeze:
            reset_ob(ob)
            continue
        for wb in wo.list:
            if wb.name not in ob.pose.bones:
                build_list()
                return
            b = ob.pose.bones[wb.name]
            if b.wiggle.mute or not (b.wiggle.head or b.wiggle.tail):
                reset_bone(b)
                continue
            if not b.wiggle.collision_col:
                if b.wiggle.collider_collection:
                    # Store the name of the collection
                    collider_col = bpy.data.collections.get(b.wiggle.collider_collection.name)
                    if collider_col:
                        b.wiggle.collision_col_name = collider_col.name  # Store name instead of reference

                elif b.wiggle.collider_collection_head:
                    # Store the name of the head collection
                    collider_col_head = bpy.data.collections.get(b.wiggle.collider_collection_head.name)
                    if collider_col_head:
                        b.wiggle.collision_col_name = collider_col_head.name  # Store name

                elif b.wiggle.collider:
                    # Store the name of the object
                    collider_obj = bpy.data.objects.get(b.wiggle.collider.name)
                    if collider_obj:
                        b.wiggle.collision_obj_name = collider_obj.name  # Store name

                elif b.wiggle.collider_head:
                    # Store the name of the head object
                    collider_obj_head = bpy.data.objects.get(b.wiggle.collider_head.name)
                    if collider_obj_head:
                        b.wiggle.collision_obj_name = collider_obj_head.name  # Store name
    
            b.location = Vector((0,0,0))
            b.rotation_quaternion = Quaternion((1,0,0,0))
            b.rotation_euler = Vector((0,0,0))
            b.scale = Vector((1,1,1))
    bpy.context.view_layer.update()

@persistent                
def wiggle_post(scene,dg):
    if (scene.wiggle.lastframe == scene.frame_current) and not scene.wiggle.reset: return
    if scene.wiggle.reset: return
    if not scene.wiggle.enable: return
    if scene.wiggle.is_rendering: return

    lastframe = scene.wiggle.lastframe
    if (scene.frame_current == scene.frame_start) and (scene.wiggle.loop == False) and (scene.wiggle.is_preroll == False):
        bpy.ops.wiggle.reset()
        return
    if scene.frame_current >= lastframe:
        frames_elapsed = scene.frame_current - lastframe
    else:
        e1 = (scene.frame_end - lastframe) + (scene.frame_current - scene.frame_start) + 1
        e2 = lastframe - scene.frame_current
        frames_elapsed = min(e1,e2)
    if frames_elapsed > 4: frames_elapsed = 1 #handle large jumps?
    if scene.wiggle.is_preroll: frames_elapsed = 1
    scene.wiggle.dt = 1/scene.render.fps * frames_elapsed
    scene.wiggle.lastframe = scene.frame_current

    for wo in scene.wiggle.list:
        ob = scene.objects[wo.name]
        if ob.wiggle.mute or ob.wiggle.freeze: continue
        bones = []
        for wb in wo.list:
            b = ob.pose.bones[wb.name]
            if b.wiggle.mute or not (b.wiggle.head or b.wiggle.tail):
                continue
            bones.append(ob.pose.bones[wb.name])
        for b in bones:
            b.wiggle.collision_normal = b.wiggle.collision_normal_head = Vector((0,0,0))
            move(b,dg)
        for i in range(scene.wiggle.iterations):
            for b in bones:
                constrain(b, scene.wiggle.iterations-1-i,dg)
        for b in bones:
            update_matrix(b,True) #final update handling constraints?
        if frames_elapsed:
            for b in bones:
                vb = Vector((0,0,0))
                if b.wiggle.collision_normal.length:
                    vb = b.wiggle.velocity.reflect(b.wiggle.collision_normal).project(b.wiggle.collision_normal)*b.wiggle.bounce
                b.wiggle.velocity = (b.wiggle.position - b.wiggle.position_last)/max(frames_elapsed,1) + vb
                vb = Vector((0,0,0)) 
                if b.wiggle.collision_normal_head.length:
                    vb = b.wiggle.velocity_head.reflect(b.wiggle.collision_normal_head).project(b.wiggle.collision_normal_head)*b.wiggle.bounce_head
                b.wiggle.velocity_head = (b.wiggle.position_head - b.wiggle.position_last_head)/max(frames_elapsed,1) + vb
                b.wiggle.position_last = b.wiggle.position
                b.wiggle.position_last_head = b.wiggle.position_head
                
@persistent        
def wiggle_render_pre(scene):
    scene.wiggle.is_rendering = True
    
@persistent
def wiggle_render_post(scene):
    scene.wiggle.is_rendering = False
    
@persistent
def wiggle_render_cancel(scene):
    scene.wiggle.is_rendering = False
    
@persistent
def wiggle_load(scene):
    build_list()
    s = bpy.context.scene
    s.wiggle.is_rendering = False


def register():
    bpy.app.handlers.frame_change_pre.append(wiggle_pre)
    bpy.app.handlers.frame_change_post.append(wiggle_post)
    bpy.app.handlers.render_pre.append(wiggle_render_pre)
    bpy.app.handlers.render_post.append(wiggle_render_post)
    bpy.app.handlers.render_cancel.append(wiggle_render_cancel)
    bpy.app.handlers.load_post.append(wiggle_load)

def unregister():
    bpy.app.handlers.frame_change_pre.remove(wiggle_pre)
    bpy.app.handlers.frame_change_post.remove(wiggle_post)
    bpy.app.handlers.render_pre.remove(wiggle_render_pre)
    bpy.app.handlers.render_post.remove(wiggle_render_post)
    bpy.app.handlers.render_cancel.remove(wiggle_render_cancel)
    bpy.app.handlers.load_post.remove(wiggle_load)