# -*- coding: utf-8 -*-

import collections
import json
import requests
import threading
import traceback


def get_online_json(url, max_retry_times=5):
    print('try to get online json')
    print('url:"{}"\nmax retry times:{}'.format(url, max_retry_times))
    retry_times = 1
    while (retry_times < max_retry_times + 1):
        try:
            print('try times:{}'.format(retry_times))
            stringContent = str(requests.get(url).content, 'utf-8')
            if stringContent != None and stringContent != '':
                online_json = json.loads(stringContent)
                retry_times = max_retry_times + 2
        except:
            retry_times = retry_times + 1
    print('get online json successful\n')
    return online_json


def merge_genshin_json(local_json, online_json):
    print('try to merge genshin json')
    local_json['pre_download_game'] = online_json['data']['pre_download_game']
    latest = online_json['data']['game']['latest']
    if local_json['latest'] != latest:
        deprecated_packages = local_json['deprecated_packages']
        deprecated_packages.append(local_json['latest'])
        local_json['latest'] = latest
    print('merge genshin json successful\n')
    return local_json


def get_genshin_json():
    print('try to get genshin json\n')
    genshin_url = 'https://sdk-static.mihoyo.com/hk4e_cn/mdk/launcher/api/resource?key=eYd89JmJ&launcher_id=18'
    online_json = get_online_json(genshin_url)
    local_path = 'README.md'
    with open(local_path, 'a+') as local_file:
        print('try to read local file')
        local_file.seek(0)
        try:
            local_json = json.loads(local_file.read().strip().strip('```'), object_pairs_hook=collections.OrderedDict)
        except:
            local_json = {'pre_download_game': '', 'latest': '', 'deprecated_packages': []}
        genshin_json = merge_genshin_json(local_json, online_json)
        local_file.seek(0)
        local_file.truncate()
        json_str = json.dumps(genshin_json, ensure_ascii=False, indent=4, separators=(',', ':'))
        print('try to write local file')
        local_file.write('```\n{}\n```'.format(json_str))
        print('get genshin json successful')


def git_update_workflows(workflows_path):
    with open(workflows_path, "r", encoding="utf-8") as f:
        workflows = f.read()
    import random
    import re
    import time
    m = random.randint(0, 59)
    h = random.randint(0, 8)
    cron = "cron: '{} {} * * *'".format(m, h)
    workflows = re.sub(r"cron: '\d+ \d+ \* \* \*'", cron, workflows)
    timestamp = time.strftime("%Y/%m/%d %H:%M:%S %Z", time.localtime())
    workflows = re.sub(r"# timestamp: .*", "# timestamp: {}".format(timestamp), workflows)
    with open(workflows_path, "w", encoding="utf-8") as f:
        f.write(workflows)


if __name__ == '__main__':
    try:
        t = threading.Thread(target=get_genshin_json)
        t.daemon = True
        t.start()
        t.join(timeout=300)
    except:
        print(traceback.format_exc())
    git_update_workflows(".github/workflows/workflow.yml")
