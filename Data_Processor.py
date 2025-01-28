from Data_Collector import data, artist_list, album_list, last_played, num_songs
from File_Handlers import File_Handlers
from Data_Collector import collect_data
from datetime import datetime

#dictionary to hold ratio of artist listens to total listens
artist_ratio = {}

#top 5 chart (basically wrapped)

#calculates the ratios for each artist (only if that artist has more than 1 listen)
def calculate_artist_ratios():
    for item in artist_list:
        if artist_list[item] == 1:
            continue
        ratio = artist_list[item]/(float(num_songs[0]))
        artist_ratio[item] = ratio

    print(artist_ratio)

if __name__ == "__main__":
    date = datetime.now().date()
    print(date)
    # File_Handlers.read_from_file(data, album_list, artist_list, last_played, num_songs)
    # calculate_artist_ratios()
    #collect_data()
    #print(num_songs)