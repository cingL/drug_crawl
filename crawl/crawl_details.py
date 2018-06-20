import codecs
import os
import re
import threading

import xlwt
from bs4 import BeautifulSoup
from selenium import webdriver

from crawl import util
from crawl.util import FILE_DIR_LIST, folder


def cut(result):
    arr = re.compile(',').split(result)
    arr = arr[1:util.field_count]
    # print(''.join(arr))
    return ','.join(arr)


def crawl_detail(browser, url, times=0):
    detail_str = ''
    try:
        browser.get(url)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        div = soup.find('div', attrs={'class': 'listmain'})
        if div:
            table = div.find_all('table')[0]
            all_td = table.find_all('td')
            for td in all_td:
                detail_str += td.getText().strip() + ','
            detail_str = cut(detail_str)
    except Exception as ex:
        print("crawl_detail : Exception has been thrown. " + str(ex))
    finally:
        if detail_str:
            return detail_str
        else:
            if times < 3:
                times += 1
                crawl_detail(browser, url, times)
            else:
                return detail_str


def output_excel(file, name):
    book = xlwt.Workbook()
    sh = book.add_sheet('Sheet1')
    with codecs.open(file, 'r', 'utf-8') as f:
        col = 0
        b = webdriver.Chrome()
        # read file ,get url,get No.
        for line in f:
            if line.strip():
                drug_url = line.split(',')[-1]
                number = int(line.split(',')[0].split('.')[0])
                drug_id = line.split('=')[-1]
                # crawl detail
                detail = crawl_detail(b, drug_url)
                sh.write(col, 0, number.__str__() + ',id,' + drug_id + ',' + detail.__str__() + ',url,' + drug_url)
                print(number.__str__() + ',id,' + drug_id + ',' + detail.__str__() + ',url,' + drug_url)
                col += 1
                book.save(name + '.xls')
        b.close()
    f.close()


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
