import pandas as pd
from selenium import webdriver

from crawl import param
from crawl.crawl_details import crawl_detail

"""
国产药品-list-1-2500.xls
国产药品-list-2501-5000.xls
"""

"""
158,id,33946,None,url,http://app1.sfda.gov.cn/datasearch/face3/content.jsp?tableId=25&tableName=TABLE25&tableView=%E5%9B%BD%E4%BA%A7%E8%8D%AF%E5%93%81&Id=33946

批准文号,国药准字Z51021640,产品名称,龙胆泻肝片,英文名称,,商品名,,剂型,片剂(素片、糖衣片),规格,----,生产单位,四川禾润制药有限公司,生产地址,广汉市三星镇,产品类别,中药,批准日期,2015-08-21,原批准文号,,药品本位码,86902153000138；86902153000152


110660,id,95138
,批准文号,国药准字H32022930,产品名称,异烟肼,英文名称,Isoniazid,商品名,,剂型,原料药,规格,----,生产单位,苏州第五制药厂有限公司,生产地址,江苏省苏州市白洋湾大街169号,产品类别,化学药品,批准日期,2015-09-23,原批准文号,,药品本位码,86901648000066,url,http://app1.sfda.gov.cn/datasearch/face3/content.jsp?tableId=25&tableName=TABLE25&tableView=%E5%9B%BD%E4%BA%A7%E8%8D%AF%E5%93%81&Id=95138


"""

file_path = 'detail\\' + '国产药品-list-2501-5000.xls'


def combine_str(array, detail):
    array.remove('None')
    array.insert(3, detail)
    return ','.join(array)


def retry():
    try:
        count = 0
        browser = webdriver.Chrome()
        data = pd.read_excel(param.FILE_PREFIX + file_path, sheet_name='Sheet1')
        for row in range(data.shape[0] - 1):
            s = str(data.iat[row, 0])
            if s.__contains__(',None'):
                print(s)
                arr = s.split(',')
                new_str = combine_str(arr, crawl_detail(browser, arr[-1]))
                print(new_str)
                data = data.drop([row], axis=0)
                data = pd.DataFrame(pd.np.insert(data.values, row, [new_str]))
                count += 1
                if count > 100:
                    count = 0
                    data.to_excel(param.FILE_PREFIX + file_path, index=False)
    except Exception as ex:
        print("Exception has been thrown. " + str(ex))
    finally:
        data.to_excel(param.FILE_PREFIX + file_path, index=False)


# iloc[row-2,col]
# target_str = data.iloc[(40 - 2), 0]
# print(target_str.split(','))


if __name__ == '__main__':
    retry()
