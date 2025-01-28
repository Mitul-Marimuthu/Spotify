# has template methods with parameters that allow for streamlined fileIO
import ast
from datetime import datetime
class File_Handlers:
    # writes the content of the list into the file in a way that makes it easy to extract
    #TODO: include the 'played_at list after'
    @staticmethod
    def write_to_file(data, album_list, artist_list, last_played):
        # global data
        # global artist_list
        # global album_list
        # global last_played
        with open('/Users/mitul/Desktop/spotify/data_files/frequency_list.txt', 'w') as file:
            for item in data:
                #adds a + sign to discern between the three components of the input
                # 1. "(song name) - (artist)"
                # 2. "(album name), {image information}"
                # 3. frequency counter
                file.write(f"{item} + {data[item][0]} + {data[item][1]}")
                file.write("\n")
        
        # writes to the file that stores the times that all the songs were played
        with open('/Users/mitul/Desktop/spotify/data_files/time_list.txt', 'w') as file:
            if len(last_played) > 0:
                for item in last_played:
                    file.write(f"first + {item} + {last_played[item]}\n\n")
            for item in data:
                file.write(f"{item} + {data[item][2]}\n")

        # writes to the file that stores the number of albums listened to and the number of songs
        # listened to from the album
        #print(album_list)
        with open('/Users/mitul/Desktop/spotify/data_files/album_list.txt', 'w') as file:
            for item in album_list:
                file.write(f"{item} + {album_list[item][0]} + {album_list[item][1]}\n")

        #writes to the file that stores the number of songs listened to by an artist
        #print('a')
        #print(artist_list)
        with open('/Users/mitul/Desktop/spotify/data_files/artist_list.txt', 'w') as file:
            for item in artist_list:
                file.write(f"{item} + {artist_list[item]}\n") 

    @staticmethod
    def read_from_file(data, album_list, artist_list, last_played, num_songs, start_date):
        # global data
        # global album_list
        # global artist_list
        # global last_played
        #print(os.getcwd())
        #file with song information and times played
        with open('/Users/mitul/Desktop/spotify/data_files/frequency_list.txt', 'r') as file:
            line = file.readline()
            while line:
                params = line.split('+')
                data[params[0].strip()] = [params[1].strip(), int(params[2].strip()), []]
                num_songs[0] += int(params[2].strip())
                line = file.readline()

        if len(data) == 0:
            start_date = datetime.now().date()
        #print (num_songs)
        #file with the times of when the song was played
        with open('/Users/mitul/Desktop/spotify/data_files/time_list.txt', 'r') as file:
            line = file.readline()
            while line:
                if '+' not in line: 
                    line = file.readline()
                    continue
                params = line.split('+')
                if params[0].strip() == 'first':
                    #print('yay')
                    #last_played = {}
                    last_played[params[1].strip()] = params[2].strip()
                else:
                    data[params[0].strip()][2] = ast.literal_eval(params[1].strip())
                # print(data[params[0].strip()][2])
                line = file.readline()

        #file with the artists and total number of songs (iterations included) listened to by the artist
        with open('/Users/mitul/Desktop/spotify/data_files/artist_list.txt', 'r') as file:
            line = file.readline()
            while line:
                params = line.split('+')
                artist_list[params[0].strip()] = int(params[1].strip())
                line = file.readline()

        #file with the albums and how many songs (iterations included) listened to in the album
        with open('/Users/mitul/Desktop/spotify/data_files/album_list.txt', 'r') as file:
            line = file.readline()
            while line:
                params = line.split('+')
                album_list[params[0].strip()] = [params[1].strip(), int(params[2].strip())]
                line = file.readline() 

        #print(last_played)
