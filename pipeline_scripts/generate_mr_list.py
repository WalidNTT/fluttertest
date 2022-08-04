import requests
import sys
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def format_mr(mr):
    return "!{}: {} by {}".format(mr['iid'],mr['title'],mr['author']['name'])

id=157

if len(sys.argv)!=5:
    print("Usage: {} tag tag_date(ex: 2017-12-22) token branch".format(sys.argv[0]))
    print("Warning: a maximum of 1000 merge requests will be returned")

    exit(1)

milestone = sys.argv[1]
last_release_date = sys.argv[2]
private_token = sys.argv[3]
branch = sys.argv[4]

# Merge Requests with milestone M.m.p
req="https://gitlab-tooling.dsp.intdigital.ee.co.uk/api/v4/projects/157/merge_requests?scope=all&per_page=1000&state=merged&milestone={}".format(milestone)
headers = {'PRIVATE-TOKEN': private_token}
r = requests.get(req,verify=False, headers=headers)
data = json.loads(r.text)

#Merge Requests merged in develop after branching to last release
req="https://gitlab-tooling.dsp.intdigital.ee.co.uk/api/v4/projects/157/merge_requests?scope=all&per_page=1000&state=merged&target_branch={}&updated_after={}".format(branch,last_release_date)
headers = {'PRIVATE-TOKEN': private_token}
r = requests.get(req,verify=False, headers=headers)
data+=json.loads(r.text)


data = sorted(data, key=lambda data: data['iid'])

mr_list = []

ids=set()

for mr in data:
    if mr['iid'] not in ids:
            mr_list.append(mr)
    ids.add(mr['iid'])

print("Changes in this release:")

for mr in mr_list:
    print("   * "+format_mr(mr))
