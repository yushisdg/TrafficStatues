import requests
import json
import time
from pandas import DataFrame
import psycopg2


# 获取可用key值
def getUseableKey(conn, cur):
    currentDate = time.strftime("%Y-%m-%d", time.localtime());
    sql = "select KJ.key from (SELECT k.key, COALESCE((select j.request_count from gaode_keys j where j.date='" + currentDate + "' and j.key=k.key),0) request_count from (SELECT t.key from gaode_keys t GROUP BY t.key)  K) KJ  where KJ.request_count<1000";
    cur.execute(sql);
    keyData = cur.fetchall();
    key = keyData[0][0];
    if key == None:
        print("没有可用key了，需要申请更多的账户");
    return key;


# 获取研究区域网格
def getRegionRectangles(conn, cur):
    cur.execute("select t.__xmin||','||t.ymin||';'||t.__xmax||','||t.ymax rectangle from hangzhou_grid t");
    rectangleData = cur.fetchall();
    return rectangleData;


# 记录key值使用情况
def OneKeyAfterRequest(conn, cur, key, currentDate):
    cur.execute("SELECT count(*) from gaode_keys t where t.key='" + key + "' and t.date='" + currentDate + "'");
    keyData = cur.fetchall();
    if keyData[0][0] == 0:
        cur.execute(
            " INSERT INTO gaode_keys (key, date, request_count) VALUES('" + key + "','" + currentDate + "'" + ",1)");
    else:
        cur.execute(
            "UPDATE gaode_keys t set request_count=t.request_count+1 where t.key='" + key + "' and t.date='" + currentDate + "'");
    conn.commit();


# 向高德请求数据
def requestGaodeTrafficDate(conn, cur, key, currentDate, rec, currentTime):
    insert_list = []
    TrafficStatusUrl = 'http://restapi.amap.com/v3/traffic/status/rectangle?key=' + key + '&rectangle=' + rec[
        0] + '&extensions=all';
    res = requests.get(url=TrafficStatusUrl).content;
    # 记录key使用情况
    OneKeyAfterRequest(conn, cur, key, currentDate)
    total_json = json.loads(res);
    print(total_json);
    trafficinfo = total_json.get('trafficinfo');
    if trafficinfo == None:
        print(rec[0] + "无交通信息");
    else:
        jsondata = trafficinfo['roads'];
        currentDate = time.strftime("%Y-%m-%d", time.localtime());
        if any(jsondata):
            for i in jsondata:
                name = i.get('name')
                status = i.get('status')
                direction = i.get('direction')
                angle = i.get('angle')
                speed = i.get('speed');
                # 若速度参数缺失，补为Null
                if speed == None:
                    speed = "10000";
                lcodes = i.get('lcodes')
                polyline = i.get('polyline')
                list = [name, status, direction, angle, lcodes, polyline, currentDate, currentTime, speed];
                insert_list.append(list);
            insertSql = "";
            for i in insert_list:
                if len(i):
                    insertSql = insertSql + "insert into gaode_date(name, status, direction, angle, lcodes, polyline, date, time,speed)  values ('" + \
                                i[0] + "'," + i[1] + ",'" + i[2] + "'," + i[3] + ",'" + i[4] + "','" + i[
                                    5] + "','" + i[6] + "','" + i[7] + "'," + i[8] + ");"
            cur.execute(insertSql)
            conn.commit();
        else:
            pass


# 批量请求高德数据
def batchGetTrafficStatus():
    # insertSql="";
    currentDate = time.strftime("%Y-%m-%d", time.localtime());
    conn = psycopg2.connect(database="superpower", user="postgres", password="123456", host="localhost", port="5432");
    cur = conn.cursor();
    rectangleData = getRegionRectangles(conn, cur);
    currentTime = time.strftime("%H:%M:%S", time.localtime());
    for rec in rectangleData:
        key = getUseableKey(conn, cur);
        if key == None:
            print("没有可用key了，需要申请更多的账户");
        else:
            requestGaodeTrafficDate(conn, cur, key, currentDate, rec, currentTime);
    cur.close;
    conn.close();


# 定时执行任务
def timedTask(interval):
    a = 1;
    while a == 1:
        print("开始请求的时间： " + time.strftime("%H:%M:%S", time.localtime()));
        batchGetTrafficStatus();
        print("结束请求的时间： " + time.strftime("%H:%M:%S", time.localtime()));
        time.sleep(interval);


# 每五分钟执行一次
timedTask(60 * 5);
