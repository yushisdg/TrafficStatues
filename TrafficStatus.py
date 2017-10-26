
import requests
import json
import time
from pandas import DataFrame
import psycopg2

#请求高德实时路况数据
def getGaodeTrafficStatus(key,rectangle,currentTime):
    insert_list = []
    TrafficStatusUrl = 'http://restapi.amap.com/v3/traffic/status/rectangle?key='+key+'&rectangle='+rectangle+'&extensions=all';
    res = requests.get(url=TrafficStatusUrl).content;
    total_json = json.loads(res);
    print(total_json);
    trafficinfo=total_json.get('trafficinfo');
    if trafficinfo==None:
        print("无交通信息");
    else:
        jsondata = trafficinfo['roads'];
        print(jsondata);
        currentDate = time.strftime("%Y-%m-%d", time.localtime());
        if any(jsondata):
            for i in jsondata:
                name = i['name']
                status = i['status']
                direction = i['direction']
                angle = i['angle']
                speed = i.get('speed');
                # 若速度参数缺失，补为Null
                if speed == None:
                    speed = None;
                lcodes = i['lcodes']
                polyline = i['polyline']
                list = [name, status, direction, angle, lcodes, polyline, currentDate, currentTime, speed];
                insert_list.append(list);
            conn = psycopg2.connect(database="superpower", user="postgres", password="123456", host="localhost",
                                    port="5432");
            cur = conn.cursor();
            for i in insert_list:
                if len(i):
                    cur.execute(
                        "insert into gaode_date(name, status, direction, angle, lcodes, polyline, date, time,speed)  values (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        i)
                conn.commit()
            conn.close()
        else:
            pass


#注册多个高德key,轮流使用，并记录请求的个数，满2000次换下一个key继续请求。
keyList=[{}];
#建立覆盖研究区的rectangle数组
rectangleList=[];

key='c29be2081e00e4714273b6b49b398692';
    #'c29be2081e00e4714273b6b49b398692';
rectangle='120.12924,30.30185;120.16018,30.27150';
#请求整个杭州的区域


# #获取覆盖研究区域的网格

#
# #创建请求时间，确保一次请求的时间都相同


# getGaodeTrafficStatus(key,rectangle);

def getAllRegionGaodeData():
    conn = psycopg2.connect(database="superpower", user="postgres", password="123456", host="localhost", port="5432");
    cur = conn.cursor();
    cur.execute("select t.__xmin||','||t.ymin||';'||t.__xmax||','||t.ymax rectangle from hangzhou_grid t");
    rectangleData=cur.fetchall();
    cur.close;
    conn.close();
    currentTime = time.strftime("%H:%M:%S", time.localtime());  # 设置请求时间
    for rec in rectangleData:
        print(rec[0]);
        key=getOneKey();
        if key==None:
            print("没有可用key了，需要申请更多的账户");
        else:
            getGaodeTrafficStatus(key, rec[0], currentTime);
            afterRequest(key);



def getOneKey():
    currentDate = time.strftime("%Y-%m-%d", time.localtime());
    conn = psycopg2.connect(database="superpower", user="postgres", password="123456", host="localhost", port="5432");
    cur = conn.cursor();
    cur.execute("select KJ.key from (SELECT k.key, COALESCE((select j.request_count from gaode_keys j where j.date='" + currentDate + "' and j.key=k.key),0) request_count from (SELECT t.key from gaode_keys t GROUP BY t.key)  K) KJ  where KJ.request_count<1000");
    keyData = cur.fetchall();
    key=keyData[0][0];
    cur.close;
    conn.close();
    if key==None:
        print("没有可用key了，需要申请更多的账户");
    return key;

def afterRequest(key):
    currentDate = time.strftime("%Y-%m-%d", time.localtime());
    conn = psycopg2.connect(database="superpower", user="postgres", password="123456", host="localhost", port="5432");
    cur = conn.cursor();
    cur.execute("SELECT count(*) from gaode_keys t where t.key='"+key+"' and t.date='"+currentDate+"'");
    keyData = cur.fetchall();
    if keyData[0][0]==0:
        cur.execute(" INSERT INTO gaode_keys (key, date, request_count) VALUES('"+key+"','"+currentDate+"'"+",1)");
    else:
        cur.execute("UPDATE gaode_keys t set request_count=t.request_count+1 where t.key='"+key+"' and t.date='"+currentDate+"'");
    conn.commit();
    cur.close;
    conn.close();
    print(keyData[0][0]);

def timedTask(interval):
    a=1;
    while a==1:
        print(time.strftime("%H:%M:%S", time.localtime()));
        getAllRegionGaodeData();
        time.sleep(interval);


timedTask(60*5);




