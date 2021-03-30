# -*- coding: utf-8 -*-
'''
@Time    : 2020/08/01 
@Author  : Yue Yang
@Site    :
@File    : csdn访客量.py
@Software: PyCharm
'''

"""
Annotation by Yue Yang:
1. note: when use requests.get(), please use headers, or probably get nothing from the target url.

2. the code is modified by Yue Yang. The changes are following(see details in git):
    a. the split-page method now dosn't work, so we adapt a not split-page method.
    b. we change from sleeping a fixed time to sleep a random time, which is more like the real visit.
    c. a single thread to multi-thread
	d. add exception-handle.
	
3. note that we use some proxies which comes from  'https://www.kuaidaili.com/free/inha/'
    sometimes we may fail to visit the web, please try again. 
    sleeping before visit the proxy-get web again can reduce the risk of failure.

"""

import linecache
import time
import re
from pyquery import PyQuery as pq
import requests
from bs4 import BeautifulSoup
import random
from fake_useragent import UserAgent
from lxml import etree
import ssl
import _thread, threading
ssl._create_default_https_context = ssl._create_unverified_context

headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
        }

# 爬取csdn类


class ScrapyMyCSDN:
    ''' class for csdn'''

    def __init__(self, blogname):
        '''init 类似于构造函数 param[in]:blogname:博客名'''
        csdn_url = 'https://blog.csdn.net/'  # 常规csdnurl
        self.blogurl = csdn_url + blogname  # 拼接字符串成需要爬取的主页url
        self.blog_nums = 0  # 原创博客数量
        self.blog_vs = 0  # 博客访客量

    '''博客访问量'''

    def get_vs(self, headers, proxies):
        main_response = requests.get(
            self.blogurl, timeout=10, headers=headers, proxies=proxies)
        if main_response.status_code == 200:
            soup = BeautifulSoup(main_response.text, 'html.parser')
            text : str = soup.find('div', class_='user-profile-statistics-num').text
            self.blog_vs = int(text.replace(',',''))
            return self.blog_vs  # 返回博文数量
        else:
            print('爬取失败')
            return 0  # 返回0 说明博文数为0或者爬取失败

    ''' Func:获取写了多少篇原创文章 '''
    ''' return:写了多少篇原创文章'''

    def getOriginalArticalNums(self, headers, proxies, fal):
        main_response = requests.get(
            self.blogurl, timeout=10, headers=headers, proxies=proxies)
        # 判断是否成功获取 (根据状态码来判断)
        # print('状态码', main_response.status_code)
        if main_response.status_code == 200:
            if fal:
                print('获取成功')
            self.main_html = main_response.text
            # print(self.main_html, main_response.text)
            html = BeautifulSoup(self.main_html, "html.parser")
            # print('html', html)
            # print('内容', html.find_all('div', class_='data-info d-flex item-tiling'))
            for tag in html.find_all('div', class_='data-info d-flex item-tiling'):
                # print('tag', tag)
                self.blog_nums = int(
                    tag.find('span', class_='count').get_text())
                break
                # print('blog_nums', self.blog_nums)
            if fal:
                print("原创博客数量为"+":"+str(self.blog_nums))
            return self.blog_nums  # 返回博文数量
        else:
            if fal:
                print('爬取失败')
            return 0  # 返回0 说明博文数为0或者爬取失败

    ''' Func：分页'''
    ''' param[in]:nums:博文数 '''
    ''' return: 需要爬取的页数'''

    def getScrapyPageNums(self, nums, fal):
        self.blog_original_nums = nums
        if nums == 0:
            if fal:
                print('它没写文章，0页啊！')
            return 0
        else:
            if fal:
                print('现在开始计算')
            cur_blog = nums/20  # 获得精确的页码
            cur_read_page = int(nums/20)  # 保留整数
            # 进行比对
            if cur_blog > cur_read_page:
                self.blog_original_nums = cur_read_page + 1
                if fal:
                    print('你需要爬取 %d' % self.blog_original_nums + '页')
                return self.blog_original_nums  # 返回的数字
            else:
                self.blog_original_nums = cur_read_page
                if fal:
                    print('你需要爬取 %d' % self.blog_original_nums + '页')
            return self.blog_original_nums

    '''Func:开始爬取，实际就是刷浏览量hhh'''
    '''param[in]:page_num:需要爬取的页数'''
    '''return:0:浏览量刷失败'''

    def beginToScrapy(self, page_num, header, proxies, fal):
        if page_num == 0:
            if fal:
                print('连原创博客都不写 爬个鬼!')
            return 0
        else:
            article_doc = requests.get(
                self.blogurl, timeout=10, headers=header, proxies=proxies)  # 访问该网站
            # 先判断是否成功访问
            if article_doc.status_code == 200:

                # 进行解析
                cur_page_html = article_doc.text
                # print(cur_page_html)
                soup = BeautifulSoup(cur_page_html, 'html.parser')
                articles = soup.find_all('p', class_="content")
                for link in articles:
                    # print(link.find('a')['href'])
                    art_url = link.find('a')['href']
                    requests.get(art_url, proxies=proxies, headers=header)  # 进行访问
                    time.sleep(0.1)
            else:
                if fal:
                    print('访问失败')
        if fal:
            print('访问结束')


class IpPool():   # 获取免费代理ip
    def __init__(self):
        self.ip_pool = set()
        self.UserAgents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
            "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
            "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
            "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
            "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
            "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
            "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
            "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
            "Mozilla/5.0 (Windows; U; Windows NT 5.2) Gecko/2008070208 Firefox/3.0.1",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070309 Firefox/2.0.0.3",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070803 Firefox/1.5.0.12",
            "Opera/9.27 (Windows NT 5.2; U; zh-cn)",
            "Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/525.13 (KHTML, like Gecko) Version/3.1 Safari/525.13",
            "Mozilla/5.0 (iPhone; U; CPU like Mac OS X) AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/4A93 ",
            "Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.27 ",
            "Mozilla/5.0 (Linux; U; Android 3.2; ja-jp; F-01D Build/F0001) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13 ",
            "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_1 like Mac OS X; ja-jp) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.0.5 Mobile/8B117 Safari/6531.22.7",
            "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_2_1 like Mac OS X; da-dk) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5 ",
            "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_6; en-US) AppleWebKit/530.9 (KHTML, like Gecko) Chrome/ Safari/530.9 ",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Ubuntu/11.10 Chromium/27.0.1453.93 Chrome/27.0.1453.93 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36"
        ]
        for i in range(1, 8):
            url = 'http://www.ip3366.net/free/?stype=1&page=%d' % i
            ip_list = self.get_ip_list(url, headers=self.random_header(), proxies=None)
            self.ip_pool.update(ip_list)
        print("Ip pool has %d proxy ip"%len(self.ip_pool))

    def get_ip_list(self, url, headers, proxies):
        web_data = requests.get(url, headers=headers, proxies=proxies)
        soup = BeautifulSoup(web_data.text, 'lxml')
        ips = soup.find_all('tr')
        ip_list = []
        for i in range(1, len(ips)):
            ip_info = ips[i]
            tds = ip_info.find_all('td')
            ip_list.append(tds[0].text + ':' + tds[1].text)
        return ip_list

    def random_header(self):
        return {'User-Agent' : random.choice(self.UserAgents)}


    def get_one(self):
        return {'http': 'http://' + random.choice(list(self.ip_pool))}


# def run_(name_, su_):
#     for i in range(1, su_+1):
#         ip_pool = IpPool()
#         proxies = ip_pool.get_one()
#         # print("使用的代理ip为：", proxies)
#         # 如何调用该类
#         mycsdn = ScrapyMyCSDN(name_)  # 初始化类 参数为博客名
#         # print("初始访客量为"+":"+str(vs_0))
#         cur_write_nums = mycsdn.getOriginalArticalNums(
#             ip_pool.random_agent(), proxies, False)  # 得到写了多少篇文章
#
#         cur_blog_page = mycsdn.getScrapyPageNums(
#             cur_write_nums, False)  # cur_blog_page:返回需要爬取的页数
#         mycsdn.beginToScrapy(cur_blog_page, ip_pool.random_agent(), proxies, False)
#         time.sleep(random.random() * 1)  # 给它休息时间 还是怕被封号的


def run(threadName, name_, su_):
    #name_ = input("请输入您的csdn博客id:")
    #su_ = int(input("请输入您要刷的次数(这里的次数指博主您所有博客的访问次数，请注意我们只刷原创博客哦，支持原创！！！):"))
    while su_ >= 10000:
        print("刷访客量的行为可不好哦，请不要太贪心！！(号被封了可别哭)")
        su_ = int(input("请输入您要刷的次数(这里的次数指博主您所有博客的访问次数，请注意我们只刷原创博客哦，支持原创！！！):"))
    mycsdn = ScrapyMyCSDN(name_)

    #print("正在计算访客量，请勿关闭.......")
    #run_('nuoyanli', su_)  # 嘻嘻用我的代码就帮我也刷一下吧(据说好人一般都会取消这个注释)
    ip_pool = IpPool()

    while True:
        try:
            proxies = ip_pool.get_one()
            break
        except IndexError:
            time.sleep(5)

    global headers
    vs = mycsdn.get_vs(headers, proxies=proxies)
    time.sleep(5)
    failCnt = 0

    for i in range(1, su_+1):
        headers = ip_pool.random_header()
        print(f'{i} / {su_}')
        try:
            new_proxies = ip_pool.get_one()
            proxies = new_proxies
            failCnt = 0
        except IndexError:
            time.sleep(5)
            failCnt += 1
            if failCnt > 10:
                print('已经连续十次获取新代理失败，害怕被封号，所以停了')
                raise Exception


        #print("使用的代理ip为：", proxies)
        # 如何调用该类
        try:
            vs_0 = mycsdn.get_vs(headers, proxies)  # 初始访客量
            print(f"{threadName}访客量为"+":"+str(vs_0))
            cur_write_nums = mycsdn.getOriginalArticalNums(headers, proxies, False)  # 得到写了多少篇文章
            cur_blog_page = mycsdn.getScrapyPageNums(cur_write_nums, False)  # cur_blog_page:返回需要爬取的页数
            mycsdn.beginToScrapy(cur_blog_page, headers, proxies, False)
        except requests.exceptions:
            pass

        time.sleep(random.random()*20)  # 给它休息时间 还是怕被封号的

    vs_1 = mycsdn.get_vs(headers, proxies)  # 刷后的访客量
    print(f"{threadName}刷后的访客量"+":"+str(vs_1), end='')
    print(",增加了" + str(vs_1 - vs) + "的访客量")
    if vs_1 - vs > 0:
        print("哇有人悄悄访问了你的博客呢，快去看看是谁吧！")


def multi_thread():
    # 给自己刷访问量的同时也帮我刷刷吧，好人不会注释掉这一行的（反正是开的多线程，帮我刷也不会影响自己刷的效率哦）
    t0 = threading.Thread(target=run, args=(f'thread_-1', 'qq_43714612', su))
    t0.start()

    for i in range(5) :
        t = threading.Thread(target=run, args=(f'thread{i}', blogname, su))
        t.start()
        trd_list.append(t)



if __name__ == '__main__':
    trd_list = []
    blogname = 'qq_43714612'   # enter your blog name
    su = 100   # enter the times you want to visit for every thread and for every blog

    run('Debug', blogname, su)
    # multi_thread()



