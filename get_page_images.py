import requests
from bs4 import BeautifulSoup
from bs4 import Tag


import pymysql
db_config = {
   'host': '127.0.0.1',
   'port': 3306,
   'user': 'baikai',
    'passwd': 'baikai#1234',
    'db': 'cehui',
    'charset': 'utf8'
}
conn = pymysql.connect(**db_config)
cursor = conn.cursor()


r = requests.get('http://gdysch.com/main/200811115295737/Page/20101026142927937/NewsDetail.asp?NewsID=20190808165346734')
r.encoding = 'gb2312'
# print(r.text)
soup = BeautifulSoup(r.text, features='html.parser')


def filter():
    menu_selector = ".td0 tr td:nth-child(2) > span"
    title_selector = ".td1 font"
    article_selector = ".td1 table div"

    menu_element = soup.select(menu_selector)
    menu_text = menu_element[0].contents[0]

    print(menu_text)
    title_element = soup.select(title_selector)
    title_text = title_element[0].contents[0]
    print(title_text)

    release_time = title_element[0].parent.parent.select("div:last-child")[0].contents[0]
    print(release_time)

    article_element = soup.select(article_selector)

    article_content = []
    for el in article_element[3].contents:
        if type(el) == Tag:
            article_content.append(el.decode())
        else:
            article_content.append("\n")

    print(''.join(article_content))

    cursor.execute('insert into `article` (`menu_text`, `title`, `content`, `created_time`) values (%s, %s, %s, %s)', (
        menu_text, title_text, ''.join(article_content), release_time
    ))

    conn.commit()


filter()
