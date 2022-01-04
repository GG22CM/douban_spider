#用来爬取豆瓣上的网页并且保存到excel表和sqlite数据库中


import xlwt
import urllib.request, urllib.error
from bs4 import BeautifulSoup
import re
import sqlite3

def main():
    datalist = get_datalist() #获取数据
    # into_excel(datalist, "movie.xls")
    into_db(datalist, "movie.db")
#爬取网页
headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0",
        'Cookie': '''Cookie: ll="118281"; bid=MBnrRKrE2h0; _pk_id.100001.4cf6=f5051cd51a131f6c.1640333008.1.1640333018.1640333008.; _pk_ses.100001.4cf6=*; ap_v=0,6.0; __utma=30149280.1044948428.1640333011.1640333011.1640333011.1; __utmb=30149280.0.10.1640333011; __utmc=30149280; __utmz=30149280.1640333011.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utma=223695111.1836595012.1640333011.1640333011.1640333011.1; __utmb=223695111.0.10.1640333011; __utmc=223695111; __utmz=223695111.1640333011.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _vwo_uuid_v2=D5E74A61A67A6421E63A3AC111319ACC7|18c3046e15855ea691f84a879e39cfdc'''
    }


def urlget(url):
    req = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(req)
    return response.read()


#获取数据
def get_datalist():
    datalist = []
    #循环爬取网页
    for i in range(10):
        url = "https://movie.douban.com/top250?start=%d"%(i*25)
        html = urlget(url)
        items = html2divs(html)
        for item in items:
            datalist.append(item2data(item))
    return datalist


#解析html数据
def html2divs(html):
    bs = BeautifulSoup(html, "html.parser")
    return bs.find_all("div", class_="item")

get_link = re.compile(r'<a href="(.*?)">')
get_imgsrc = re.compile(r'<img.*?src="(.*?)"')
get_name = re.compile(r'<span class="title">(.*?)</span>')
get_name_other = re.compile(r'<span class="other">(.*?)</span>')
get_create_info = re.compile(r'<p class="">(.*?)</p>', re.S)
get_rate = re.compile(r'<span class="rating_num" property="v:average">(.*?)</span>')
get_judge = re.compile(r'<span>(\d*)人评价</span>')
get_introduction = re.compile(r'<span class="inq">(.*?)</span>')
#解析item数据
def item2data(item):
    item = str(item)
    link = do_none(re.findall(get_link, item))[0]
    imgsrc = do_none(re.findall(get_imgsrc, item))[0]
    name = re.findall(get_name, item)

    if len(name) == 2:
        name = name[0]+" "+name[1]
    else:
        name = do_none(name[0])
    name_other =do_none(re.findall(get_name_other, item))[0]
    create_info = do_none(re.findall(get_create_info, item))[0]
    create_info = re.sub(r'\n', " ", create_info)
    create_info = create_info.replace("<br/>", "")
    create_info = create_info.replace("/", " ")
    create_info = create_info.strip()
    template = re.findall(r"([^\w\.]*?)\d", create_info)[0]
    create_info = re.sub(template, r"\n", create_info) #换行代替空白
    rate = do_none(re.findall(get_rate, item))[0]
    judge = do_none(re.findall(get_judge,item))[0]
    introduction = do_none(re.findall(get_introduction, item))[0]

    return [link, imgsrc, name, name_other, create_info, rate, judge, introduction]

#非空操作
def do_none(data):
    if not len(data):
        return [""]
    return data

#将数据放入excel
def into_excel(datalist, excel_name):
    workbook = xlwt.Workbook(encoding="utf-8")
    sheet1 = workbook.add_sheet("sheet1")

    for i, data in enumerate(['编号', '电影详情地址', '电影图片地址', '电影名', '别名', '详细信息', '评分', '评价人数', '电影介绍']):
        sheet1.write(0, i, data )
    for i, data in enumerate(datalist):
        sheet1.write(i+1, 0, i+1)
        for j in range(len(data)):
            sheet1.write(i+1, j+1, data[j])
    workbook.save(excel_name)
#将数据放入数据库
def into_db(datalist, connection):
    conn = sqlite3.connect(connection)
    cur = conn.cursor()

    for data in datalist:

        for i, item in enumerate(data):
            if not is_num(item):
               data[i] = "\"" + item + "\""
        sql = "insert into movie250(link, imgsrc, name, name_other, create_info, rate, judge, introduction) values (%s, %s, %s, %s, %s, %s, %s, %s)"%(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7])
        print(sql)
        cur.execute(sql)
        conn.commit()
    cur.close()
    conn.close()


#判断字符串是否未整数或者浮点树：
def is_num(s):
    if s.isdigit():
        return True
    res = re.match(r"^\d+\.\d*$", s)
    if res != None:
        return True
    return False
if __name__ == "__main__":
    main()


