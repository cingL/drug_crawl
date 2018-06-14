import os
import re
from urllib import parse

total = 5000 + 1
step = 1000
start = 3000 + 1

#
name = '进口化妆品'
tableId = '69'
tableName = 'TABLE69'
bcId = '124053679279972677481528707165'

FILE_PREFIX = os.getcwd() + '\国产药品\\'
list_file = '国产药品-list-1-1.txt'
"""
page = 11070 ,166043条
国产药品
http://app1.sfda.gov.cn/datasearch/face3/base.jsp?
tableId=25
&tableName=TABLE25
&title=国产药品
&bcId=124356560303886909015737447882

进口化妆品
12809页 共192130条
http://app1.sfda.gov.cn/datasearch/face3/base.jsp?
tableId=69
&tableName=TABLE69
&title=进口化妆品
&bcId=124053679279972677481528707165


国产特殊用途化妆品
http://app1.sfda.gov.cn/datasearch/face3/search.jsp?
tableId=68
&bcId=138009396676753955941050804482
&tableName=TABLE68
&viewtitleName=COLUMN787
&viewsubTitleName=COLUMN793,COLUMN789
&curstart=2
&tableView=国产特殊用途化妆品
&State=1

"""


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
