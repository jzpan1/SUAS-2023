import random
import os
import bpy

images_to_generate = 3

file_path = "/Users/jzpan/Coding/python/SUAS-2023/computer_vision/airdrop/SUAS_23/"
dropzone_dims = (152.4, 24.384) # 500 x 80 ft, in meters
data_output_path = file_path + "metadata/"
image_output_path = file_path + "images/"
filename = "drop_zone"
suffix = ""



def randomPosition():
    x = random.random() * ((dropzone_dims[0] - 4) + 2)
    y = random.random() * ((dropzone_dims[1] - 4) + 2)
    x -= dropzone_dims[0] / 2
    y -= dropzone_dims[1] / 2
    return x, y

def randomize_light():
    x, y = randomPosition()
    light = bpy.data.lights["Light"]
    light.angle = random.random()*3.14159
    light.energy = 3 + random.random()*10
    
def place():
    placed_positions = []
    randomize_light()
    global suffix
    for object in bpy.data.collections['Objects'].all_objects:
        if object.name in [obj[2] for obj in placed_positions]:
            continue
        overlapping = True
        random.random()
        while overlapping:
            x, y = randomPosition()
            if not len(placed_positions) == 0:
                for (prevx, prevy, prevobj) in placed_positions:
                    if((abs(prevx - x) > 7.62) or (abs(prevy - y) > 7.62)): # 7.62 meters = 25 ft for determining overlapping drop zones
                        overlapping = False
                    else:
                        overlapping = True
                        break
            else:
                overlapping = False
            if(overlapping == False):
                placed_positions.append((x, y, object.name))
                object.location[0] = x
                object.location[1] = y

    insertionSort(placed_positions)
    metadata = open(data_output_path + filename + suffix + ".csv", "w+")
    metadata.write("name,world_x,world_y\n")
    for i in range(len(bpy.data.collections['Objects'].all_objects)):
        metadata.write(placed_positions[i][2] + "," +str(placed_positions[i][0]) + ',' + str(placed_positions[i][1]) + "\n")

def pointGreater(point1, point2):
    if(point1[1] == point2[1]):
        return point1[0] > point2[0]
    return point1[1] > point2[1]

def insertionSort(arr):
    n = len(arr)
    if n <= 1: return
    for i in range(1, n):
        j = i-1
        key = arr[i]
        while j >= 0 and not pointGreater(key, arr[j]):
            arr[j+1] = arr[j]
            j -= 1
        arr[j+1] = key
        
def check_file_paths():
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    if not os.path.exists(image_output_path):
        os.makedirs(image_output_path)
    if not os.path.exists(data_output_path):
        os.makedirs(data_output_path)

def render(num):
    global suffix
    suffix = str(num)
    place()
    bpy.context.scene.render.filepath = os.path.join(image_output_path, (filename + suffix + ".png"))
    bpy.ops.render.render(write_still = True)
 
check_file_paths()
for i in range(images_to_generate):
    render(i)