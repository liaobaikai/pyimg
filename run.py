from bs4 import BeautifulSoup
from bs4 import Tag
import requests
import os
from urllib import parse
import re
import sys

# 域名正则表达式
domain_pattern = re.compile(
    r'^(([a-zA-Z])|([a-zA-Z][a-zA-Z])|'
    r'([a-zA-Z][0-9])|([0-9][a-zA-Z])|'
    r'([a-zA-Z0-9][-_.a-zA-Z0-9]{0,61}[a-zA-Z0-9]))\.'
    r'([a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})$'
)

sys.setrecursionlimit(100000)

# 解析出来的数据
data = []

# 连接的选择器
# 选择器: { 属性：正则, 属性：正则, ... }
link_selectors = {
    "table.xwlb": {
        'onclick': r'location.href="(.+?)"',
    },
    "a": {
        'href': None
    }

}
base_url = "https://www.xiami.com/"
charset = 'gb2312'
include_paths = ["/manager/tools/Grace/uploadfile"]
download_path = "/Users/fei00/Desktop/虾米/"
header = {
    # 'Referer': 'http://www.gdys938.com/default.aspx?pageid=46',
    'Cookie': '_xm_umtoken=TE12AB502B78B873DF012A5E906754C06402122DFE1B24B4469D97F286C; gid=159524391333226; join_from=1zufSNtP6D010%2FjCCA; _xiamitoken=87cd569452e26d50946643cf9811d4f7; _unsign_token=e7951d399c5ea9dcaccdfb223a7b9e59; user_from=1; cna=6z6XFwP7fSwCAbcyz1KEChdx; UM_distinctid=1736bf26c21449-07fa358cd7b47e8-4a5a66-13c680-1736bf26c22529; isg=BBISyVFombgFf-XEcVb_n6G6YN70Ixa98K4lndxrsUWw77Hp0rLBzFMdXctThI5V; l=eBMYMSL4OTcylHJsBOfahurza77OSIOYYuPzaNbMiOCPOp1B5Gj5WZk7XuT6C31Vhs_JR3R79SBHBeYBcQAonxvtlrFEy4Hmn; _xm_cf_=WEGVqNZQGx9hLrJJQSgp9OmL; xmgid=be23bea3-218c-461c-a7f7-ab469a7e61b4; xm_sg_tk=7bb1afd1c1834bbcb228979eaabad611_1595243966341; xm_sg_tk.sig=jwOILr3KI9z2lEtXY_hJUK_KEHhEk2WcZhp2iYYTla8; xm_traceid=0bb84c4415952439992987865efffe; xm_oauth_state=bbaea2ed738e97a783b9948c91bbccc3; _uab_collina=159524396669735755653357; _xm_umtoken=T7B2647A453299DA804F526B960E4F4C3C81F4F0D411BC2A96C098C718A',
    'Host': parse.urlparse(base_url).hostname,
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:68.0) Gecko/20100101 Firefox/68.0'
}
if download_path[-1] != '/':
    download_path += '/'

# anchor_upload_prefix = "/uploads"

# 当前在跑的URL
current_url = ""

s = requests.session()

# 整站的锚点(a标签)
all_links = {}
download_files = {}


# 判断域名是有为有效的域名
def is_valid_domain(value):
    try:
        return True if domain_pattern.match(value) else False
    except Exception as e:
        print("is_valid_domain", e)
    return False


# 保存网页
def save_html(html: str, url: str):
    pass


# 文件下载
def download(url: str):

    url = parse.unquote(url)

    if url.startswith("http://") or url.startswith("https://"):
        pass
    else:
        url = parse.urljoin(base_url, url)

    p = parse.urlparse(url)
    if not p or not p.hostname or is_valid_domain(p.hostname) is False:
        print("无效的地址：`{}`".format(url))
        return

    if download_files.get(url) == 1:
        print("已跳过：`{}` ... 文件已下载。".format(url))
        return

    # 本地文件目录
    # 考虑非本站点的文件
    #
    try:
        local_file = download_path + p.hostname + p.path
    except Exception as e:
        print("url", url)
        print("download_path", download_path)
        print("hostname", p.hostname)
        print("path", p.path)
        print('local_file:', e)
        return

    if os.path.exists(local_file):
        print("已跳过：`{}` ... 文件已存在。".format(url))
        return

    local_file_path = os.path.dirname(local_file)
    if not os.path.exists(local_file_path):
        print("创建本地目录：`{}` ... ".format(local_file_path), end='')
        os.makedirs(local_file_path)
        print('成功。', end='\n')

    try:
        print("即将下载: `{}` <= `{}` ... ".format(local_file, url), end='')
        remote_file = s.get(url, headers=header, stream=True, timeout=1)
        if remote_file.status_code == 200:
            with open(local_file, "wb") as rf:
                for chunk in remote_file.iter_content(chunk_size=1024):
                    if chunk:
                        rf.write(chunk)
            print("成功。", end='\n')
            download_files[url] = 1
        else:
            print('失败！响应码: {}'.format(remote_file.status_code), end='\n')
    except Exception as e:
        print("download", e)
        pass


# 分析所有图片：查找并下载
def analyze_image(soup: BeautifulSoup):
    # 获取当前页面的所有图片
    images = soup.find_all('img')

    for img in images:

        if img.attrs.get('src') is None:
            continue
        elif len(img.attrs.get('src')) == 0:
            continue

        image_src = img.attrs['src']
        download(image_src)


# 分析所有超链接
# def analyze_anchor(soup: BeautifulSoup):
#     # 获取当前页面的所有超链接
#     anchors = soup.find_all('a')
#     # 如果超链接开头是 /uploads 的话，下载文件
#     for anchor in anchors:
#         anchor_href = anchor.attrs.get('href')
#         # print(anchor.attrs)
#         if anchor_href is None:
#             continue
#
#         is_external_links = False
#         if anchor_href[0:4] == 'http' and anchor_href[0:len(base_url)] != base_url:
#             is_external_links = True
#         if is_external_links:
#             continue
#
#         # 获取连接的文件
#         if all_links.get(anchor_href) == 1:
#             continue
#         else:
#             all_links[anchor_href] = 1
#             if anchor_href[0:1] == "/" or anchor_href[0:4] != 'http':
#                 analyze(base_url + anchor_href)
#             else:
#                 analyze(anchor_href)

def handle(el_attr_value: str, current_url: str):
    # print(anchor.attrs)
    if el_attr_value is None:
        return

    is_external_links = False
    if el_attr_value[0:4] == 'http' and el_attr_value[0:len(base_url)] != base_url:
        is_external_links = True
    if is_external_links:
        return

    # 获取连接的文件
    if all_links.get(el_attr_value) == 1:
        return
    else:
        all_links[el_attr_value] = 1
        if el_attr_value[0:1] == "/":
            # 如 /Upload
            analyze(base_url + el_attr_value)
        elif el_attr_value[0:1] == '?':
            # 如 ?id=aaaa
            analyze(current_url.split("?")[0] + el_attr_value)
        elif el_attr_value[0:4] != 'http':
            # 如 Upload
            # 拼接当前的路径
            print("current_url", current_url)
            print("el_attr_value", el_attr_value)
            p = parse.urlparse(current_url)
            print("path:", ('/'.join(p.path.split("/")[0:-1]) + '/').replace("//", "/"))
            link_url = "{}{}{}".format(base_url,
                                       ('/'.join(p.path.split("/")[0:-1]) + '/').replace("//", "/"), el_attr_value)
            print("link_url", link_url)
            analyze(link_url)
        else:
            # 如 http://
            analyze(el_attr_value)


# 分析额外绑定的元素
def analyze_link_elements(soup: BeautifulSoup, current_url: str):
    for selector in link_selectors:
        # 获取当前页面的所有连接
        elements = soup.select(selector)
        # 如果超链接开头是 /uploads 的话，下载文件
        for el in elements:
            selector_attrs = link_selectors.get(selector)
            # 选择器对应的是属性值
            for selector_attr in selector_attrs.keys():
                re_value = selector_attrs.get(selector_attr)
                el_attr_value = el.attrs.get(selector_attr)
                if re_value == '' or re_value is None:
                    # 正则没设置
                    handle(el_attr_value, current_url)
                else:
                    # 通过正则获取内容
                    for el_attr_value in re.findall(re_value, el_attr_value):
                        handle(el_attr_value, current_url)


# 拦截器
def filter(soup: BeautifulSoup):

    menu_selector = ".td0 tr td:nth-child(2) > span"
    title_selector = ".td1 font"
    article_selector = ".td1 table div"

    try:
        menu_element = soup.select(menu_selector)
        menu_text = menu_element[0].contents[0]

        # print(menu_text)
        title_element = soup.select(title_selector)
        title_text = title_element[0].contents[0]
        # print(title_text)

        release_time = title_element[0].parent.parent.select("div:last-child")[0].contents[0]
        # print(release_time)

        article_element = soup.select(article_selector)

        article_content = []
        for el in article_element[3].contents:
            if type(el) == Tag:
                article_content.append(el.decode())
            else:
                article_content.append("\n")

        # print(''.join(article_content))
        data.append((menu_text, title_text, ''.join(article_content), release_time))
    except Exception as e:
        print('filter Exception > {}', e)
        pass


# 分析页面
def analyze(url):
    print("正在分析: `{}`".format(url))
    try:
        if is_valid_domain(parse.urlparse(url).hostname) is False:
            print("无效的地址：`{}`".format(url))
            return
        r = s.get(url, headers=header)
        if r.status_code == 200:
            r.encoding = 'utf-8'
        else:
            print('响应码[{}]: `{}`'.format(r.status_code, url))
            return
    except Exception as e:
        print(e)
        return

    r.encoding = charset
    html = r.text

    # application/pdf
    content_type = r.headers.get("Content-Type")
    if content_type.split(";")[0] != "text/html":
        # html类型的是网页
        # 其他类型的需要下载
        # if href[0:len(anchor_upload_prefix)] == anchor_upload_prefix:
        download(url)
    else:
        save_html(html, url)

    try:
        soup = BeautifulSoup(html, features='html.parser')
        analyze_image(soup)
        analyze_link_elements(soup, url)
        # filter(soup)
    except Exception as e:
        print('analyze > Exception: ', e)


# 开始执行
def run(href):
    all_links[href] = 1
    analyze(href)


# run("http://www.gds940.com/news.asp?lflm=1.2")
run(base_url)


print('站点链接数：{}'.format(len(all_links.keys())))
print('下载文件数：{}'.format(len(download_files.keys())))

# print('解析到文章数: {}'.format(len(data)))
# print('即将插入数据库')
# import pymysql
# db_config = {
#    'host': '127.0.0.1',
#    'port': 3306,
#    'user': 'baikai',
#     'passwd': 'baikai#1234',
#     'db': 'cehui',
#     'charset': 'utf8'
# }
# conn = pymysql.connect(**db_config)
# cursor = conn.cursor()
# cursor.executemany(
#         'insert into `article` (`menu_text`, `title`, `content`, `created_time`) values (%s, %s, %s, %s)', data)
# conn.commit()
