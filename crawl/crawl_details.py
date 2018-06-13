import codecs
import os
import re
import threading

import pandas as pd
import xlwt
from bs4 import BeautifulSoup
from pandas import ExcelWriter
from selenium import webdriver

from crawl import param

# '国产药品-list-1-2500.txt',
# '国产药品-list-2501-5000.txt',
# '国产药品-list-5001-6000.txt',
# '国产药品-list-7001-8000.txt',
# '国产药品-list-8001-9000.txt',
# '国产药品-list-6001-7000.txt'
list_arr = [
    '国产药品-list-9001-10000.txt',
    '国产药品-list-10001-11000.txt',
    '国产药品-list-11001-11070.txt'
]

"""
批准文号,国药准字Z20020147,
产品名称,龟龙中风丸,
英文名称,,
商品名,,
剂型,丸剂(水丸),
规格,每30丸重5g,
生产单位,沈阳红药集团股份有限公司,
生产地址,沈阳市大东区北大营西路2号,
产品类别,中药,
批准日期,2015-07-30,
原批准文号,,
药品本位码,86901343001160
"""


def cut(result):
    arr = re.compile(',').split(result)
    arr = arr[1:-9]
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
                return crawl_detail(browser, url, times)
            else:
                return detail_str


def combine_excel():
    """
    combine all the excel
    :return:
    """
    files = os.listdir(os.getcwd())
    files_xls = [f for f in files if f[-3:] == 'xls']
    with ExcelWriter(param.name + '.xls') as writer:
        for i, f in enumerate(files_xls):
            print(i)
            print(f)
            df = pd.DataFrame()
            data = pd.read_excel(f, sheet_name='Sheet1')
            df = df.append(data)
            df.to_excel(writer, sheet_name='Sheet' + (i + 1).__str__(), merge_cells=False, index=False)
    writer.close()


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
    for txt in list_arr:
        file_path = param.FILE_PREFIX + 'list\\' + txt
        print(file_path, txt.split('.')[0])
        thread = CrawlDetailThread(file_path, txt.split('.')[0])
        thread.start()
