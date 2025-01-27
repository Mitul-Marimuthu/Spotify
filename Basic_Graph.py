#verion 1: bar graph of the artist ratios

import matplotlib.pyplot as plt # type: ignore
from Data_Collector import collect_data, artist_list, data, album_list, last_played, num_songs
from File_Handlers import File_Handlers
import math as ma

#shows a graph in pages with 10 artists per page for ALL artists
def pagination_artist_graph():
    #print(artist_list)
    artists = [item for item in artist_list]
    values = [artist_list[item] for item in artist_list]
    # artists.reverse()
    # values.reverse()
    colors = ['red', 'blue']
    #print(artists)
    artists_per_page = 10.0
    num_pages = min(10, int(ma.ceil(len(artists)/artists_per_page)))
    max_value = max(values)
    #height = 
    # Create a subplot with a specific layout (2 rows, 1 column in this case)
    fig, axs = plt.subplots(int(num_pages/2), 2, figsize=(10, 7))  # 2 rows, 1 column (adjust figsize as needed)
    counter = 1
    for page in range(int(num_pages/2)):
        start_index = page*(int(artists_per_page))
        end_index = start_index + (int(artists_per_page))
        page_artists = artists[start_index:end_index]
        page_values = values[start_index:end_index]
        page_artists.reverse()
        page_values.reverse()

        axis = axs[page] if num_pages > 1 else axs

        axis[0].barh(page_artists, page_values, color=colors)

        axis[0].set_xlabel('Number of Songs Listened To')
        axis[0].set_ylabel('Artists')
        axis[0].set_title(f'Bar Graph (Page {counter})')
        axis[0].tick_params(axis='y', labelsize=5)
        axis[0].set_xlim(0, max_value)

        #page += 1
        start_index2 = (page)*(int(artists_per_page))
        end_index2 = start_index + (int(artists_per_page))
        page_artists = artists[start_index2:end_index2]
        page_values = values[start_index2:end_index2]
        page_artists.reverse()
        page_values.reverse()
        counter += 1
        #ax = axs[page][1] if num_pages > 1 else axs[0][0]
        axis[1].barh(page_artists, page_values, color=colors)
        axis[1].set_xlabel('Number of Songs Listened To')
        axis[1].set_ylabel('Artists')
        axis[1].set_title(f'Bar Graph (Page {counter})')
        axis[1].tick_params(axis='y', labelsize=5)
        axis[1].set_xlim(0, max_value)
        counter += 1

        #new figure for each page
        # plt.figure(figsize=(8,5))

        # plt.barh(page_artists, page_values, color=colors)

        # plt.ylabel('Artist')
        # plt.xlabel('Number of Songs Listened To')
        # plt.title(f'Top Artists (Page {page+1})')

        # plt.show()

    plt.tight_layout()
    plt.show()

#shows a graph with as many top artists as necessary
def simple_artist_graph():
    #collect_data()
    #File_Handlers.read_from_file(data, album_list, artist_list, last_played, num_songs)
    categories = [item for item in artist_list]
    values = [artist_list[item] for item in artist_list]
    categories.reverse()
    values.reverse()

    colors = ['red', '#FFD700']
    plt.barh(categories, values, color=colors)

    # for x, y in enumerate(values):
    #     plt.text(y/2, x, f"{categories[x]} is your #{x} artist!", ha='center', va='center', color='black')
    #change font size
    plt.yticks(fontsize=5)

    plt.ylabel('Artist')
    plt.xlabel('Number of Songs Listened To')
    plt.title('Top Artists')

    plt.show()

if __name__ == "__main__":
    collect_data()
    pagination_artist_graph()