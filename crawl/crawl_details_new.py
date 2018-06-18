import os
import threading

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver

from crawl.util import FILE_DIR_LIST, folder, get_title, get_file_content, arrange


def crawl_detail(browser, url, times=0):
    detail_arr = []
    try:
        browser.get(url)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        div = soup.find('div', attrs={'class': 'listmain'})
        if div:
            table = div.find_all('table')[0]
            all_td = table.find_all('td')
            for td in all_td:
                detail_arr.append(td.getText().strip())
                # detail_str += td.getText().strip() + ','
            # detail_str = cut(detail_str)
    # except Exception as ex:
    #     print("crawl_detail : Exception has been thrown. " + str(ex))
    finally:
        if detail_arr:
            return detail_arr
        else:
            if times < 3:
                times += 1
                crawl_detail(browser, url, times)
            else:
                return detail_arr


def output_excel(file, name):
    data = pd.DataFrame()
    txt_content = get_file_content(file)
    b = webdriver.Chrome()
    # read file ,get url,get No.
    for line in txt_content:
        if line.strip():
            try:
                drug_url = line.split(',')[-1]
                drug_id = line.split('=')[-1]
                # crawl detail
                detail = crawl_detail(b, drug_url)
                if detail:
                    detail.insert(1, str(drug_id).strip())
                    detail_arr = arrange(detail[1:-8], drug_url)
                    title = get_title(detail[1:-8])
                    data = data.append(pd.DataFrame(columns=title, data=[detail_arr]),
                                       ignore_index=True, sort=False)
                else:
                    data = data.append(pd.DataFrame(data=[line + ',None']), ignore_index=True, sort=False)
            finally:
                data.to_excel(name + '.xlsx')
    # b.close()


class CrawlDetailThread(threading.Thread):
    def __init__(self, file, name):
        threading.Thread.__init__(self)
        self.file = file
        self.name = name

    def run(self):
        print('starting ' + self.name)
        output_excel(self.file, self.name)


if __name__ == '__main__':
    for directory in FILE_DIR_LIST:
        list_arr = [f for f in os.listdir(os.getcwd() + directory + folder[0]) if f[-3:] == 'txt']
        for txt in list_arr:
            file_path = os.getcwd() + directory + folder[0] + txt
            print(file_path, txt.split('.')[0])
            thread = CrawlDetailThread(file_path, txt.split('.')[0])
            thread.start()
