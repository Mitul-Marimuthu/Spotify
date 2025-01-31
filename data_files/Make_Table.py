#Turns text files into csv files via pandas
#saves to sql server
import pandas as pd
import sqlite3

def freq_file():
    df = pd.read_csv('frequency_list.txt', delimiter='+')

    df.to_csv('frequency_list.csv', index=False, header=True)

def artist_file():
    df = pd.read_csv('artist_list.txt', delimiter='+')
    df.to_csv('artist_list.csv', index=False, header=True)

def album_file():
    df = pd.read_csv('album_list.txt', delimiter='+')
    df.to_csv('album_list.csv', index=False, header=True)

def time_file():
    df = pd.read_csv('time_list.txt', delimiter='+')
    df.to_csv('time_list.csv', index=False, header=True)

def print_table():
    df = pd.read_csv('frequency_list.csv')
    print(df)

def last_played():
    df = pd.read_csv('time_list.txt', delimiter='+')
    conn = sqlite3.connect("spotify.db")
    df.to_sql("last", conn, index=True)
    conn.close()

def save_to_server():
    main_data = pd.read_csv('frequency_list.csv')
    artists_data = pd.read_csv('artist_list.csv')
    album_data = pd.read_csv('album_list.csv')
    time_data = pd.read_csv('time_list.csv')

    conn = sqlite3.connect("spotify.db")
    main_data.to_sql("main", conn, if_exists="replace", index=False)
    artists_data.to_sql("artists", conn, if_exists="replace", index=False)
    album_data.to_sql("albums", conn, if_exists="replace", index=False)
    time_data.to_sql("times", conn, if_exists="replace", index=True)

    conn.close()

if __name__ == "__main__":
    last_played()
   #print_table()