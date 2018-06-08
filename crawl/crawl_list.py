import codecs
import re
from urllib import parse

from bs4 import BeautifulSoup
from selenium import webdriver

# http://app1.sfda.gov.cn/datasearch/face3/content.jsp?tableId=68&tableName=TABLE68&tableView=国产特殊用途化妆品&Id=26378
PREFIX = 'http://app1.sfda.gov.cn/datasearch/face3/content.jsp?tableId=68&tableName=TABLE68&tableView=' + parse.quote(
    '国产特殊用途化妆品') + '&Id='

PROXY = "127.0.0.1:58117"


def get_remote_driver():
    webdriver.DesiredCapabilities.CHROME['proxy'] = {
        "httpProxy": PROXY,
        "ftpProxy": PROXY,
        "sslProxy": PROXY,
        "noProxy": None,
        "proxyType": "MANUAL",
        "class": "org.openqa.selenium.Proxy",
        "autodetect": False
    }

    # you have to use remote, otherwise you'll have to code it yourself in python to
    return webdriver.Remote("http://localhost:4444/wd/hub", webdriver.DesiredCapabilities.FIREFOX)


def get_ids(html):
    urls = []
    try:
        browser = webdriver.Chrome()
        browser.get(html)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        for a in soup.find_all('a'):
            href = a['href']
            # print(href)
            arr = re.compile('=').split(href)
            arr = re.compile('\D').split(arr[-1])
            # print(arr[0])
            urls.append(PREFIX + arr[0])
            # print(PREFIX + arr[0])
    finally:
        return urls


if __name__ == '__main__':
    with codecs.open('list.txt', 'wb', encoding='utf-8') as fp:
        for i in range(1, 3):
            url = 'http://app1.sfda.gov.cn/datasearch/face3/search.jsp?tableId=68&bcId=138009396676753955941050804482&tableName=TABLE68&viewtitleName=COLUMN787&viewsubTitleName=COLUMN793,COLUMN789&curstart=' + i.__str__() + '&tableView=' + parse.quote(
                '国产特殊用途化妆品') + '&State=1'
            print(url)
            url_list = get_ids(url)
            fp.write('{urls}\n'.format(urls='\n'.join(url_list)))
