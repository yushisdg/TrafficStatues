/*
Navicat PGSQL Data Transfer

Source Server         : localhost
Source Server Version : 90411
Source Host           : localhost:5432
Source Database       : superpower
Source Schema         : public

Target Server Type    : PGSQL
Target Server Version : 90411
File Encoding         : 65001

Date: 2017-10-26 12:20:17
*/

CREATE SEQUENCE gaode_id_seq
START WITH 1
INCREMENT BY 1
NO MINVALUE
NO MAXVALUE
CACHE 1;
-- ----------------------------
-- Table structure for gaode_date
-- ----------------------------
DROP TABLE IF EXISTS "public"."gaode_date";
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
"speed" float8
)
WITH (OIDS=FALSE)

;
COMMENT ON COLUMN "public"."gaode_date"."name" IS '道路名称';
COMMENT ON COLUMN "public"."gaode_date"."status" IS '路况 0：未知 1：畅通 2：缓行 3：拥堵';
COMMENT ON COLUMN "public"."gaode_date"."direction" IS '方向描述';
COMMENT ON COLUMN "public"."gaode_date"."angle" IS '车行角度，判断道路正反向使用。以正东方向为0度，逆时针方向为正，取值范围：[0,360]';
COMMENT ON COLUMN "public"."gaode_date"."lcodes" IS '方向';
COMMENT ON COLUMN "public"."gaode_date"."polyline" IS '道路坐标集，坐标集合';
COMMENT ON COLUMN "public"."gaode_date"."date" IS '请求日期';
COMMENT ON COLUMN "public"."gaode_date"."time" IS '请求时间';
COMMENT ON COLUMN "public"."gaode_date"."speed" IS '速度';

-- ----------------------------
-- Alter Sequences Owned By 
-- ----------------------------

-- ----------------------------
-- Triggers structure for table gaode_date
-- ----------------------------
CREATE TRIGGER "beforeinsertinsertgaodedata_trigger" BEFORE INSERT ON "public"."gaode_date"
FOR EACH ROW
EXECUTE PROCEDURE "beforeinsertgaodedata"();

-- ----------------------------
-- Primary Key structure for table gaode_date
-- ----------------------------
ALTER TABLE "public"."gaode_date" ADD PRIMARY KEY ("id");
