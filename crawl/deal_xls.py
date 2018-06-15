import os
import re

import pandas as pd

from crawl.retry import get_file_pd


def output_form(directory):
    all_xls = pd.DataFrame()
    d_arr = [f for f in os.listdir(os.getcwd() + '\\' + directory + '\\detail\\') if f[-3:] == 'xls']
    d_arr = sorted(d_arr, key=lambda f: int(f.split('-')[2]))
    print(d_arr)
    try:
        for xls in d_arr:
            print(xls)
            data = get_file_pd('\\' + directory + '\\detail\\' + xls)
            all_xls = all_xls.append(data, ignore_index=True)

        # todo edit


    finally:
        all_xls.to_excel(directory + '.xlsx', index=False, sheet_name=directory)


if __name__ == '__main__':
    output_form('国产药品')
