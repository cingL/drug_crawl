1. 修改 util.py 文件的参数
2. run crawl_list.py 

    会输出两个文件： 
    
    《name-list-PageStart-PageEnd.txt》,用来存每一页的内容，url为该药品详细页面url；
    
    《name-list-PageStart-PageEnd.xls》,用来存每条数据的内容。请勿在抓取过程中打开！读写错误GG
    
3. retry.py 用来检查和填补 步骤2 输出的文件
   具体参考该文件各个函数
   
P.S. 各种bug，留了todo，你猜什么时候填？
    




