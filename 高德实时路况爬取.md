# 高德实时路况数据获取
- **高德实时路况数据获取接口说明**：
[link](http://lbs.amap.com/api/webservice/guide/api/trafficstatus)
- **高德数据获取流程**

```
graph LR
数据请求-->数据解析
数据解析-->数据入库
数据入库-->空间信息解析
```
- **数据库设计**

```
CREATE TABLE "public"."gaode_date" (
"name" varchar(50) COLLATE "default",
"status" int4,
"direction" varchar(50) COLLATE "default",
"angle" int4,
"lcodes" varchar(255) COLLATE "default",
"polyline" text COLLATE "default",
"id" int4 DEFAULT nextval('gaode_id_seq'::regclass) NOT NULL,
"geom" "public"."geometry",
"date" date,
"time" time(6),
"speed" float8,
CONSTRAINT "gaode_date_pkey" PRIMARY KEY ("id")
)
WITH (OIDS=FALSE)
;

ALTER TABLE "public"."gaode_date" OWNER TO "postgres";
COMMENT ON COLUMN "public"."gaode_date"."name" IS '道路名称';
COMMENT ON COLUMN "public"."gaode_date"."status" IS '路况 0：未知 1：畅通 2：缓行 3：拥堵';
COMMENT ON COLUMN "public"."gaode_date"."direction" IS '方向描述';
COMMENT ON COLUMN "public"."gaode_date"."angle" IS '车行角度，判断道路正反向使用。以正东方向为0度，逆时针方向为正，取值范围：[0,360]';
COMMENT ON COLUMN "public"."gaode_date"."lcodes" IS '方向';
COMMENT ON COLUMN "public"."gaode_date"."polyline" IS '道路坐标集，坐标集合';
COMMENT ON COLUMN "public"."gaode_date"."date" IS '请求日期';
COMMENT ON COLUMN "public"."gaode_date"."time" IS '请求时间';
COMMENT ON COLUMN "public"."gaode_date"."speed" IS '速度';
CREATE TRIGGER "beforeinsertinsertgaodedata_trigger" BEFORE INSERT ON "public"."gaode_date"
FOR EACH ROW
EXECUTE PROCEDURE "beforeinsertgaodedata"();
```
- **请求高德数据Python脚本**

```
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
    jsondata = total_json['trafficinfo']['roads'];
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
            print(speed);
            lcodes = i['lcodes']
            polyline = i['polyline']
            list = [name, status, direction, angle, lcodes, polyline, currentDate, currentTime, speed];
            insert_list.append(list);
        conn = psycopg2.connect(database="superpower", user="postgres", password="123456", host="localhost", port="5432");
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
#创建请求时间，确保一次请求的时间都相同
currentTime = time.strftime("%H:%M:%S", time.localtime());  # 设置请求时间
key='yourkey';
rectangle='120.12924,30.30185;120.16018,30.27150';
getGaodeTrafficStatus(key,rectangle，currentTime);
```
- **空间信息解析（在此采用触发器，对数据进行解析，插入数据的同时完成空间信息的解析，减少人工参与。），触发器Sql脚本如下：**

```
--高德数据插入触发器
CREATE OR REPLACE FUNCTION BeforeInsertGaodeData() RETURNS TRIGGER AS $example_table$ 
BEGIN
--自动进行坐标计算，并赋值
NEW.geom=ST_LineFromText('LINESTRING('||replace(replace(New.polyline,',',' '),';',',')||')',4326);
return new;
End	;
$example_table$ LANGUAGE plpgsql;
CREATE TRIGGER BeforeInsertInsertGaodeData_trigger Before INSERT  ON gaode_date FOR EACH ROW EXECUTE PROCEDURE BeforeInsertGaodeData ();
```


- **数据查看，可视化获取的高德数据，如下（未正儿八经的进行渲染：）**
![image](http://note.youdao.com/yws/public/resource/9461424f32755baa75fe045abe52c653/xmlnote/2F1E73B0548744C0AFB78743F6764B81/48612)

- 爬取整个研究区域的实时路况数据
1. 构建整个研究区域的网格，如下图，构建网格过程略。
![image](http://note.youdao.com/yws/public/resource/9461424f32755baa75fe045abe52c653/xmlnote/FA8CF6B67E3E47E29EEBCE7F79E93F88/48620)
    
2. 网格数据库脚本

```
CREATE TABLE "public"."hangzhou_grid" (
"gid" int4 DEFAULT nextval('hangzhou_grid_gid_seq'::regclass) NOT NULL,
"id" numeric(10),
"__xmin" numeric,
"__xmax" numeric,
"ymin" numeric,
"ymax" numeric,
"geom" "public"."geometry",
CONSTRAINT "hangzhou_grid_pkey" PRIMARY KEY ("gid")
)
WITH (OIDS=FALSE)
;

ALTER TABLE "public"."hangzhou_grid" OWNER TO "postgres";
COMMENT ON COLUMN "public"."hangzhou_grid"."__xmin" IS '最小x';
COMMENT ON COLUMN "public"."hangzhou_grid"."__xmax" IS '最大x';
COMMENT ON COLUMN "public"."hangzhou_grid"."ymin" IS '最小y';
COMMENT ON COLUMN "public"."hangzhou_grid"."ymax" IS '最大y';
CREATE INDEX "hangzhou_grid_geom_idx" ON "public"."hangzhou_grid" USING gist ("geom");
```

3.请求整个杭州高德实时路况数据Python脚本

```
#请求整个杭州的区域
conn = psycopg2.connect(database="superpower", user="postgres", password="123456", host="localhost", port="5432");
cur = conn.cursor();

#获取覆盖研究区域的网格
cur.execute("select t.__xmin||','||t.ymin||';'||t.__xmax||','||t.ymax rectangle from hangzhou_grid t");
rectangleData=cur.fetchall();
cur.close;
conn.close();
#创建请求时间，确保一次请求的时间都相同
currentTime = time.strftime("%H:%M:%S", time.localtime());  # 设置请求时间
for rec in rectangleData:
    print(rec[0]);
    getGaodeTrafficStatus(key,rec[0],currentTime);
```
4. 查看请求结果，如下图
![image](http://note.youdao.com/yws/public/resource/9461424f32755baa75fe045abe52c653/xmlnote/7DE06A9F0A6C45FDB690F3D6841699CC/48673)

- 建立高德Key表

```
CREATE TABLE "public"."gaode_keys" (
"key" varchar(255) COLLATE "default" NOT NULL,
"date" date,
"request_count" int4 DEFAULT 0,
"id" int4 NOT NULL,
CONSTRAINT "gaode_keys_pkey" PRIMARY KEY ("id")
)
WITH (OIDS=FALSE)
;
ALTER TABLE "public"."gaode_keys" OWNER TO "postgres";
COMMENT ON COLUMN "public"."gaode_keys"."key" IS 'key值';
COMMENT ON COLUMN "public"."gaode_keys"."date" IS '请求日期';
COMMENT ON COLUMN "public"."gaode_keys"."request_count" IS '请求次数';
```



- **总结**
1. 该方法基本能够将请求区域里的数据，进行覆盖。
2. 获取的数据只是原始数据，若需要进行使用可能需要进行进一步处理，如将某时刻重复数据去除等。
3. 高德API接口有请求次数的限制，因此要覆盖大多数时间，需要申请多个key,大致是60个key,目前不知道高德有没有限制一个IP地址访问次数。（后面持续改进方向：建立key表记录每个key一天访问的次数，动态分配key）
4. 该方法也可以构建研究区域的主要道路，解放道路采集的人力。



