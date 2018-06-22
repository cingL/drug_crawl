import codecs
import math
import os
import re
import threading
from itertools import zip_longest

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

from crawl import util
from crawl.crawl_details_new import crawl_detail
from crawl.crawl_list import get_ids
from crawl.util import get_file_content, get_file_pd, folder, FILE_DIR_LIST, arrange, get_title, get_list_url


def check(custom_directory=None):
    """
    check
    检查全部输出的文件
    fail -> 没抓取到的数据
    error -> 编号没对上的数据，错一个后面全部跪，数值很大，不要被吓坏

    :param custom_directory: optional, '\\directory_name\\', or '\\' means current folder
    :return:
    """
    if custom_directory is not None:
        txt_check(custom_directory,
                  [f for f in os.listdir(os.getcwd() + custom_directory + folder[0]) if f[-3:] == 'txt'])

        xls_check(custom_directory,
                  [f for f in os.listdir(os.getcwd() + custom_directory + folder[0]) if f[-3:] == 'xls'])

    else:
        for directory in FILE_DIR_LIST:
            l_arr = [f for f in os.listdir(os.getcwd() + directory + folder[0]) if f[-3:] == 'txt']
            txt_check(directory, l_arr)

            d_arr = [f for f in os.listdir(os.getcwd() + directory + folder[1]) if f[-3:] == 'xls']
            xls_check(directory, d_arr)


def xls_check(directory, file_arr):
    """
    check xls
    :param directory:
    :param file_arr:
    :return:
    """
    for d in file_arr:
        f_path = directory + folder[1] + d
        start = int(re.compile('-').split(d)[2]) - 1

        data = get_file_pd(f_path)
        error = []
        fail = []
        for index in range(data.shape[0]):
            item = str(data.iat[index, 0])
            if not item.__contains__(',None'):
                if item.strip().split(',')[0]:
                    number = int(item.strip().split(',')[0]) - (15 * start)
                    if number != int(index + 1):
                        error.append(item)
                        # print(index.__str__() + ' == ' + number.__str__())
            else:
                fail.append(item)
                # print(item)
        if error.__len__() or fail.__len__():
            print(
                'check ' + f_path + ' finish : with ' + fail.__len__().__str__() + ' failed and ' + error.__len__().__str__() + ' error index has found')
        else:
            print('check ' + f_path + ' finish : with no error')
    print('------ ' + directory + ' xls check finish -------')


def txt_check(directory, file_arr):
    """
    check whether there is failed in txt

    :param directory:
    :param file_arr:
    :return:
    """
    for l in file_arr:
        f_path = directory + folder[0] + l
        start = int(re.compile('-').split(l)[2]) - 1
        print(f_path)
        content = get_file_content(f_path)
        error = []
        fail = []
        for index, item in enumerate(content):
            if not item.__contains__('failed'):
                if item.strip().split('.')[0]:
                    number = int(item.strip().split('.')[0]) - (15 * start)
                    if number != index + 1:
                        error.append(item)
                        print(index.__str__() + ' == ' + item)
            else:
                fail.append(item)
                # print(item)
        if error.__len__() or fail.__len__():
            print(
                'check ' + f_path + ' finish : with ' + fail.__len__().__str__() + ' failed and ' + error.__len__().__str__() + ' error index has found')
        else:
            print('check ' + f_path + ' finish : with no error')
    print('------ ' + directory + ' txt check finish -------')


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
                    # new_str = combine_str(arr, detail) todo
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


def fill_txt(directory, l):
    """
    填补xls
    insert and append
    :param directory:
    :param l:
    :return:
    """
    start = int((l.split('-')[2]).split('.')[0]) - 1
    end = int((l.split('-')[3]).split('.')[0])
    # print('start:' + start.__str__() + ' , end =' + end.__str__())
    list_content = get_file_content(directory + folder[0] + l)
    # print(list_content.__len__())
    browser = webdriver.Chrome()
    # insert
    try:
        for index, line in enumerate(list_content):
            if line.strip():
                number = int(line.split('.')[0]) - start * 15
                if index + 1 != number:
                    print(index + 1, number)
                    page = math.ceil(index / 15) + start
                    urls = get_ids(browser, get_list_url(page))
                    # print(urls)
                    if urls:
                        for k, v in urls.items():
                            if int(str(k).split('.')[0]) == (index + start * 15):
                                insert_str = '{name},{urls}'.format(name=k, urls=v + '\n')
                                print(l + ' ' + index.__str__() + ' row insert : ' + insert_str)
                                list_content.insert(index, insert_str)
                    else:
                        list_content.insert(index, index.__str__() + '. crawl failed')

        print('--- ' + l + ' insert finish. ---')

        # append
        last_index = list_content.__len__()
        from_page = int(round((last_index / 15) + start, 0))
        # print(from_page, end)
        if from_page != end and from_page <= end:
            last_content = (from_page - 1) * 15
            list_content = list_content[0:last_content]
            while from_page <= end:
                try:
                    url = util.get_list_url(from_page)
                    print(l + ' append page ' + from_page.__str__() + ' , ' + url)
                    url_list = get_ids(browser, url)
                    try:
                        for k, v in url_list.items():
                            if not v.startswith('http'):
                                raise Exception('cannot get page content : ' + k + ',' + v)
                            append_str = k + ',' + v
                            list_content.append('\n' + append_str)
                            # print(append_str)
                    except Exception as e:
                        list_content.append('page ' + from_page.__str__() + ' crawl failed')
                        print(l + ' page ' + from_page.__str__() + ' crawl failed , with exception :' + e.__str__())
                except Exception as e:
                    list_content.append(' page ' + from_page.__str__() + ' crawl failed')
                    print(l + ' page ' + from_page.__str__() + ' crawl failed, with exception : ' + e.__str__())
                    continue
                finally:
                    from_page += 1

        print('--- ' + l + ' append finish. ---')
    except WebDriverException as e:
        print(e.__str__())
    finally:
        with codecs.open(os.getcwd() + directory + folder[0] + l, 'wb', encoding='utf-8') as f:
            f.write(''.join(list_content))
            f.close()


def fill_xls(directory, l, d):
    """
    填补xls
    insert and append
    注意，会因为内容格式……emmm……太花哨而fail

    :param directory: category
    :param l: list file,txt
    :param d: detail file,xls
    """
    list_content = get_file_content(directory + folder[0] + l)
    detail_content = get_file_pd(directory + folder[1] + d)
    start = (int(re.compile('-').split(d)[2]) - 1) * 15
    browser = webdriver.Chrome()
    col_len = len(detail_content.columns)
    try:
        while detail_content.shape[0] < list_content.__len__():
            detail_content = insert_or_append_xls(browser, detail_content, list_content, start, col_len)

    finally:
        print('fill_xls() end')
        browser.close()
        detail_content.to_excel(os.getcwd() + directory + folder[1] + d, index=False)


def insert_or_append_xls(browser, detail_content, list_content, start, col_len):
    for l_line, d_line in zip_longest(list_content, range(detail_content.shape[0]), fillvalue=None):
        txt_number = str(l_line.split('.')[0])
        if d_line is None:
            xls_number = -1
        else:
            xls_number = str(detail_content.iat[d_line, 0]).split(',')[0]
        if not txt_number == xls_number:
            print(txt_number + ' == ' + xls_number.__str__())
            # print(txt_number, l_line.split(',')[1])
            url = l_line.split(',')[-1]
            detail = crawl_detail(browser, url)
            if detail:
                # 组合成可分割的数组
                drug_id = url.split('=')[-1]
                detail.insert(1, str(drug_id).strip())
                detail.insert(1, txt_number)
                detail_arr = arrange(detail, url)
                title = get_title(detail)
                print(detail_arr)
                print('detail:' + detail_arr.__len__().__str__())
                print(title)
                print('title:' + title.__len__().__str__())
                try:
                    if xls_number == -1:  # append
                        detail_content = detail_content.append(pd.DataFrame(columns=title, data=[detail_arr]),
                                                               ignore_index=True, sort=False)
                    else:  # insert
                        detail_content = pd.DataFrame(
                            data=pd.np.insert(detail_content.values, int(txt_number) - start - 1, detail_arr,
                                              axis=0),
                            columns=title)
                except ValueError as e:
                    # 数组跟表头对不上的（含有特殊格式文本），截取，id 替换为 url
                    detail_arr[1] = detail_arr[detail_arr.__len__() - 1]
                    detail_arr = detail_arr[:col_len]
                    if xls_number == -1:
                        detail_content = detail_content.append(pd.DataFrame(data=[detail_arr]),
                                                               ignore_index=True, sort=False)
                    else:
                        detail_content = pd.DataFrame(
                            data=pd.np.insert(detail_content.values, int(txt_number) - start - 1, detail_arr,
                                              axis=0))
                        break
                    print(txt_number + ' crawl failed, with ValueError : ' + e.__str__())
    return detail_content


class TxtFillThread(threading.Thread):
    def __init__(self, directory, list_file):
        threading.Thread.__init__(self)
        self.directory = directory
        self.list_file = list_file

    def run(self):
        print('starting ' + self.list_file)
        fill_txt(self.directory, self.list_file)


class XlsFillThread(threading.Thread):
    def __init__(self, directory, list_file, detail_file):
        threading.Thread.__init__(self)
        self.directory = directory
        self.list_file = list_file
        self.detail_file = detail_file

    def run(self):
        print('starting ' + self.list_file + ' vs ' + self.detail_file)
        fill_xls(self.directory, self.list_file, self.detail_file)


def txt_vs_xls(direct=None, txt_list=None, detail=None):
    """
    用 txt 的序号 和 xls 的序号进行比对
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
        # print(l_line, int(detail_content.iat[d_line, 0]))
        txt_number = int(l_line.split('.')[0])
        if d_line is None:
            xls_number = -1
        else:
            xls_number = int(detail_content.iat[d_line, 0])
        if not txt_number == xls_number:
            print(txt_number, xls_number)
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


def retry_xls():
    for directory in FILE_DIR_LIST:
        l_arr = [f for f in os.listdir(os.getcwd() + directory + folder[1]) if f[-3:] == 'xls']
        for l in l_arr:
            f_path = os.getcwd() + directory + folder[1] + l
            print(f_path)
            thread = XlsRetryThread(f_path)
            thread.start()


def compare_url():
    """
    txt 的 link 的 id  VS xls 的数据 id
    :return:
    """
    for directory in FILE_DIR_LIST:
        l_arr = [f for f in os.listdir(os.getcwd() + directory + folder[0]) if f[-3:] == 'txt']
        d_arr = [f for f in os.listdir(os.getcwd() + directory + folder[1]) if f[-3:] == 'xls']
        for l, d in zip(l_arr, d_arr):
            print(l + ' vs ' + d)
            error = []
            list_content = get_file_content(directory + folder[0] + l)
            detail_content = get_file_pd(directory + folder[1] + d)
            for l_line, d_line in zip(list_content, range(detail_content.shape[0])):
                l_url = str(l_line).split(',')[-1].strip()
                l_id = int(l_url.split('=')[-1])
                # print(l_line, d_line)
                d_id = int(detail_content.iat[d_line, 1])
                # try:
                #     d_id = int(d_id)
                # except:
                #     d_id = d_id.split(',')[-1].strip().split('=')[-1]
                if l_id != d_id:
                    error.append(l_line.split('.')[0])
                    print('row ' + l_line.split('.')[0].__str__() + ' : ' + l_id.__str__() + ' == ' + d_id.__str__())
            if error.__len__():
                print('with ' + error.__len__().__str__() + ' error has found')
            print('--------------------------------')


def fill_all_txt(directory):
    l_arr = [f for f in os.listdir(os.getcwd() + directory + folder[0]) if f[-3:] == 'txt']
    for list_file in l_arr:
        TxtFillThread(directory, list_file).start()


def fill_all_xls(directory):
    l_arr = [f for f in os.listdir(os.getcwd() + directory + folder[0]) if f[-3:] == 'txt']
    d_arr = [f for f in os.listdir(os.getcwd() + directory + folder[1]) if f[-3:] == 'xls']
    for list_file, detail_file in zip(l_arr, d_arr):
        thread = XlsFillThread(directory, list_file, detail_file)
        thread.start()


if __name__ == '__main__':
    """检查 fail 和 数据缺失"""
    # check()

    """消灭 failed"""
    # retry_txt()
    # retry_xls()

    """填补缺失数据"""
    # fill_all_txt(FILE_DIR_LIST[0])
    fill_all_xls(FILE_DIR_LIST[0])

    """以url比对"""
    # compare_url()
    """以序号比对"""
    # txt_vs_xls()

    """合并文件"""
    # output_form(FILE_DIR_LIST[0])
