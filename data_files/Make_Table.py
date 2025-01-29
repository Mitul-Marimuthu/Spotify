#Turns text files into csv files via pandas
import pandas as pd

def freq_file():
    df = pd.read_csv('freq_copy.txt', delimiter='+')

    df.to_csv('frequenxy_list.csv', index=False, header=True)

def print_table():
    df = pd.read_csv('frequency_list.csv')
    print(df)

if __name__ == "__main__":
   print_table()