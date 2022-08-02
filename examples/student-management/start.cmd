@echo off
cd /d %~dp0
@REM 生成数据库实体信息
python ..\..\tools\mysqlgen.py j2g.json
j2g
pause