#_*_ coding:UTF-8 _*_

# import datetime
import json
import sys
import pymysql
import requests

reload(sys)
sys.setdefaultencoding('utf-8')

#取当天日期
# date=(datetime.datetime.now()).strftime('%Y-%m-%d')
# print date
insert_list=[]
getIntersData='http://172.10.3.153:8080/hz_brain_server/getIntersData'
def run():
    # 路口报警
    res = requests.get(url=getIntersData).content
    total_json = json.loads(res)
    print total_json
    jsondata = total_json['data']
    print jsondata
    # scats_id, inter_name, date_day, time_point, alarm_color, vechile_dir, is_entrance, delay_value
    # alarm_color为路口报警，当entrance==1为进口delay_value值范围 0-40  3 ，40-50 2,50+ 1 ：状态1为延时报警 ，状态为2 预警
    # entrance==0为出口0-15 3，15-25 2，25+ 1 ：状态1为延时报警，状态为2 预警（进出口delay_value分别为50+，25+时报警）
    #遍历结果集
    if any(jsondata):
        for i in jsondata:
            scats_id=i['scats_id']
            inter_name=i['inter_name']
            date_day=i['date_day']
            time_point=i['time_point']
            alarm_color=i['alarm_color']
            vechile_dir=i['vechile_dir']
            is_entrance=i['is_entrance']
            delay_value=i['delay_value']
            list=[scats_id,inter_name,date_day,time_point,alarm_color,vechile_dir,is_entrance,delay_value]
            insert_list.append(list)
            print insert_list
         # 插入数据库
        conn = pymysql.connect(host='172******7', port=3306, user='a*er', passwd='*****', db='d*b',
                               charset='utf8')
        cursor = conn.cursor()
        print insert_list
        for i in insert_list:
            print i
            if len(i):
                cursor.execute( "insert into inter_alarm_records(scats_id,inter_name,date_day,time_point,alarm_color,vechile_dir,is_entrance,delay_value)  values (%s,%s,%s,%s,%s,%s,%s,%s,%s)", i)
            conn.commit()
            conn.close()
    else:
        pass





run()

#使用Linux crontab 调度 每分钟一次，数据库设定主键，避免重复数据。   */1 * * * * /usr/bin/python /脚本路径