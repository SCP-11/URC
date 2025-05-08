import unreal
import random
import math
import time

# Get the editor world
subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
editor_world = subsystem.get_editor_world()

# Get actors
all_actors = unreal.GameplayStatics.get_all_actors_of_class(editor_world, unreal.StaticMeshActor)
for actor in all_actors:
    if "Target" in actor.tags:
        print("Target actor found: ", actor.get_actor_label())
        target_actor = actor
        break

if not target_actor:
    print("Target actor not found.")
    exit()

# static_mesh = target_actor.get_editor_property("static_mesh_component")
# print("Target actor found: ", target_actor.get_actor_label())
# velocity = target_actor.call_method("GetVelocity_BP")
camera_actor = None
actors = unreal.GameplayStatics.get_all_actors_of_class(editor_world, unreal.Actor)
for a in actors:
    if "Cam" in a.tags:
        print("Camera actor found: ", a.get_actor_label())
        camera_actor = a
        # break
if camera_actor is None:
    print("Camera actor not found.")
    exit()

light_source = unreal.GameplayStatics.get_all_actors_of_class(editor_world, unreal.DirectionalLight)[0]
original_light_color = light_source.get_editor_property("directional_light_component").get_editor_property("light_color")
original_light_color = unreal.Color(
    r = original_light_color.r,
    g = original_light_color.g,
    b = original_light_color.b,
    a = 1.0
)

sky_sphere = unreal.GameplayStatics.get_actor_of_class(editor_world, unreal.SkyLight)
fog = unreal.GameplayStatics.get_actor_of_class(editor_world, unreal.ExponentialHeightFog)
# Randomize lighting
def randomize_lighting():
    global original_light_color

    try:
        light_compponent = light_source.get_editor_property("directional_light_component")
        intensity = random.uniform(1.0, 8.0)
        new_color = unreal.Color()
        multply = random.uniform(0.2, 1.0)
        new_color = unreal.Color(
            r = original_light_color.r * multply,
            g = original_light_color.g * multply,
            b = original_light_color.b * multply,
            a = 1.0
        )
        # new_color.r = original_light_color.r.clone() * multply
        # new_color.g = original_light_color.g.clone() * multply
        # new_color.b = original_light_color.b.clone() * multply
        light_compponent.set_editor_property("intensity", intensity)
        light_compponent.set_editor_property("light_color", new_color)
            # light.set_editor_property("intensity", intensity)

        print("Lighting randomized: ", intensity, new_color)
        print("Original color: ", original_light_color)
    except Exception as e:
        print(e)
        exit_clean("Synthetic data generation failed.")
    
# Randomize fog
def randomize_fog():
    if fog:
        fog_component = fog.get_editor_property("component")
        fog_component.set_editor_property("fog_density", random.uniform(0.01, 0.1))
        # fog.set_editor_property("fog_density", random.uniform(0.01, 0.1))

# Move camera while ensuring target visibility
def move_camera():
    global target_pos, camera_actor, target_actor
    if camera_actor and target_actor:
        radius = random.uniform(1000, 2000)
        angle = random.uniform(0, 360)
        height = random.uniform(400, 600)

        x = target_actor.get_actor_location().x + radius * math.cos(math.radians(angle))
        y = target_actor.get_actor_location().y + radius * math.sin(math.radians(angle))
        z = target_actor.get_actor_location().z + height

        target_pos = unreal.Vector(x, y, z)  
        camera_actor.call_method("SetPos", args=(target_pos,))
        # camera_actor.set_actor_location(target_pos, sweep=False, teleport=True)
        print("Camera moved to: ", target_pos)
        # while camera_actor.get_actor_location() != unreal.Vector(x, y, z) or tick_count < 2:
            # time.sleep(0.1)
        # target_mesh = target_actor.call_method("GetMesh_BP")
        # camera_actor.set_editor_property("lookat_tracking_settings", unreal.CameraLookatTrackingSettings(
        #     actor_to_track = target_mesh
        # ))
        # camera_actor.CameraLookatTrackingSettings()

# def __posttick__(self):
#     global tick_count, target_pos, data_count, data_max, target_actor, wait_time
    
#     try:
#         tick_count += 1
#         # print("Tick count: ", tick_count)
#         wait_time += 1
#         # velocity = target_actor.call_method("GetVelocity_BP")
#         if camera_actor.get_actor_location() == target_pos and tick_count > 100:
#         # and velocity.x == 0 and velocity.y == 0 and velocity.z == 0
#             data_count += 1
#             tick_count = 0
#             # target_pos

#             capture_image("image_" + str(data_count))
#             randomize_lighting()
#             randomize_fog()
#             move_camera()
#             wait_time = 0
#         # print("Data count: ", data_count)
#         if data_count >= data_max:
#             exit_clean("Synthetic data generation complete.")

#         if tick_count > 200:        
#             move_camera()
            
#         if tick_count > 600:
#             exit_clean("Stuck.. Exiting.")
#     except Exception as e:
#         print(e)
#         exit_clean("Synthetic data generation failed.")

def __posttick__(self):
    global tick_count, target_pos, data_count, data_max, target_actor, wait_time, camera_actor
    # print("Tick")
    try:
        tick_count += 1

        ## GET THE CAMERA ACTOR
        # camera_actor = None
        actors = unreal.GameplayStatics.get_all_actors_of_class(editor_world, unreal.Actor)
        for a in actors:
            if "Cam" in a.tags:
                print("Camera actor found: ", a.get_actor_label())
                camera_actor = a
                # break
        if camera_actor is None:
            print("Camera actor not found.")
            exit()

        ## CHECK READY FOR IMAGE CAPTURE
        if(camera_actor is None):
            print("Camera actor is None.")
            exit_clean("Synthetic data generation failed.")

        ready = camera_actor.call_method("GetReady")
        ready = camera_actor.get_editor_property("ReadyForCapture")

        print("Tick", ready)
        if(ready):
            capture_image("image_" + str(data_count))
            tick_count = 0
            # while camera_actor.call_method("GetReady"):
            #     time.sleep(0.1)
            #     print("Waiting for camera to be ready.")
            #     camera_actor.call_method("SetReady", False)
        if tick_count > 2000:
            exit_clean("Stuck.. Exiting.")
    except Exception as e:
        # print(e)
        exit_clean("Synthetic data generation failed. Error: " + str(e))

def exit_clean(msg):
    light_source.get_editor_property("directional_light_component").set_editor_property("light_color", original_light_color)
    print(msg)
    unreal.unregister_slate_post_tick_callback(slate_post_tick_handle)
    exit()
# Capture images 
def capture_image(name):
    # unreal.EditorLevelLibrary.editor_tick(0.1)
    screenshot_path = "/Game/Screenshots/" + name + ".png"
    unreal.AutomationLibrary.take_high_res_screenshot(1920, 1080, screenshot_path)

# return
data_max = 4
data_count = 0
tick_count = 0
wait_time = 0
target_pos = camera_actor.get_actor_location()

# unreal.LevelEditorSubsystem().editor_play_simulate()
unreal.LevelEditorSubsystem().editor_request_begin_play()
slate_post_tick_handle = unreal.register_slate_post_tick_callback(__posttick__)

