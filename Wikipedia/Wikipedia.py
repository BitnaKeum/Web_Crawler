import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd

title_list = []
content_list = []

iter = 0
while (1):
    # 랜덤 키워드
    url = 'https://ko.wikipedia.org/wiki/%ED%8A%B9%EC%88%98:%EC%9E%84%EC%9D%98%EB%AC%B8%EC%84%9C'

    response = requests.get(url)
    if response.status_code == requests.codes.ok:
        print(f"#{iter} 접속 성공")
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.select('h1#firstHeading')[0].text  # 제목(키워드) 가져오기
        title_list.append(title)

        tags = soup.select('p')  # 내용(본문) 가져오기
        contents = ''
        for tag in tags:
            text = tag.text
            text = text.replace('\n', '')
            contents += text
        content_list.append(contents)

        if iter % 10 == 0:  # 10번째마다 출력
            print('title: ', title)
            print(contents)
        iter += 1


        # csv 파일로 저장
        result = {'title': title_list, 'content': content_list}
        data = pd.DataFrame(result)
        data.to_csv("output.csv", index=False, encoding='utf-8-sig')

    else:
        print(f"#{iter} 접속 실패")
