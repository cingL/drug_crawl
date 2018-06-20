import codecs
import threading

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver

from crawl import util
from crawl.crawl_details_new import crawl_detail
from crawl.util import arrange, get_title


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
                details = util.get_detail_url(href)
                urls[title] = details
    # except TimeoutException as ex:
    #     print("Exception has been thrown. " + str(ex))
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
    file_name = util.name + '-list-' + (index_arr[0]).__str__() + '-' + (index_arr[1] - 1).__str__() + '.txt'
    xls_file_name = util.name + '-list-' + (index_arr[0]).__str__() + '-' + (index_arr[1] - 1).__str__() + '.xls'
    detail_content = pd.DataFrame()
    browser = webdriver.Chrome()
    with codecs.open(file_name, 'wb', encoding='utf-8') as fp:
        for i in range(index_arr[0], index_arr[1]):
            url = util.get_list_url(i)
            # print(url)
            url_list = get_ids(browser, url)
            if url_list:
                try:
                    for k, v in url_list.items():
                        fp.write('{name},{urls}'.format(name='\n' + k, urls=v))
                        detail = crawl_detail(browser, v)
                        if detail:
                            try:
                                number = int(k.split('.')[0])
                                drug_id = v.split('=')[-1]
                            except Exception as e:
                                print('\npage ' + i.__str__() + ' crawl failed', e)
                                continue
                            detail.insert(1, str(drug_id).strip())
                            detail.insert(1, number)
                            detail_arr = arrange(detail, v)
                            title = get_title(detail)
                            # print(detail_arr)
                            # print('detail:' + detail_arr.__len__().__str__())
                            # print(title)
                            # print('title:' + title.__len__().__str__())
                            detail_content = detail_content.append(pd.DataFrame(columns=title, data=[detail_arr]),
                                                                   ignore_index=True, sort=False)
                            print('{name},{urls}'.format(name='\n' + k, urls=v))
                            print(xls_file_name, detail_arr)
                except Exception as e:
                    print('\npage ' + i.__str__() + ' crawl failed', e)
                finally:
                    detail_content.to_excel(xls_file_name, index=False)
            else:
                fp.write('\npage ' + i.__str__() + ' crawl failed')
                print('\n ')
        fp.close()
    # browser.close()


class CrawlThread(threading.Thread):
    def __init__(self, arr):
        threading.Thread.__init__(self)
        self.arr = arr

    def run(self):
        print('starting ' + self.name)
        do_crawl(self.arr)


if __name__ == '__main__':
    while util.start < util.total:
        end = util.start + util.step if util.step + util.start < util.total else util.total
        print('(' + util.start.__str__() + ' , ' + end.__str__() + ')')
        thread = CrawlThread([util.start, end])
        thread.start()
        util.start += util.step
