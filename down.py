import time
import urllib.request
from urllib.request import urlopen
import requests
import zipfile
import io
import pandas as pd
import os
import cherrypy
from jinja2 import Environment, FileSystemLoader
import redis
def download():
 timestr = time.strftime("EQ%d%m%y_CSV.ZIP")
 print (timestr)
 urllib.request.urlretrieve('https://www.bseindia.com/download/BhavCopy/Equity/'+timestr, 'zerodha.zip')
 target = 'zerodha.zip'
 handle = zipfile.ZipFile(target)
 handle.extractall()
 return handle.namelist()[0]

def redisdb(yolo):
    csv = pd.read_csv(yolo)
    csv = csv[['SC_CODE', 'SC_NAME', 'OPEN', 'HIGH', 'LOW', 'CLOSE']].copy()
    for index, row in csv.iterrows():
        r.hmset(row['SC_CODE'], row.to_dict())
        r.set("equity:"+row['SC_NAME'], row['SC_CODE'])


class WebApp:
    @cherrypy.expose
    def index(self, search=""):

        html_file = env.get_template('index.html')
        self.result = []
        for key in r.scan_iter("equity:*"):
            code = r.get(key)
            self.result.append(r.hgetall(code).copy())
        self.result = self.result[0:10]
        return html_file.render(result=self.result)


if __name__ == '__main__':
    yolo = download()
    r = redis.StrictRedis(host="localhost", port=6379, decode_responses=True, db=1)
    redisdb(yolo)
    env = Environment(loader=FileSystemLoader('data'))
    config = {'global': {'server.socket_host':  '0.0.0.0',
                'server.socket_port':  int(os.environ.get('PORT', '1234'))}}
    cherrypy.quickstart(WebApp(), config=config)
