import codecs

import xlwt as xlwt
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

from crawl import param


def crawl_detail(url):
    detail_str = ''
    try:
        browser = webdriver.Chrome()
        browser.get(url)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        div = soup.find('div', attrs={'class': 'listmain'})
        table = div.find_all('table')[0]
        all_td = table.find_all('td')
        # todo 剔除第一行那个乱码
        for td in all_td:
            detail_str += td.getText().strip() + ','
    except TimeoutException as ex:
        print("Exception has been thrown. " + str(ex))
    finally:
        return detail_str


if __name__ == '__main__':
    book = xlwt.Workbook()
    sh = book.add_sheet(param.name)
    with codecs.open(param.list_file, 'rb', 'utf-8') as f:
        # read file ,get url,get No.
        for line in f:
            # line = '1.维生素B1片 (86902259000483 四川金药师制药有限公司 国药准字H51021516),http://app1.sfda.gov.cn/datasearch/face3/content.jsp?tableId=25&tableName=TABLE25&tableView=%E5%9B%BD%E4%BA%A7%E8%8D%AF%E5%93%81&Id=109149'
            drug_url = line.split(',')[-1]
            number = int(line.split(',')[0].split('.')[0])
            # crawl detail
            detail = crawl_detail(drug_url)
            sh.write(number - 1, 0, detail.__str__())
            book.save('维生素B1片.xls')
            break
        f.close()
