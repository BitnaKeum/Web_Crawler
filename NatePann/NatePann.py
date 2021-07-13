from selenium import webdriver
from bs4 import BeautifulSoup
import time
import requests
import pandas as pd

start_date = '20210710' # 시작 날짜 입력
end_date = '20210712'   # 종료 날짜 입력


driver = webdriver.Chrome("./chromedriver")


# 글 링크 모으기 (하루 당 100개의 글)

url_list = []
for date in range(int(start_date), int(end_date)+1):
    for page in [1, 2]:
        url = f'https://pann.nate.com/talk/ranking/d?stdt={date}&page={page}'
        driver.get(url)
        time.sleep(0.3)

        src = driver.page_source
        html = BeautifulSoup(src, 'html.parser')
        tags = html.select('div.cntList dt a')

        for tag in tags:
            url_list.append('https://m.pann.nate.com'+tag.attrs['href'])


# 본문 및 댓글 크롤링

content_list = []  # 본문 리스트
comment_list = []  # 댓글 리스트

for url in url_list:
    # 페이지 접속
    page_id = url[-9:]
    driver.get(url)
    time.sleep(1)

    # 본문 가져오기
    src = driver.page_source
    html = BeautifulSoup(src, 'html.parser')
    tags = html.select('div.content')
    for tag in tags:
        content = tag.text
        content = content.replace('\n', ' ')
        content = content.replace('\t', '')
        content = content.replace('\xa0', '')
        if '이미지확대보기' in content:  # 이미지 첨부된 경우
            content = content.replace('이미지확대보기', '')
        content_list.append(content)

    # 댓글 버튼 누르기
    driver.find_element_by_xpath('//*[@id="contents"]/div[10]/div/a[1]').click()

    # 베스트 댓글
    src = driver.page_source
    html = BeautifulSoup(src, 'html.parser')
    tags = html.select('div.reply-best dd.userText')
    for tag in tags:
        best_comment = tag.text
        best_comment = best_comment.replace('\n', ' ')
        best_comment = best_comment.replace('\t', '')
        if '이미지확대보기' in best_comment:  # 이미지 첨부된 경우
            best_comment = best_comment.replace('이미지확대보기', '')
        comment_list.append(best_comment)

    # 일반 댓글
    reply_page = 1
    bef_tags = None
    while True:
        src = driver.page_source
        html = BeautifulSoup(src, 'html.parser')
        cur_tags = html.select('div#listDiv dd.userText')

        if bef_tags == cur_tags:  # 댓글 마지막 페이지
            break
        bef_tags = cur_tags

        for tag in cur_tags:
            comment = tag.text
            comment = comment.replace('\n', ' ')
            comment = comment.replace('\t', '')
            if '이미지확대보기' in comment:  # 이미지 첨부된 경우
                comment = comment.replace('이미지확대보기', '')
            comment_list.append(comment)

        # 댓글 다음 페이지로 이동
        reply_page += 1
        reply_url = f'https://m.pann.nate.com/talk/reply/view?pann_id={page_id}&order=N&rankingType=total&page={reply_page}'
        driver.get(reply_url)
        time.sleep(1)


# csv 파일로 저장

df = pd.DataFrame(content_list+comment_list, columns=["text"])

# UnicodeEncodeError 에러 발생 시 해당 문자열을 제거해줌
# df = df.applymap(lambda x: x.replace('오류난 문자열',''))

df.to_csv('./natepann.csv', mode = 'w', encoding='cp949')
