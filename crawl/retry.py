import codecs
import os
import threading

import pandas as pd
from selenium import webdriver

from crawl import param
from crawl.crawl_details import crawl_detail
from crawl.crawl_list import get_ids

# iloc[row-2,col]
# target_str = data.iloc[(40 - 2), 0]
# print(target_str.split(','))

"""
'进口化妆品-list-2001-3000.txt',
'进口化妆品-list-3001-4000.txt',
'进口化妆品-list-4001-5000.txt'
"""


def combine_str(array, detail):
    array.remove('None')
    array.insert(3, detail)
    return ','.join(array)


def retry(path):
    data = pd.read_excel(path, sheet_name='Sheet1')
    try:
        browser = webdriver.Chrome()
        for row in range(data.shape[0]):
            s = str(data.iat[row, 0])
            if s.__contains__(',None'):
                print(s)
                arr = s.split(',')
                detail = crawl_detail(browser, arr[-1])
                if detail:
                    new_str = combine_str(arr, detail)
                    print(new_str)
                    data = data.drop([row], axis=0)
                    data = pd.DataFrame(pd.np.insert(data.values, row, [new_str]))
    except Exception as ex:
        print("retry : Exception has been thrown. " + ex.__str__())
    finally:
        data.to_excel(path, index=False)


class RetryThread(threading.Thread):
    def __init__(self, file_path):
        threading.Thread.__init__(self)
        self.file_path = file_path

    def run(self):
        print('starting ' + self.file_path)
        retry(self.file_path)


class CheckThread(threading.Thread):
    def __init__(self, file_path):
        threading.Thread.__init__(self)
        self.file_path = file_path

    def run(self):
        print('starting ' + self.file_path)
        check(self.file_path)


class TxtRetryThread(threading.Thread):
    def __init__(self, file_path):
        threading.Thread.__init__(self)
        self.file_path = file_path

    def run(self):
        print('starting ' + self.file_path)
        txt_retry(self.file_path)


def txt_retry(path):
    content = []
    with codecs.open(os.getcwd() + path, 'r', 'utf-8') as txt:
        for line in txt:
            content.append(line)
    txt.close()
    txt_file = pd.DataFrame(content)
    browser = webdriver.Chrome()
    try:
        # bug：item+在原数组上了……
        for row in range(txt_file.shape[0]):
            s = str(txt_file.iat[row, 0]).strip()
            if s.__contains__('failed'):
                page = s.split(' ')[1]
                print(path + ' , ' + page)
                url_dir = get_ids(browser, param.get_list_url(page))
                if url_dir:
                    count = 0
                    txt_file = txt_file.drop([row], axis=0)
                    for k, v in url_dir.items():
                        new_str = '{name},{urls}'.format(name=k, urls=v + '\n')
                        txt_file = pd.DataFrame(pd.np.insert(txt_file.values, row + count, [new_str]))
                        count += 1
    except Exception as e:
        print('txt_retry() Exception : ' + e.__str__())
    finally:
        pd.np.savetxt(os.getcwd() + path, txt_file.values, fmt='%s', encoding='utf-8', newline='')
        print('txt_retry() ' + path + ' finish.')


def check(path, start=0):
    """
    eg
        check('\\进口化妆品\\list\\进口化妆品-list-2001-3000.txt', 2000)

    :param path:
    :param start:
    :return:
    """
    content = []
    with codecs.open(os.getcwd() + path, 'r', 'utf-8') as txt:
        for line in txt:
            content.append(line)
    txt.close()

    try:
        for index, item in enumerate(content):
            if not item.__contains__('failed'):
                if item.strip().split('.')[0]:
                    number = int(item.strip().split('.')[0]) - (15 * start)
                    if not number == index + 1:
                        print(index.__str__() + ' == ' + item)
            else:
                print(item)
    finally:
        print('check ' + path + ' finish')


list_arr = [
    '进口化妆品-list-2001-3000.txt'
    # '进口化妆品-list-3001-4000.txt',
    # '进口化妆品-list-4001-5000.txt'
]
if __name__ == '__main__':
    # check('\\进口化妆品\\list\\' + '进口化妆品-list-2001-3000.txt', 2000)
    for xls in list_arr:
        f_path = '\\进口化妆品\\list\\' + xls
        print(f_path, xls.split('.')[0])
        thread = TxtRetryThread(f_path)
        thread.start()
