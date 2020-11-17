import requests
from requests.auth  import HTTPBasicAuth
import subprocess
import time
import json

def send_request(url, auth):
    return requests.get(url,
                        auth=auth,
                        headers={'Accept': 'application/json'}
                    ).json()
with open('user.json') as user_file:
    with open('mob.json') as mob_file:
        user_info = json.load(user_file)
        auth = HTTPBasicAuth(user_info['username'], user_info['password'])
        mob = set(json.load(mob_file))
        found_keys = set()
        while True:
            failed_build = send_request('https://bamboo.eurekanetwork.org/rest/api/latest/result/EPMP?buildstate=failed', auth)['results']['result']
            for build in failed_build:
                authors = set()
                plan_data = send_request(build['link']['href'] + '?expand=changes', auth)
                changes =  plan_data['changes']['change']
                key = plan_data['planResultKey']['key']
                if key not in found_keys:
                    found_keys.add(key)
                    for change in changes:
                        if 'fullName' in change:
                            authors.add(change['fullName'])
                    if len(authors.intersection(mob)) > 0:
                        subprocess.run(['terminal-notifier',
                            '-title',
                            'Bamboo failure',
                            '-message',
                            'You have a failing build (Click to view)',
                            '-open', 'https://bamboo.eurekanetwork.org/browse/' + key,
                            '-sound',
                            'Submarine',
                            '-subtitle',
                            plan_data['plan']['shortName']]
                        )
            time.sleep(30)
            