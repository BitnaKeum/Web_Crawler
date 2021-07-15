import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

start_date = '20210710' # 시작 날짜 입력
end_date = '20210712'   # 종료 날짜 입력


# 글 링크 모으기 (하루 당 100개의 글 존재)
def Get_url():
    url_list = []
    for date in range(int(start_date), int(end_date) + 1):
        for page in [1, 2]:
            url = f'https://pann.nate.com/talk/ranking/d?stdt={date}&page={page}'
            response = requests.get(url)
            time.sleep(0.3)
            if response.status_code != requests.codes.ok:  # 접속 실패
                print("접속 실패")
                continue

            html = BeautifulSoup(response.text, 'html.parser')
            tags = html.select('div.cntList dt a')

            for tag in tags:
                url_list.append('https://pann.nate.com' + tag.attrs['href'])

    return url_list


# 본문 및 댓글 크롤링
def Crawling(url_list):
    content_list = []  # 본문 리스트
    comment_list = []  # 댓글 리스트

    for url in url_list:
        # 페이지 접속
        page_id = url[-9:]
        response = requests.get(url)
        time.sleep(1)
        if response.status_code != requests.codes.ok:  # 접속 실패
            print(f"{url} 접속 실패")
            continue

        # 본문 가져오기
        html = BeautifulSoup(response.text, 'html.parser')
        tags = html.select('div#contentArea')
        for tag in tags:
            content = tag.text
            content = content.replace('\n', ' ')
            content = content.replace('\t', '')
            content = content.replace('\xa0', '')
            if '이미지확대보기' in content:  # 이미지 첨부된 경우
                content = content.replace('이미지확대보기', '')
            content_list.append(content)

        #     # 베스트 댓글 (일반 댓글과 중복됨)
        #     tags = html.select('div.cmt_best dd.usertxt span')
        #     for tag in tags:
        #         best_comment = tag.text
        #         best_comment = best_comment.replace('\n', ' ')
        #         best_comment = best_comment.replace('\t', '')
        #         if '이미지확대보기' in best_comment: # 이미지 첨부된 경우
        #             best_comment = best_comment.replace('이미지확대보기', '')
        #         comment_list.append(best_comment)

        # 일반 댓글
        reply_page = 1
        bef_tags = None
        while True:
            # 웹 버전에서는 댓글 페이지가 동적이어서 모바일 버전으로 가져옴
            # 그럼 아예 모바일 버전으로 하면 되지 않나요? -> 모바일 버전에서는 댓글을 보려면 댓글 버튼을 눌러야해서 selenium 필요 ^^;
            reply_url = f'https://m.pann.nate.com/talk/reply/view?pann_id={page_id}&page={reply_page}'
            response = requests.get(reply_url)
            time.sleep(0.5)
            if response.status_code != requests.codes.ok:  # 접속 실패
                print(f"{reply_url} 접속 실패")
                continue

            html = BeautifulSoup(response.text, 'html.parser')
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

            reply_page += 1

    return content_list, comment_list


# csv 파일로 저장
def Save_csv(content_list, comment_list):
    df = pd.DataFrame(content_list+comment_list, columns=["text"])

    # UnicodeEncodeError 에러 발생 시 해당 문자열을 제거해줌
    # df = df.applymap(lambda x: x.replace('오류난 문자열',''))

    df.to_csv('./natepann.csv', mode = 'w', encoding='cp949')


if __name__ == '__main__':
    url_list = Get_url()
    content_list, comment_list = Crawling(url_list)
    Save_csv(content_list, comment_list)