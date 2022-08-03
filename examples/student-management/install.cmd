@echo off
cd /d %~dp0
python ..\..\setup.py install
pip insatll PyMySQL==1.0.2
