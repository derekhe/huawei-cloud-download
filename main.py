import json
import os
from urllib.parse import urlparse

import browser_cookie3
import requests
import arrow

headers = {
    'Connection': 'keep-alive',
    'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
    'x-hw-account-brand-id': '0',
    'x-hw-device-manufacturer': 'HUAWEI',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36',
    'Content-Type': 'application/json;charset=UTF-8',
    'Accept': 'application/json, text/plain, */*',
    'x-hw-device-brand': 'HUAWEI',
    'Cache-Control': 'no-cache',
    'sec-ch-ua-mobile': '?0',
    'x-hw-app-brand-id': '1',
    'Origin': 'https://cloud.huawei.com',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://cloud.huawei.com/home',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6',
}

browser_cookies = browser_cookie3.chrome(domain_name="huawei.com")

cookies = {}
for c in browser_cookies:
    cookies[c.name] = c.value

headers['CSRFToken'] = cookies['CSRFToken']

s = requests.Session()
s.headers.update(headers)
s.cookies.update(cookies)

data = {"needRefresh": 0, "traceId": "04113_02_1595943080_87857589"}

response = s.post('https://cloud.huawei.com/album/galleryStatInfo', data=json.dumps(data))

gallery_stat_info = response.json()

total_files = gallery_stat_info['photoNum'] + gallery_stat_info['videoNum']
count = 500

with open("cmdlist.sh", "wt", newline="\n") as f:
    for i in range(0, total_files, count):
        data = {"albumId": None, "currentNum": i, "count": count, "type": None,
                "traceId": "04118_02_1595940145_34834964"}
        file_list = s.post('https://cloud.huawei.com/album/getSimpleFile', data=json.dumps(data)).json()['fileList']
        image_files = [{"albumId": image_file['albumId'], "uniqueId": image_file['uniqueId']} for image_file in
                       file_list]

        data = {"fileList": image_files, "ownerId": None, "traceId": "04101_02_1595940148_21875898"}
        file_list = s.post('https://cloud.huawei.com/album/queryCloudFileName', data=json.dumps(data)).json()[
            'fileList']

        file_creation_time = {}
        for afile in file_list:
            file_creation_time[afile['uniqueId']] = afile['createTime']

        image_file_names = [
            {"albumId": image_file['albumId'], "uniqueId": image_file['uniqueId'], "fileName": image_file['fileName']}
            for
            image_file in file_list]

        data = {"fileList": image_file_names, "type": "0", "ownerId": None, "traceId": "04101_02_1595941545_61344217"}

        url_list = s.post('https://cloud.huawei.com/album/getSingleUrl', data=json.dumps(data)).json()['urlList']

        for url_detail in url_list:
            url = url_detail['url']
            file_name = os.path.basename(urlparse(url).path)
            creation_time = file_creation_time[url_detail['uniqueId']]
            folder_name = str(arrow.get(creation_time / 1000).date())
            output = f'mkdir -p {folder_name} && wget --timeout=1800 -c -O {folder_name}/{file_name} "{url}"'
            f.write(output + '\n')
            print(output)
        print("Progress", i / total_files * 100)
