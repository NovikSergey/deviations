from typing import Type
import pandas as pd


class Stat_plotter:
    
    def drow_plots(j_file):
        try:
            df = pd.read_json(j_file)
        except ValueError:
            print("please give the path to json file")
            return
        
        print('read json file')
        Stat_plotter.DataFrame = df

if __name__ == '__main__':
    analyzator = Stat_plotter
    analyzator.drow_plots('./deviation.json')
    