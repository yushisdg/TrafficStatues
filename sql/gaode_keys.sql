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

Date: 2017-10-26 12:20:36
*/

CREATE SEQUENCE key_id_seq
START WITH 1
INCREMENT BY 1
NO MINVALUE
NO MAXVALUE
CACHE 1;
-- ----------------------------
-- Table structure for gaode_keys
-- ----------------------------
DROP TABLE IF EXISTS "public"."gaode_keys";
CREATE TABLE "public"."gaode_keys" (
"key" varchar(255) COLLATE "default" NOT NULL,
"date" date,
"request_count" int4 DEFAULT 0,
"id" int4 DEFAULT nextval('key_id_seq'::regclass) NOT NULL
)
WITH (OIDS=FALSE)

;
COMMENT ON COLUMN "public"."gaode_keys"."key" IS 'key值';
COMMENT ON COLUMN "public"."gaode_keys"."date" IS '请求日期';
COMMENT ON COLUMN "public"."gaode_keys"."request_count" IS '请求次数';

-- ----------------------------
-- Records of gaode_keys
-- ----------------------------
INSERT INTO "public"."gaode_keys" VALUES ('a5e9cfffb5d9a00c14142cdc17742a8d', '2017-10-25', '0', '2');
INSERT INTO "public"."gaode_keys" VALUES ('911f1e0af83c79bcf9cf35771cda966f', '2017-10-25', '0', '3');
INSERT INTO "public"."gaode_keys" VALUES ('62f8056fccfbed20f5ba53ed210723be', '2017-10-25', '91', '4');
INSERT INTO "public"."gaode_keys" VALUES ('0c15e7b6d463716fb9284d3238199466', '2017-10-25', '0', '5');
INSERT INTO "public"."gaode_keys" VALUES ('911f1e0af83c79bcf9cf35771cda966f', '2017-10-26', '0', '6');
INSERT INTO "public"."gaode_keys" VALUES ('a5e9cfffb5d9a00c14142cdc17742a8d', '2017-10-26', '60', '9');

-- ----------------------------
-- Alter Sequences Owned By 
-- ----------------------------

-- ----------------------------
-- Primary Key structure for table gaode_keys
-- ----------------------------
ALTER TABLE "public"."gaode_keys" ADD PRIMARY KEY ("id");
