import os
import re
import threading
from itertools import zip_longest

import pandas as pd
from selenium import webdriver

from crawl import util
from crawl.crawl_details import crawl_detail
from crawl.crawl_list import get_ids
from crawl.util import get_file_content, get_file_pd, folder, FILE_DIR_LIST


def txt_retry(path):
    """
    replace 'page xx crawl failed' in txt
    :param path:
    :return:
    """
    content = get_file_content(path)

    txt_file = pd.DataFrame(content)
    browser = webdriver.Chrome()
    try:
        for row in reversed(range(txt_file.shape[0])):
            s = str(txt_file.iat[row, 0]).strip()
            if not s:
                txt_file.drop(row)
            if s.__contains__('failed'):
                page = s.split(' ')[1]
                print(path + ' , ' + page)
                url_dir = get_ids(browser, util.get_list_url(page))
                if url_dir:
                    count = 0
                    txt_file = txt_file.drop([row], axis=0)
                    for k, v in url_dir.items():
                        new_str = '{name},{urls}'.format(name=k, urls=v + '\n')
                        txt_file = pd.DataFrame(pd.np.insert(txt_file.values, row + count, [new_str]))
                        count += 1
        txt_file.sort_index(axis=0)
    except Exception as e:
        print('txt_retry() Exception : ' + e.__str__())
    finally:
        pd.np.savetxt(os.getcwd() + path, txt_file.values, fmt='%s', encoding='utf-8', newline='')
        print('txt_retry() ' + path + ' finish.')


def xls_retry(path):
    """
    replace None in xls
    :param path:
    :return:
    """
    count = (int(path.split('-')[2]) - 1) * 15
    data = pd.read_excel(path, sheet_name='Sheet1')
    browser = webdriver.Chrome()
    try:
        for row in range(data.shape[0]):
            s = str(data.iat[row, 0])
            if s.__contains__(',None'):
                print((count + row).__str__(), s)
                arr = data.iat[row, 0].split(',')
                detail = crawl_detail(browser, arr[-1])
                if detail:
                    # new_str = combine_str(arr, detail)
                    data = data.drop([row], axis=0)
                    new_str = (count + row + 1).__str__() + ',id,' + str(arr[-1]).split('=')[-1] + ',' \
                              + detail.__str__() + ',url,' + arr[-1]
                    print(new_str)
                    data = pd.DataFrame(pd.np.insert(data.values, row, [new_str], axis=0))
    finally:
        data.to_excel(path, index=False)


class XlsRetryThread(threading.Thread):
    def __init__(self, file_path):
        threading.Thread.__init__(self)
        self.file_path = file_path

    def run(self):
        print('starting ' + self.file_path)
        xls_retry(self.file_path)


class TxtRetryThread(threading.Thread):
    def __init__(self, file_path):
        threading.Thread.__init__(self)
        self.file_path = file_path

    def run(self):
        print('starting ' + self.file_path)
        txt_retry(self.file_path)


def xls_check(path, start=0):
    """
    check xls
    :param path:
    :param start:
    :return:
    """
    data = get_file_pd(path)
    error = []
    fail = []
    for index in range(data.shape[0]):
        item = str(data.iat[index, 0])
        if not item.__contains__(',None'):
            if item.strip().split(',')[0]:
                number = int(item.strip().split(',')[0]) - (15 * start)
                if not number == int(index + 1):
                    error.append(item)
                    print(index.__str__() + ' == ' + number.__str__(), item)
        else:
            fail.append(item)
            # print(item)
    if error.__len__() or fail.__len__():
        print(
            'check ' + path + ' finish : with ' + fail.__len__().__str__() + ' failed and ' + error.__len__().__str__() + ' error index has found')
    else:
        print('check ' + path + ' finish : with no error')


def txt_check(path, start=0):
    """
    check whether there is failed in txt
    eg
            for f in list_arr:
                i = int(re.compile('-').split(f)[2]) - 1
                check(FILE_DIR_LIST + f, i)

    :param path:
    :param start:
    :return:
    """
    content = get_file_content(path)

    error = []
    fail = []
    for index, item in enumerate(content):
        if not item.__contains__('failed'):
            if item.strip().split('.')[0]:
                number = int(item.strip().split('.')[0]) - (15 * start)
                if not number == index + 1:
                    error.append(item)
                    print(index.__str__() + ' == ' + item)
        else:
            fail.append(item)
            print(item)
    if error.__len__() or fail.__len__():
        print(
            'check ' + path + ' finish : with ' + fail.__len__().__str__() + ' failed and ' + error.__len__().__str__() + ' error index has found')
    else:
        print('check ' + path + ' finish : with no error')


def fill_xls(directory, l, d):
    """
    insert
    :param directory: category
    :param l: list file,txt
    :param d: detail file,xls
    """
    list_content = get_file_content(directory + folder[0] + l)
    detail_content = get_file_pd(directory + folder[1] + d)
    browser = webdriver.Chrome()
    try:
        for l_line, d_line in zip_longest(list_content, range(detail_content.shape[0]), fillvalue=None):
            txt_number = l_line.split('.')[0]
            if d_line is None:
                xls_number = -1
            else:
                xls_number = str(detail_content.iat[d_line, 0]).split(',')[0]
            if not txt_number == xls_number:
                print(txt_number + ' == ' + xls_number.__str__())
                print(txt_number, l_line.split(',')[1])
                detail = crawl_detail(browser, l_line.split(',')[1])
                insert_str = pd.DataFrame([txt_number + ',id,' + str(l_line.split('=')[-1]).strip() + ',' \
                                           + detail.__str__() + ',url,' + l_line.split(',')[1]])
                if xls_number == -1:
                    detail_content = pd.DataFrame(detail_content.append(insert_str, ignore_index=True))
                else:
                    detail_content = pd.DataFrame(pd.np.insert(detail_content.values, d_line, insert_str, axis=0))
    # except Exception as e:
    #     detail_content.to_excel(os.getcwd() + directory + folder[1] + d, index=False)
    finally:
        print('fill_xls() end')
        detail_content.to_excel(os.getcwd() + directory + folder[1] + d, index=False)


def txt_vs_xls(direct=None, txt_list=None, detail=None):
    """
       txt_vs_xls
    """
    if direct and txt_list and detail is not None:
        compare_txt_xls(detail, direct, txt_list)
    else:
        for directory in FILE_DIR_LIST:
            list_arr = [f for f in os.listdir(os.getcwd() + directory + folder[0]) if f[-3:] == 'txt']
            detail_arr = [f for f in os.listdir(os.getcwd() + directory + folder[1]) if f[-3:] == 'xls']
            for l, d in zip(list_arr, detail_arr):
                compare_txt_xls(d, directory, l)


def compare_txt_xls(d, directory, l):
    print(l + ' vs ' + d)
    list_content = get_file_content(directory + folder[0] + l)
    detail_content = get_file_pd(directory + folder[1] + d)
    error = []
    for l_line, d_line in zip_longest(list_content, range(detail_content.shape[0]), fillvalue=None):
        txt_number = str(l_line.split('.')[0])
        if d_line is None:
            xls_number = -1
        else:
            xls_number = str(detail_content.iat[d_line, 0]).split(',')[0]
        if not txt_number == xls_number:
            # print('list No. : ' + txt_number + ' == ' + xls_number)
            error.append(txt_number)
    if error.__len__():
        print(l + ' vs ' + d + ' finish : with ' + error.__len__().__str__() + ' error found')
    else:
        print(l + ' vs ' + d + ' finish : with no error')
    print('------------------------------------')


def retry_txt():
    """
        TxtRetryThread
    """
    for directory in FILE_DIR_LIST:
        l_arr = [f for f in os.listdir(os.getcwd() + directory + folder[0]) if f[-3:] == 'txt']
        for l in l_arr:
            f_path = directory + folder[0] + l
            print(f_path, l.split('.')[0])
            thread = TxtRetryThread(f_path)
            thread.start()


def check():
    """
    check
    """
    for directory in FILE_DIR_LIST:
        l_arr = [f for f in os.listdir(os.getcwd() + directory + folder[0]) if f[-3:] == 'txt']
        for l in l_arr:
            f_path = directory + folder[0] + l
            # print(f_path)
            txt_check(f_path, int(re.compile('-').split(l)[2]) - 1)
        print('------ ' + directory + ' txt check finish -------')

        d_arr = [f for f in os.listdir(os.getcwd() + directory + folder[1]) if f[-3:] == 'xls']
        for d in d_arr:
            f_path = directory + folder[1] + d
            xls_check(f_path, int(re.compile('-').split(d)[2]) - 1)
        print('------ ' + directory + ' xls check finish -------')


def retry_xls():
    for directory in FILE_DIR_LIST:
        l_arr = [f for f in os.listdir(os.getcwd() + directory + folder[1]) if f[-3:] == 'xls']
        for l in l_arr:
            f_path = os.getcwd() + directory + folder[1] + l
            print(f_path)
            thread = XlsRetryThread(f_path)
            thread.start()


def holy(path):
    """
    化妆品补字段（。
    :param path:
    :return:
    """
    data = get_file_pd(path)
    browser = webdriver.Chrome()
    try:
        for line in range(data.shape[0]):
            s = str(data.iat[line, 0])
            if not s.__contains__('产品名称备注'):
                # print(s)
                arr = s.split(',')
                detail_str = crawl_detail(browser, arr[-1])
                if detail_str:
                    detail_arr = detail_str.split(',')
                    # print(detail_arr)
                    arr.insert(-2, detail_arr[-2])
                    arr.insert(-2, detail_arr[-1])
                    print(arr)
                    data = data.drop([line], axis=0)
                    data = pd.DataFrame(pd.np.insert(data.values, line, [','.join(arr)], axis=0))
    finally:
        data.to_excel(os.getcwd() + '\\' + path, index=False)


if __name__ == '__main__':
    check()
    # retry_txt()
    # retry_xls()

    # xls_retry(os.getcwd() + '\\进口化妆品\\detail\\进口化妆品-list-5001-6000.xls')  done
    # xls_retry(os.getcwd() + '\\进口化妆品\\detail\\进口化妆品-list-7001-8000.xls')  done
    # xls_retry(os.getcwd() + '\\进口化妆品\\detail\\进口化妆品-list-8001-9000.xls')
    # xls_retry(os.getcwd() + '\\进口化妆品\\detail\\进口化妆品-list-9001-10000.xls')
    # xls_retry(os.getcwd() + '\\进口化妆品\\detail\\进口化妆品-list-10001-11000.xls') done
    # xls_retry(os.getcwd() + '\\进口化妆品\\detail\\进口化妆品-list-11001-12000.xls') done
    # xls_retry(os.getcwd() + '\\进口化妆品\\detail\\进口化妆品-list-12001-12809.xls') done

    # txt_vs_xls()
    name = '进口化妆品-list-9001-10000.xls'
    # name = '进口化妆品-list-10001-11000.xls'
    l_name = '进口化妆品-list-9001-10000.txt'
    # l_name = '进口化妆品-list-10001-11000.txt'
    # xls_check(FILE_DIR_LIST[0] + folder[1] + name, int(re.compile('-').split(name)[2]) - 1)
    # compare_txt_xls(name, FILE_DIR_LIST[0], l_name)
    # # fill_xls(FILE_DIR_LIST[0], l_name, name)
