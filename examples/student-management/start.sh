#!/bin/sh

script_dir=$(cd $(dirname $0);pwd)
cd $script_dir
python3 ../../tools/mysqlgen.py j2g.json
j2g
read -n 1 -p "Press any key to continue..."
