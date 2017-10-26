--高德数据插入触发器
CREATE OR REPLACE FUNCTION BeforeInsertGaodeData() RETURNS TRIGGER AS $example_table$ 
BEGIN
--自动进行坐标计算，并赋值
NEW.geom=ST_LineFromText('LINESTRING('||replace(replace(New.polyline,',',' '),';',',')||')',4326);
return new;
End	;
$example_table$ LANGUAGE plpgsql;
CREATE TRIGGER BeforeInsertInsertGaodeData_trigger Before INSERT  ON gaode_date FOR EACH ROW EXECUTE PROCEDURE BeforeInsertGaodeData ();