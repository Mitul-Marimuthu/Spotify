import sys
import os
sys.path.append(os.path.abspath(".."))

from File_Handlers import File_Handlers
from Data_Collector import data, artist_list, album_list, last_played

#changes format of the strings
def change_itemizer():
    File_Handlers.read_from_file(data, {}, {}, {}, [0], '')
    #print(data)
    new_names = {}
    for item in data:
        new = item.replace("+", ":")
        new = new.replace("-", "+")
        new_names[item] = new

        index = data[item][0].find(",")
        data[item][0] = data[item][0][0:index] + ' + ' + data[item][0][(index+1):]

    for old, new in new_names.items():
        if old in data:
            data[new] = data.pop(old)

    File_Handlers.write_to_file(data, album_list, artist_list, last_played)

if __name__ == "__main__":
    change_itemizer()