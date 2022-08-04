import sys
import os
import datetime
import time
from collections import namedtuple
from jinja2 import Environment, FileSystemLoader
import urllib.request
from urllib.error import HTTPError
import json
import qrcode

print (sys.argv[0])
print (sys.argv[1])
print (sys.argv[2])

def url_request(url,token):
    print(url)
    try:
      request = urllib.request.Request(url)
      request.add_header('PROJECT_TOKEN',token)
      content = urllib.request.urlopen(request).read().decode('utf-8')
      json_content = json.loads(content)
    except HTTPError:
      print('Request to {url} failed'.format(url=url))
      json_content = None
    return json_content

def generate_qrcode(url,filename):
  qr = qrcode.QRCode(version=1,box_size=10,border=5)
  qr.add_data(url)
  qr.make(fit=True)
  img = qr.make_image(fill='black', back_color='white')
  filename = './public/{file}'.format(file=filename)
  img.save(filename)

def main():

    context_list = [] 
    file_date = None
    device = None
    file_size = None
    file=None
    ios_url=None
    base_url=None
    Row = namedtuple('Row','name file base_url device file_date file_size token pipeline_url pipeline_id qrcode')
    token = sys.argv[3]

    json_content = url_request("{url}?per_page=100".format(url=sys.argv[2]),token)
    
    if json_content is not None:
      for json_values in json_content:
          name = json_values['name']
          if json_values['_links']['delete_api_path']:
              package_url = '{package_url}/package_files?per_page=100'.format(package_url=json_values['_links']['delete_api_path'])
              json_package_values =  url_request(package_url,token)
              if json_package_values is not None:
                extensions=[]
                for package in json_package_values[::-1]:
                    if 'pipelines' in package:
                      if (package['file_name'] == 'manifest.plist' or package['file_name'].endswith(".apk")) and package['file_name'].split('.')[-1] not in extensions:
                          file = package['file_name']
                          file_size = round(int(package['size'])/(1024*1024),2)
                          file_date = package['pipelines'][0]['updated_at'].replace("T", " ").split('.')[0]
                          pipeline_url = package['pipelines'][0]['web_url']
                          pipeline_id = pipeline_url.split('/')[-1]
                          if file == "manifest.plist":
                            device = 'iOS'
                            ios_url = '{registry_url}/generic/{branch}/0.0.1'.format(registry_url=sys.argv[2],branch=name)
                            base_url = "itms-services://?action=download-manifest&url={baseurl}".format(baseurl=urllib.parse.quote(ios_url,safe=''))
                            url = '{base_url}%2F{name}%3Faccess_token%3D{token}'.format(base_url=base_url,name=file,token=token)
                            filename = 'ios_{branch}.png'.format(branch=name)
                            generate_qrcode(url,filename)
                            extensions.append('plist')
                          else:
                            device = 'Android'
                            base_url = '{registry_url}/generic/{branch}/0.0.1'.format(registry_url=sys.argv[2],branch=name)   
                            extensions.append('apk') 
                            url = '{base_url}/{name}?access_token={token}'.format(base_url=base_url,name=file,token=token)
                            filename = 'android_{branch}.png'.format(branch=name)
                            generate_qrcode(url,filename)
                          context_list.append(Row(name,file,base_url, device,file_date, file_size, token, pipeline_url, pipeline_id, filename))
                          extensions.append(package['file_name'].split('.')[-1])
      
    return context_list

if __name__ == '__main__':
    index_html_path = "./public/index.html"
    context_data = main()
    env = Environment(loader=FileSystemLoader("./"))
    template = env.get_template("index.jinja2")
    html = template.render(context_data = context_data)
    with open(index_html_path, "w") as fh:
      fh.write(html)
