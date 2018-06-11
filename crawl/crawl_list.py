import codecs
import re
from urllib import parse

from bs4 import BeautifulSoup
# PROXY = "127.0.0.1:58117"
# def get_remote_driver():
#     webdriver.DesiredCapabilities.CHROME['proxy'] = {
#         "httpProxy": PROXY,
#         "ftpProxy": PROXY,
#         "sslProxy": PROXY,
#         "noProxy": None,
#         "proxyType": "MANUAL",
#         "class": "org.openqa.selenium.Proxy",
#         "autodetect": False
#     }
#     # you have to use remote, otherwise you'll have to code it yourself in python to
#     return webdriver.Remote("http://localhost:4444/wd/hub", webdriver.DesiredCapabilities.FIREFOX)
from selenium import webdriver


# http://app1.sfda.gov.cn/datasearch/face3/content.jsp?tableId=68&tableName=TABLE68&tableView=国产特殊用途化妆品&Id=26378


def get_ids(driver, html):
    urls = []
    try:
        driver.get(html)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # print(browser.page_source)
        for a in soup.find_all('a'):
            href = a['href']
            details = get_detail_url(href)
            # print(details)
            urls.append(details)
    finally:
        return urls


def get_detail_url(a_href):
    arr = re.compile('=').split(a_href)
    arr = re.compile('\D').split(arr[-1])
    # http://app1.sfda.gov.cn/datasearch/face3/content.jsp?tableId=68&tableName=TABLE68&tableView=国产特殊用途化妆品&Id=26378
    prefix = 'http://app1.sfda.gov.cn/datasearch/face3/content.jsp?tableId=68&tableName=TABLE68&tableView=' \
             + parse.quote('国产特殊用途化妆品') + '&Id='
    return prefix + arr[0]


def get_list_url(index, category):
    return 'http://app1.sfda.gov.cn/datasearch/face3/search.jsp?tableId=68&bcId=138009396676753955941050804482&tableName=TABLE68&viewtitleName=COLUMN787&viewsubTitleName=COLUMN793,COLUMN789&curstart=' \
           + index.__str__() + '&tableView=' + parse.quote(category) + '&State=1'


def do_crawl(index_arr):
    with codecs.open('list.txt', 'wb', encoding='utf-8') as fp:
        browser = webdriver.Chrome()
        for i in range(index_arr[0], index_arr[1]):
            url = get_list_url(i, '国产特殊用途化妆品')
            # print(url)
            url_list = get_ids(browser, url)
            fp.write('{urls}\n'.format(urls='\n'.join(url_list)))
            print('{urls}\n'.format(urls='\n'.join(url_list)))
        browser.close()


if __name__ == '__main__':
    total = 10
    current = 0
    start = 1
    step = 1
    while current < total:
        sub = []
        sub.append(start)
        current += step
        sub.append(current)
        start = current
        print(sub)
        do_crawl(sub)
