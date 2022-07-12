import os
import pandas as pd
from datetime import datetime
from pathlib import Path
pd.options.mode.chained_assignment = None

def write_csv(**kwargs):
    dict = [kwargs]
    mis_dataframe = pd.DataFrame(dict)
    print(mis_dataframe)
    # get home folder
    home_folder = os.path.expanduser('~')
    csv_path = Path(home_folder + '/Documents/mis/' +'mis.csv')
    print(csv_path)
    if not os.path.isfile(csv_path):
        mis_dataframe.to_csv(csv_path,mode="w", header=True,index=False)
    else:
        mis_dataframe.to_csv(csv_path,mode="a", header=False,index=False)
