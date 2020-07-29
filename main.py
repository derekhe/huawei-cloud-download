import json
from pprint import pprint

import requests
from urllib.parse import urlparse
import os

from session import headers, cookies

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
        data = {"albumId": None, "currentNum": i, "count": count, "type": None, "traceId": "04118_02_1595940145_34834964"}
        file_list = s.post('https://cloud.huawei.com/album/getSimpleFile', data=json.dumps(data)).json()['fileList']
        image_files = [{"albumId": image_file['albumId'], "uniqueId": image_file['uniqueId']} for image_file in file_list]

        data = {"fileList": image_files, "ownerId": None, "traceId": "04101_02_1595940148_21875898"}
        file_list = s.post('https://cloud.huawei.com/album/queryCloudFileName', data=json.dumps(data)).json()['fileList']
        image_file_names = [
            {"albumId": image_file['albumId'], "uniqueId": image_file['uniqueId'], "fileName": image_file['fileName']} for
            image_file in file_list]

        data = {"fileList": image_file_names, "type": "0", "ownerId": None, "traceId": "04101_02_1595941545_61344217"}

        url_list = s.post('https://cloud.huawei.com/album/getSingleUrl', data=json.dumps(data)).json()['urlList']

        for url_detail in url_list:
            url = url_detail['url']
            file_name = os.path.basename(urlparse(url).path)
            output = f'wget -c -O {file_name} "{url}"'
            f.write(output + '\n')
            print(output)
        print("Progress", i / total_files * 100)