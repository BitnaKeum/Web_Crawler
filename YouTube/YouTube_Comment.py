#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


# 특정 키워드에 대한 영상들의 url을 저장하는 함수
def video_url_crawling():
    data = []
    keyword = input('Keyword : ')

    driver = webdriver.Chrome('./chromedriver.exe')
    driver.maximize_window()

    YOUTUBE_URL = f'https://www.youtube.com/results?search_query={keyword}&sp=CAM%253D'
    driver.get(YOUTUBE_URL)

    print('The scrolling starts moving to the bottom of the main page.')
    body = driver.find_element_by_tag_name("body")

    while True:
        body.send_keys(Keys.PAGE_DOWN)  # 스크롤 다운
        time.sleep(0.4)

        items = driver.find_elements_by_css_selector('#message')  # id = '#message' 에 해당하는 값을 가져옴
        if items[0].text == "결과가 더 이상 없습니다.":  # scroll을 맨 끝까지 내렸을 때 message의 내용
            break  # 반복문 탈출

    print('Arrived at the end of the main page')
    print('Start to get the url of the video')

    # 동영상 제목, url을 가지고 있는 class를 가져옴.
    items = driver.find_elements_by_css_selector('#video-title')

    for idx in items:
        if (idx.get_attribute('href') is not None):
            # 한글 깨짐 방지
            text = idx.text

            for i in range(len(text)):
                if not ((0 <= ord(text[i]) < 128) or (0xac00 <= ord(text[i]) <= 0xd7af)):
                    text = text.replace(text[i], ' ')
            data.append([text, idx.get_attribute('href')])

    driver.close()

    print('Finish previous working')
    print('The data is being written to the csv file.')

    # csv 파일에 저장 [동영상 제목, 동영상 url]
    dataframe = pd.DataFrame(data, columns=["title", "url"])
    dataframe.to_csv('./youtube_url_collection.csv', mode='a', encoding='cp949')

    print('Finish working')


# csv파일에 저장된 영상 url를 이용해 댓글을 크롤링하는 함수
def video_comment_crawling():
    data = []
    df = pd.read_csv('./youtube_url_collection.csv', encoding='cp949')

    driver = webdriver.Chrome('./chromedriver.exe')
    driver.maximize_window()

    temporary_storage_num = 1
    for i in range(len(df.index)):
        title = df['title'][i]
        link = df['url'][i]

        print(f'Start comment crawling : title = {title}')

        driver.get(link)
        time.sleep(3)

        count = 0
        body = driver.find_element_by_tag_name("body")

        # 댓글 데이터를 가져옴
        last = driver.find_elements_by_css_selector('#content-text')

        while True:
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.4)

            # 자세히 보기 클릭
            #             exp_div.find_elements_by_xpath('//*[@id="more"]/span')[iteration].click()
            #             time.sleep(0.2)

            # 댓글 내용
            new = driver.find_elements_by_css_selector('#content-text')

            # 답글 보기 클릭
            #             driver.find_element_by_xpath('//*[@id="more-replies"]/a').click()
            #             time.sleep(1)

            # 답글 내용
            #             reply_div = driver.find_element_by_id('expander-contents')
            #             reply1 = reply_div.find_elements_by_css_selector('#content-text')

            # 답글 더보기 클릭 및 마지막 답글까지 스크롤
            #             while True:
            #                 try:
            #                     driver.find_element_by_xpath('//*[@id="button"]/ytd-button-renderer/a').click() # 답글 더보기 클릭
            #                     time.sleep(3)
            #                 except:
            #                     print("답글 끝!")
            #                     body.send_keys(Keys.PAGE_DOWN)
            #                     time.sleep(0.4)
            #                     body.send_keys(Keys.PAGE_DOWN)
            #                     time.sleep(0.4)
            #                     break

            if new == last:
                if count == 10:  # 마지막 댓글인 경우
                    break
                count += 1
            else:
                count = 0

            last = new

        for idx in new:
            # 한글 깨짐 방지
            text = idx.text

            for idx in range(len(text)):
                if not ((0 <= ord(text[idx]) < 128) or (0xac00 <= ord(text[idx]) <= 0xd7af)):
                    text = text.replace(text[idx], ' ')

            data.append([title, text])

        if temporary_storage_num == 1:
            dataframe = pd.DataFrame(data, columns=["title", "content"])
            dataframe.to_csv('./youtube_comment.csv', mode='a', encoding='cp949')
            data = []

        if temporary_storage_num % 3 == 0:
            dataframe = pd.DataFrame(data, columns=["title", "content"])
            dataframe.to_csv('./youtube_comment.csv', mode='a', encoding='cp949', header=False)
            data = []

        temporary_storage_num += 1

    driver.close()
    print('Finish comment crawling')

    # 댓글 데이터를 csv 파일에 저장
    dataframe = pd.DataFrame(data, columns=["title", "content"])
    dataframe.to_csv('./youtube_comment.csv', mode='a', encoding='cp949')

    print('Finish working')


if __name__ == '__main__':
    video_url_crawling()  # 키워드에 대한 영상들의 url 저장
    video_comment_crawling()  # url에 접속하여 댓글들 가져옴
