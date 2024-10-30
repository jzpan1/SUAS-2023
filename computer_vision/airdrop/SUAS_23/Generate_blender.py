import random
import osx

global file_path = ".data/full_drop_zone/"
global dropzone_dims = (109.728, 21.336) # 360 x 70 ft, in meters
global data_output_path = file_path + "metadata/"
global image_output_path = file_path + "images/"

for object in bpy.data.collections['Objects'].all_objects:
    overlapping = True
    random.random()
    while overlapping:
        x = random.random() * ((dropzone_dims[0] - 4) + 2)
        y = random.random() * ((dropzone_dims[1] - 4) + 2)
        if not len(placed_positions) == 0:
            for (prevx, prevy, prevobj) in placed_positions:
                if((abs(prevx - x) > 500) or (abs(prevy - y) > 7)): # 7 meters for determining overlapping drop zones
                    overlapping = False
                else:
                    overlapping = True
                    break
        else:
            overlapping = False
        if(overlapping == False):
            placed_positions.append((x, y, object.name))
            background.paste(paper, (x,y))
    

insertionSort(placed_positions)
metadata = open(data_output_path + name + ".csv", "w+")
    metadata.write(placed_positions[i][2] + " " +str(placed_positions[i][0]) + ' ' + str(placed_positions[i][1]) + "\n")
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