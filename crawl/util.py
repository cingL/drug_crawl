import codecs
import os
import re
from urllib import parse

import pandas as pd

"""
国产药品
field_count = -7
共11075页 共166112条
http://app1.sfda.gov.cn/datasearch/face3/base.jsp?
tableId=25
&tableName=TABLE25
&title=国产药品
&bcId=124356560303886909015737447882


进口化妆品
field_count = -6
共12835页 共192513条
http://app1.sfda.gov.cn/datasearch/face3/base.jsp?
tableId=69
&tableName=TABLE69
&title=进口化妆品
&bcId=124053679279972677481528707165


国产特殊用途化妆品
field_count = -8
共2444页 共36654条
http://app1.sfda.gov.cn/datasearch/face3/search.jsp?
tableId=68
&bcId=138009396676753955941050804482
&tableName=TABLE68
&State=1

进口器械
field_count = -4
共3295页 共49420条
tableId=27
tableName=TABLE27
bcId=118103063506935484150101953610
"""

# ----------！每个类别取的字段数不一样！----------
total = 11075 + 1
step = 1000
start = 0 + 1

field_count = -7
name = '国产药品'
tableId = '25'
tableName = 'TABLE25'
bcId = '124356560303886909015737447882'
folder = ['list\\', 'detail\\']
FILE_DIR_LIST = [
    # '\\国产药品\\',
    # '\\进口化妆品\\',
    # '\\国产特殊用途化妆品\\'
    '\\进口器械\\'
]


def get_detail_url(a_href):
    """
    http://app1.sfda.gov.cn/datasearch/face3/content.jsp?tableId=68&tableName=TABLE68&tableView=国产特殊用途化妆品&Id=26378
    :param a_href:
    :return:
    """
    arr = re.compile('=').split(a_href)
    arr = re.compile('\D').split(arr[-1])
    prefix = 'http://app1.sfda.gov.cn/datasearch/face3/content.jsp?' \
             'tableId=' + tableId \
             + '&tableName=' + tableName + \
             '&tableView=' + parse.quote(name) + '&Id='
    return prefix + arr[0]


def get_list_url(index):
    """
    http://app1.sfda.gov.cn/datasearch/face3/search.jsp?tableId=69&bcId=124053679279972677481528707165&tableName=TABLE69&curstart=4386&tableView=%E8%BF%9B%E5%8F%A3%E5%8C%96%E5%A6%86%E5%93%81&State=1
    :param index:
    :return:
    """
    return 'http://app1.sfda.gov.cn/datasearch/face3/search.jsp?' \
           'tableId=' + tableId \
           + '&bcId=' + bcId \
           + '&tableName=' + tableName \
           + '&curstart=' + index.__str__() \
           + '&tableView=' + parse.quote(name) + '&State=1'
    # + '&viewtitleName=' + viewtitleName \
    # + '&viewsubTitleName=' + viewsubTitleName


def get_file_pd(path):
    return pd.read_excel(os.getcwd() + path, sheet_name='Sheet1')


def get_file_content(file):
    """
    get the content of file
    :param file: file path
    :return: an array with file content
    """
    content = []
    with codecs.open(os.getcwd() + file, 'r', 'utf-8') as t:
        for line in t:
            content.append(line)
    t.close()
    return content


def arrange(arr, url):
    result = []
    arr.pop(0)
    arr.insert(0, 'No.')
    arr.insert(2, 'ID.')
    for i in arr[1:field_count:2]:
        result.append(i)
    result.append(str(url).strip())
    return result


def get_title(arr):
    print(arr.__len__().__str__())
    arr.pop(0)
    arr.insert(0, 'No.')
    result = []
    for i in arr[0:field_count - 1:2]:
        result.append(i)
    result.append('url')
    return result


def output_form(directory):
    all_xls = pd.DataFrame()
    d_arr = [f for f in os.listdir(os.getcwd() + '\\' + directory + folder[1]) if f[-3:] == 'xls']
    d_arr = sorted(d_arr, key=lambda f: int(f.split('-')[2]))
    # print(d_arr)
    with pd.ExcelWriter(name + '.xlsx') as writer:
        try:
            for xls in d_arr:
                print(xls)
                data = get_file_pd('\\' + directory + folder[1] + xls)
                all_xls = all_xls.append(data, ignore_index=True, sort=False)
        finally:
            print(all_xls)
            all_xls.to_excel(writer, merge_cells=False, index=False)
    writer.close()
