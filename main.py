import argparse
import json
import os
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from urllib.parse import urlparse

import browser_cookie3
import requests
import arrow
import wget

from constants import headers


@dataclass
class FileToDownload:
    url: str
    path: str


def setup_session():
    browser_cookies = browser_cookie3.chrome(domain_name="huawei.com")
    cookies = {}
    for c in browser_cookies:
        cookies[c.name] = c.value
    headers['CSRFToken'] = cookies['CSRFToken']
    s = requests.Session()
    s.headers.update(headers)
    s.cookies.update(cookies)
    return s


def get_files_to_download(root_folder):
    session = setup_session()

    data = {"needRefresh": 0, "traceId": "04113_02_1595943080_87857589"}
    response = session.post('https://cloud.huawei.com/album/galleryStatInfo', data=json.dumps(data))

    gallery_stat_info = response.json()

    total_files = gallery_stat_info['photoNum'] + gallery_stat_info['videoNum']
    count = 500

    files_to_download = []
    for i in range(0, total_files, count):
        data = {"albumId": None, "currentNum": i, "count": count, "type": None,
                "traceId": "04118_02_1595940145_34834964"}
        file_list = session.post('https://cloud.huawei.com/album/getSimpleFile', data=json.dumps(data)).json()['fileList']

        image_files = [{"albumId": image_file['albumId'], "uniqueId": image_file['uniqueId']} for image_file in
                       file_list]
        data = {"fileList": image_files, "ownerId": None, "traceId": "04101_02_1595940148_21875898"}
        cloud_file_names = session.post('https://cloud.huawei.com/album/queryCloudFileName', data=json.dumps(data)).json()[
            'fileList']

        file_creation_time = {}
        for a_file in cloud_file_names:
            file_creation_time[a_file['uniqueId']] = a_file['createTime']

        image_file_names = [{"albumId": image_file['albumId'], "uniqueId": image_file['uniqueId'], "fileName": image_file['fileName']} for image_file in file_list]
        data = {"fileList": image_file_names, "type": "0", "ownerId": None, "traceId": "04101_02_1595941545_61344217"}

        url_list = session.post('https://cloud.huawei.com/album/getSingleUrl', data=json.dumps(data)).json()['urlList']

        for url_detail in url_list:
            url = url_detail['url']
            file_name = os.path.basename(urlparse(url).path)
            creation_time = file_creation_time[url_detail['uniqueId']]
            folder_name = str(arrow.get(creation_time / 1000).date())

            download_path = os.path.join(root_folder, folder_name, file_name)

            if os.path.exists(download_path):
                # print(f"{download_path} exist, skip")
                continue

            files_to_download.append(FileToDownload(url=url, path=download_path))

        print(f"{len(files_to_download)} added")

    return files_to_download


def download(file: FileToDownload):
    try:
        print("Downloading", file)
        dir = os.path.dirname(file.path)
        os.makedirs(dir, exist_ok=True)
        wget.download(file.url, file.path)
        print("Finished", file)
    except Exception as ex:
        print(ex)


def download_files(files_to_download):
    with ThreadPoolExecutor(max_workers=32) as exec:
        for file in files_to_download:
            exec.submit(download, file)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('folder', metavar='folder', type=str, help='Where to store the downloaded files')
    args = parser.parse_args()

    print("Getting files to download")
    files = get_files_to_download(args.folder)

    print("Total files to download", len(files))
    download_files(files)
