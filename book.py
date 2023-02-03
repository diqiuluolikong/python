# -*- coding: UTF-8 -*-
import os
import re

import requests as t
from fake_useragent import UserAgent
from lxml import etree


def link(url, retry_time=5):
    while retry_time:
        headers = {
            'User-Agent': UserAgent().random}
        retry_time -= 1
        try:
            content = t.get(url, headers=headers)
            content.encoding = 'utf-8'
            key = re.findall('[\u4e00-\u9fa5]{3,}', content.text)
            if not key:
                content.encoding = 'gbk'
            content_text = content.text
            if content_text and content.status_code == 200:
                return content.text
        except Exception as e:
            print(e)
        if not retry_time:
            return


def crawl_detail(curr_path, unit_name, unit_href, max_num):
    if unit_href.startswith('//'):
        de_href = 'https:' + unit_href
    elif unit_href.startswith('/'):
        de_href = domain + unit_href
    else:
        de_href = unit_href
    de_infos = '\n'.join(etree.HTML(link(de_href)).xpath('//*[@id="content"]//text()'))
    de_infos = re.sub('亲,点击进去,给个好评呗,分数越高更新越快.*', '', de_infos, re.S)
    de_infos = re.sub('手机站全新改版升级.*', '', de_infos, re.S)
    with open(os.path.join(curr_path, f'{max_num}@##%' + unit_name + '.txt'), 'w', encoding='utf-8') as fa:
        fa.write(de_infos)


def crawl_unit(xs_title, curr_path, xs_href):
    if xs_href.startswith('//'):
        xq_href = 'https:' + xs_href
    elif xs_href.startswith('/'):
        xq_href = domain + xs_href
    else:
        xq_href = xs_href
    xq_html = link(xq_href)
    unit_ports = etree.HTML(xq_html).xpath('//*[@id="list"]//dd/a')
    file_list = os.listdir(curr_path)
    try:
        max_num = max([eval(i.split('：')[0]) for i in file_list])
    except: max_num = 0
    unit_name_list = ['：'.join(i.split('@##%')[1:]).strip('.txt') for i in file_list]
    print(f'小说：{xs_title}，共计：{len(unit_ports)} 个章节信息！')
    for index, unit in enumerate(unit_ports):
        unit_name = ''.join(unit.xpath('.//text()')).strip().replace('\n', ' ').replace('/', ' ')
        unit_href = unit.xpath('./@href')[0]
        if unit_name not in unit_name_list:
            max_num += 1
            unit_name_list.append(unit_name)
            print(f'抓取小说：{xs_title} 的 {unit_name} 章节！')
            crawl_detail(curr_path, unit_name, unit_href, max_num)
            print(f'{unit_name} 章节抓取完成!')


def shuming():
    root_page = link(root_url)
    xs_list = etree.HTML(root_page).xpath('//*[@id="main"]//ul/li/a')
    for xs_port in xs_list[:eval(limit_)]:
        xs_title = ''.join(xs_port.xpath('.//text()')).strip().replace('\n', ' ').replace('/', ' ')
        xs_href = xs_port.xpath('./@href')[0]
        print(f'抓取小说：{xs_href}，标题：{xs_title}')
        curr_path = os.path.join(root_dir, xs_title)
        try:
            os.makedirs(curr_path)
        except: pass
        crawl_unit(xs_title, curr_path, xs_href)


if __name__ == '__main__':
    print('开始小说抓取任务。请在下方输入相关参数，然后开始抓取任务！\n')
    root_dir = 'book'
    limit_ = input('请输入抓取小说数量：').strip()
    # limit_ = '100'
    root_url = input('请输入小说网址：').strip()
    # root_url = 'https://www.xbiquge.la/xiaoshuodaquan/'
    # root_url = 'https://www.xxbiqudu.com/xiaoshuodaquan/'
    domain = '/'.join(root_url.split('/')[:-2])
    shuming()
    print(f'本次以完成：{limit_} 篇小说的采集，退出程序只需要关闭窗口即可！')


