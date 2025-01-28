#Version 1: Prints the images of the top 5 songs with the name and the number of times played
import sys
import os
sys.path.append(os.path.abspath(".."))

from Data_Collector import data, collect_data
from File_Handlers import File_Handlers
import matplotlib.pyplot as plt
#import matplotlib.image as mpimg
from PIL import Image
from io import BytesIO
import requests
import json

songs = []
images = []
numbers = []

#does a print like the spotify wrapped thing p cool
def graph():
    counter = 1
    fig, axs = plt.subplots(6, 1, figsize=(10,7))
    fig.patch.set_facecolor('#D50032')

    #background = mpimg.imread('background.jpg')
    #axs[0].imshow(background, aspect='auto')
    axs[0].text(0.22, 0.5, 'Song Name', transform=axs[0].transAxes, fontsize=20, color='#B5A600', va='center', ha='left', wrap=True)
    axs[0].text(0.75, 0.5, 'Times Played', transform=axs[0].transAxes, fontsize=20, color='#B5A600', va='center', ha='left', wrap=True)
    axs[0].axis('off')
    for image in images:
        axis = axs[counter]

        img_ax = fig.add_axes([0.05, 0.75 - (counter) * 0.146, 0.125, 0.123])
        img_ax.imshow(image, aspect='auto')
        img_ax.text(2, 0.5, songs[counter-1], transform=img_ax.transAxes, fontsize=20, color='#B5A600', va='center', ha='left', wrap=True)
        img_ax.text(6, 0.5, numbers[counter-1], transform=img_ax.transAxes, fontsize=20, color='#B5A600', va='center', ha='left', wrap=True)

        img_ax.axis('off')
        axis.axis('off')
        counter += 1

    plt.title('TOP SONGS')
    plt.show()

#gets the actual image objects
def get_images():
    counter = 0
    for url in images:
        response = requests.get(url)
        images[counter] = Image.open(BytesIO(response.content))
        counter += 1

#gets the 5 songs that will show and their album covers
def get_graph_data():
    global songs
    global images
    counter = 1
    for item in data:
        params = item.split('-')
       # print(data[item])
        songs.append(params[0].strip())
        value_params = data[item][0].split('{')
        value_params[1] = "{" + value_params[1]
        value_params[1] = value_params[1].replace("'", '"')
        #print(value_params[1])
        images.append(json.loads(value_params[1])['url'])
        numbers.append(str(data[item][1]))
        counter += 1
        if counter > 5:
            break

if __name__ == '__main__':
    #collect_data()
    File_Handlers.read_from_file(data, {}, {}, {}, [0], "")
    get_graph_data()
    get_images()
    graph()

    
