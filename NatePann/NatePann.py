import requests
from bs4 import BeautifulSoup
import time

start_date = '20130101'   # 시작 날짜 입력
end_date   = '20130102'   # 종료 날짜 입력


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

# 약간의 전처리
def preprocessing(text):
    text = text.replace('\n', ' ')
    text = text.replace('\t', '')
    if '이미지확대보기' in text: # 이미지 첨부된 경우
        text = text.replace('이미지확대보기', '')
    return text


# 본문 및 댓글 크롤링
def Crawling(url_list):
    content_list = []  # 본문 리스트
    reply_list = []  # 댓글 리스트
    subreply_list = []  # 대댓글 리스트

    for url in url_list:
        # 페이지 접속
        pann_id = url[-9:]
        response = requests.get(url)
        time.sleep(1)
        if response.status_code != requests.codes.ok:  # 접속 실패
            print(f"{url} 접속 실패")
            continue

        # 본문
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

        # 댓글
        reply_page = 1
        bef_reply_text = None
        while True:
            # 웹 버전에서는 댓글 페이지가 동적이어서 모바일 버전으로 가져옴
            # 그럼 아예 모바일 버전으로 하면 되지 않나요? -> 모바일 버전에서는 댓글을 보려면 댓글 버튼을 눌러야해서 selenium 필요 ^^;
            reply_url = f'https://m.pann.nate.com/talk/reply/view?pann_id={pann_id}&page={reply_page}'
            response = requests.get(reply_url)
            time.sleep(0.5)
            if response.status_code != requests.codes.ok:  # 접속 실패
                print(f"{reply_url} 접속 실패")
                continue

            # 현재 댓글 페이지에 나온 댓글들의 id 저장
            reply_id_list = []
            html = BeautifulSoup(response.text, 'html.parser')
            cur_reply_href = html.select('div#listDiv dl dt a')
            for href_tag in cur_reply_href:
                href = href_tag.attrs['href']
                reply_id = href[-9:]
                reply_id_list.append(reply_id)

            # 댓글 내용 저장
            cur_reply_text = []
            cur_reply_text = html.select('div#listDiv dd.userText')
            if bef_reply_text == cur_reply_text:  # 댓글 마지막 페이지
                break
            bef_reply_text = cur_reply_text

            for idx, text_tag in enumerate(cur_reply_text):
                reply = preprocessing(text_tag.text)
                reply_list.append(reply)

                # 대댓글
                reply_id = reply_id_list[idx]
                subreply_page = 1
                bef_subreply_text = None
                subreply_temp_list = []
                while True:
                    subreply_url = f'https://m.pann.nate.com/talk/reply/subReply?pann_id={pann_id}&prts_reply_id={reply_id}&page={subreply_page}'
                    response = requests.get(subreply_url)
                    time.sleep(0.5)
                    if response.status_code != requests.codes.ok:  # 접속 실패
                        print(f"{subreply_url} 접속 실패")
                        continue

                    html = BeautifulSoup(response.text, 'html.parser')
                    cur_subreply_text = html.select('div#listDiv dd.userText em')
                    if bef_subreply_text == cur_subreply_text:  # 대댓글 마지막 페이지
                        break
                    bef_subreply_text = cur_subreply_text

                    for text_tag in cur_subreply_text:
                        subreply = preprocessing(text_tag.text)
                        subreply_temp_list.append(subreply)

                    subreply_page += 1

                subreply_list.append(subreply_temp_list)

            reply_page += 1

    return content_list, reply_list, subreply_list

# reply_list와 subreply_list는 인덱스에 따라 대응함
# subreply_list[0]이 ['a','b','c']라면, reply_list[0] 댓글에 3개의 대댓글이 달린 것



if __name__ == '__main__':
    url_list = Get_url()
    content_list, reply_list, subreply_list = Crawling(url_list)