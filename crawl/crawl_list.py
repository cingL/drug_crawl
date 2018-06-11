import codecs
import threading

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

from crawl import param


# PROXY = "61.101.178.32:1752"
#
#
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
#     return webdriver.Remote(webdriver.DesiredCapabilities.CHROME)


def get_ids(driver, html, times=0):
    """
    :param driver: web driver
    :param html: url
    :param times: current times
    :return: list
    """
    urls = {}
    try:
        driver.get(html)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # print(browser.page_source)
        all_a = soup.find_all('a')
        if all_a:
            for a in soup.find_all('a'):
                href = a['href']
                title = a.getText().strip()
                details = param.get_detail_url(href)
                # print(d   etails)
                # urls.append(details)
                urls[title] = details
    except TimeoutException as ex:
        print("Exception has been thrown. " + str(ex))
    finally:
        if urls:
            return urls
        else:
            # retry
            if times < 3:
                times += 1
                get_ids(driver, html, times)
            else:
                return urls


def do_crawl(index_arr):
    """
    :param index_arr: range()
    """
    file_name = param.name + '-list-' + (index_arr[0]).__str__() + '-' + (index_arr[1] - 1).__str__() + '.txt'
    with codecs.open(file_name, 'wb', encoding='utf-8') as fp:
        browser = webdriver.Chrome()
        # browser = get_remote_driver()
        for i in range(index_arr[0], index_arr[1]):
            url = param.get_list_url(i)
            # print(url)
            url_list = get_ids(browser, url)
            if url_list:
                for k, v in url_list.items():
                    fp.write('{name},{urls}'.format(name='\n' + k, urls=v))
                    print('{name},{urls}'.format(name='\n' + k, urls=v))
            else:
                fp.write('\npage ' + i.__str__() + ' crawl failed')
                print('\npage ' + i.__str__() + ' crawl failed')
        fp.close()
    # browser.close()


class CrawlThread(threading.Thread):
    def __init__(self, tid, arr):
        threading.Thread.__init__(self)
        self.tid = tid
        self.arr = arr

    def run(self):
        print('starting ' + self.name)
        do_crawl(self.arr)


if __name__ == '__main__':
    threads = []
    while param.start < param.total:
        end = param.start + param.step if param.step + param.start < param.total else param.total
        print('(' + param.start.__str__() + ' , ' + end.__str__() + ')')
        thread = CrawlThread(1, [param.start, param.start + param.step])
        threads.append(thread)
        thread.start()
        param.start += param.step
