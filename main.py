import argparse
import json
import os
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from urllib.parse import urlparse

import arrow
import browser_cookie3
import requests
from retrying import retry

from constants import headers


@dataclass
class FileToDownload:
    url: str
    path: str


def setup_session():
    try:
        browser_cookies = browser_cookie3.chrome(domain_name="huawei.com")
        cookies = {}
        for c in browser_cookies:
            cookies[c.name] = c.value
        headers['CSRFToken'] = cookies['CSRFToken']
        s = requests.Session()
        s.headers.update(headers)
        s.cookies.update(cookies)
        return s
    except Exception as ex:
        print("请用chrome到cloud.huawei.com登陆并进入相册程序后关闭浏览器")
        exit(-1)


def get_files_to_download(root_folder):
    data = {"needRefresh": 0, "traceId": "04113_02_1595943080_87857589"}
    response = session.post('https://cloud.huawei.com/album/galleryStatInfo', data=json.dumps(data))

    gallery_stat_info = response.json()

    total_files = gallery_stat_info['photoNum'] + gallery_stat_info['videoNum']
    count = 500
    with ThreadPoolExecutor() as exec:
        for i in range(0, total_files, count):
            print(f"Getting file list from count = {i}")
            data = {"albumId": None, "currentNum": i, "count": count, "type": None,
                    "traceId": "04118_02_1595940145_34834964"}
            file_list = session.post('https://cloud.huawei.com/album/getSimpleFile', data=json.dumps(data), timeout=120).json()['fileList']

            image_files = [{"albumId": image_file['albumId'], "uniqueId": image_file['uniqueId']} for image_file in
                           file_list]
            data = {"fileList": image_files, "ownerId": None, "traceId": "04101_02_1595940148_21875898"}
            cloud_file_names = session.post('https://cloud.huawei.com/album/queryCloudFileName', data=json.dumps(data), timeout=120).json()[
                'fileList']

            file_creation_time = {}
            for a_file in cloud_file_names:
                file_creation_time[a_file['uniqueId']] = a_file['createTime']

            image_file_names = [{"albumId": image_file['albumId'], "uniqueId": image_file['uniqueId'], "fileName": image_file['fileName']} for image_file in file_list]
            data = {"fileList": image_file_names, "type": "0", "ownerId": None, "traceId": "04101_02_1595941545_61344217"}

            url_list = session.post('https://cloud.huawei.com/album/getSingleUrl', data=json.dumps(data), timeout=120).json()['urlList']

            for url_detail in url_list:
                url = url_detail['url']
                file_name = os.path.basename(urlparse(url).path)
                creation_time = file_creation_time[url_detail['uniqueId']]
                folder_name = str(arrow.get(creation_time / 1000).date())

                download_path = os.path.join(root_folder, folder_name, file_name)

                if os.path.exists(download_path):
                    # print(f"{download_path} exist, skip")
                    continue

                exec.submit(download, FileToDownload(url=url, path=download_path))


@retry(stop_max_attempt_number=3)
def download(file: FileToDownload):
    try:
        print("Downloading", file.path)
        dir = os.path.dirname(file.path)
        os.makedirs(dir, exist_ok=True)

        temp_file = file.path + ".tmp"

        r = session.get(file.url, stream=True, timeout=60 * 60)
        r.raise_for_status()
        with open(temp_file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        os.rename(temp_file, file.path)

        print("Finished", file.path)
    except Exception as ex:
        print(ex)
        raise ex


if __name__ == "__main__":
    session = setup_session()
    parser = argparse.ArgumentParser()
    parser.add_argument('folder', metavar='folder', type=str, help='Where to store the downloaded files')
    args = parser.parse_args()

    print("Getting files to download")
    get_files_to_download(args.folder)
