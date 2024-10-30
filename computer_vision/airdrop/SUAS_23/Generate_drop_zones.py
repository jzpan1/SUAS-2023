import os
import sys
import random
import numpy as np
from PIL import Image, ImageDraw


def generateRandFromFolder(folder_dir, image_selections):
    img_names = []
    # add all image names to the img_names container
    for image in os.listdir(folder_dir):
        if(image.endswith(".png")):
            img_names.append(image)

    for i in range (0,4):
        temp = random.randrange(0, len(img_names)-1)
        if (temp not in image_selections):
            image_selections.append(img_names[temp])
        else:
            i = i-1

def place_on_paper(folder_dir, image_selections, papers):
    paper_size = (21,28)
    paper_color = (255, 255, 255)
    

    for i in range (len(image_selections)):
        currImg = Image.open(os.path.join(folder_dir, image_selections[i]))
        # change all pixels that match gray (128, 128, 128) to white
        im = currImg.convert('RGB')
        data = np.array(im)
        mask = np.all(data[:,:,:3] == (128,128,128), axis = -1)
        data[mask] = (255,255,255)
        currImg = Image.fromarray(data)
        currImg.thumbnail([19,19])
        paper = Image.new("RGB", paper_size, paper_color)
        paper.paste(currImg, (1, 4))
        papers.append(paper)

    return papers


def place_on_background(background_size, folder_path, image_selections, papers, image_output_path, data_output_path, name):
    background_color = (128, 128, 128)
    background = Image.new("RGB", background_size, background_color)

    placed_positions = []

    for i in range(len(papers)):
        paper = papers[i]
        image_path = image_selections[i]
        overlapping = True
        while overlapping:
            x = random.randint(100, background.width - paper.width - 100)
            y = random.randint(100, background.height - paper.height - 100)
            if not len(placed_positions) == 0:
                for (prevx, prevy, previmg) in placed_positions:
                    if((abs(prevx - x) > 500) or (abs(prevy - y) > 500)): # 500 pixels for determining overlapping
                        overlapping = False
                    else:
                        overlapping = True
                        break
            else:
                overlapping = False
            if(overlapping == False):
                placed_positions.append((x + 10, y + 14, image_path))
                background.paste(paper, (x,y))

    background.save(image_output_path + name + ".png")
    metadata = open(data_output_path + name + ".txt", "w+")
    

    insertionSort(placed_positions)
    for i in range(0,4):
        metadata.write("1 " + str(placed_positions[i][0]/4000)+ ' ' + str(placed_positions[i][1]/3000) + ' ' + str(21/4000) + " " + str(28/4000) + "\n")

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


def generate_rand_configs(number, background_size, folder_dir, image_output_path, data_output_path, name):
    for i in range(number):
        image_selections = []
        generateRandFromFolder(folder_dir, image_selections)
        papers = []
        place_on_paper(folder_dir, image_selections, papers)
        place_on_background(background_size, folder_dir, image_selections, papers, image_output_path, data_output_path, name+str(i))


def check_file_paths(file_path, image_output_path, data_output_path):
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    if not os.path.exists(image_output_path):
        os.makedirs(image_output_path)
    if not os.path.exists(data_output_path):
        os.makedirs(data_output_path)

if __name__ == "__main__":
    current_file_path = os.path.abspath(__file__)
    folder_dir = os.path.join(os.path.dirname(current_file_path), '.data/training_images')
    background_size = (4000, 3000)

    file_path = ".data/full_drop_zone/"
    data_output_path = file_path + "metadata/"
    image_output_path = file_path + "images/"
    check_file_paths(file_path, image_output_path, data_output_path)
    name = "config_"

    number_of_configs = int(sys.argv[1])
    generate_rand_configs(number_of_configs, background_size, folder_dir, image_output_path, data_output_path, name)