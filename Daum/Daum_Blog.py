import requests
from bs4 import BeautifulSoup

keyword = '강아지'
total_page = 100
blog_type = 'daumsec' # 'tistory' or 'daumsec'


content_list = []  # 본문
comment_list = []  # 댓글/대댓글

for page in range(1, total_page + 1):
    url = f'https://search.daum.net/search?w=blog&enc=utf8&q={keyword}&f=section&SA={blog_type}&page={page}&DA=PGD'

    href_list = []
    response = requests.get(url)
    if response.status_code == requests.codes.ok:  # 연결 성공
        print(f'page {page} 접속 성공')
        html = BeautifulSoup(response.text, 'html.parser')
        tags = html.select('a.f_link_b')

        for tag in tags:
            href_list.append(tag.attrs['href'])  # 검색된 블로그의 링크 저장
        print(href_list)

        for href in href_list:
            response = requests.get(href)
            if response.status_code != requests.codes.ok:  # 연결 실패
                print(f'{href} 접속 실패')
                continue

            html = BeautifulSoup(response.text, 'html.parser')

            # 본문
            tags = html.select('div.tt_article_useless_p_margin p')
            for tag in tags:
                content = tag.text
                content = content.replace('\xa0', '')
                if content == '':
                    continue
                content_list.append(content)

            # 댓글/대댓글
            if blog_type == 'tistory':
                tags = html.select('div.comment-content')
            else:
                tags = html.select('p.text')
            for tag in tags:
                comment = tag.text
                comment = comment.replace('\r\n', '')
                comment = comment.replace('\n', ' ')
                comment_list.append(comment)

        if len(href_list) != 10:  # 마지막 페이지
            break


    else:
        print('접속 실패')


# csv 파일로 저장

import pandas as pd
import csv

content = pd.DataFrame({'content' : content_list})
content.to_csv("Daum_Blog_content.csv", index=False, encoding='utf-8-sig')

comment = pd.DataFrame({'comment' : comment_list})
comment.to_csv("Daum_Blog_comment.csv", index=False, encoding='utf-8-sig')
