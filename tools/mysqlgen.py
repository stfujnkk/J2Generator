#!/usr/bin/python3

import argparse
import os
from shutil import copyfile
from typing import Dict, List
import pymysql
import json

HOST = 'localhost'
USER = 'root'
PASSWD = '123456'
DATABASE = 'fingard'
ENCODING= 'utf8'
PORT = 3306

data_type_map: Dict[str, str] = {
    "VARCHAR": "String",
    "CHAR": "String",
    "BLOB": "byte[]",
    "TEXT": "String",
    "INTEGER": "Long",
    "INT": "Integer",
    "TINYINT": "Integer",
    "SMALLINT": "Integer",
    "MEDIUMINT": "Integer",
    "BIT": "Boolean",
    "BIGINT": "BigInteger",
    "FLOAT": "Float",
    "DOUBLE": "Double",
    "DECIMAL": "BigDecimal",
    "BOOLEAN": "Integer",
    "ID": "Long",
    "DATE": "Date",
    "TIME": "Time",
    "DATETIME": "Timestamp",
    "TIMESTAMP": "Timestamp",
    "YEAR": "Date",
}


def covert_data_type(tp: str):
    tp = tp.upper()
    if tp in data_type_map:
        return data_type_map[tp]
    return tp


def get_col_info(conn: pymysql.Connection, table: str, db: str):
    sql = '''
    SELECT 
        COLUMN_NAME AS `name`,
        DATA_TYPE AS `type`,
        COLUMN_COMMENT AS `commit`
    FROM 
        information_schema.`columns`
    WHERE `table_name` = '{}' AND `table_schema` = '{}'
    '''
    cur = conn.cursor()
    cur.execute(sql.format(table, db))
    cols = []
    for i in cur.fetchall():
        cols.append({
            "name": i[0],
            "type": covert_data_type(i[1]),
            "commit": i[2],
        })
    return {
        "table": table,
        "size": len(cols),
        "cols": cols,
    }


def gen_entities(conn: pymysql.Connection, entities_name: List[str], tables: List[str]):
    '''
    根据类名和表名生成生成实体类信息
    '''
    res = {}
    for i in range(len(entities_name)):
        ename=entities_name[i]
        # 1.当类的首字母和第二个字母都是大写时，返回原值
        if len(ename)>=2 and ename[0].isupper() and ename[1].isupper():
            beanName=ename
        else:
            # 2.默认的情况下是将类的首字母小写,其余的字母不变
            beanName=ename[0].lower()+ename[1:]
        res[ename] = get_col_info(
            conn=conn, table=tables[i], db=str(conn.db, encoding=ENCODING))
        res[ename]['beanName']=beanName
    return res


def save_json(file_path: str, data, indent=None):
    with open(file_path, "w", encoding=ENCODING) as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
    pass


def save_json_config(file_path: str, DTO, indent=None):
    data = {
        "import": [],
        "pathMappings": [],
        "defines": {
            "DTO": DTO
        },
    }
    save_json(file_path, data=data, indent=indent)


def main():
    parser = argparse.ArgumentParser(
        'mysqlgen', description='A general file generator using jinja2 syntax')
    parser.add_argument("main_conf_path", help="主配置路径", default='j2g.json')
    parser.add_argument("-o","--output", help="扩展配置输出路径", default='ext.json',required=False)
    parser.add_argument("-e", "--encode", help="文件编码")
    args = parser.parse_args()
    main_conf_path = os.path.abspath(args.main_conf_path)
    ext_conf_path = os.path.abspath(args.output)
    global ENCODING
    if args.encode:
        ENCODING = args.encode
    enames, tables = [], []
    conn = pymysql.connect(host=HOST, user=USER,
                           password=PASSWD, database=DATABASE, charset='utf8', port=PORT)
    # 备份原文件
    copyfile(main_conf_path, main_conf_path+'.bak')
    with open(main_conf_path, "r", encoding=ENCODING) as f:
        main_conf = json.load(f)
        enames = main_conf['defines']['entities']
        tables = main_conf['defines']['tables']
    save_json_config(ext_conf_path, gen_entities(
        conn=conn, entities_name=enames, tables=tables), indent=4)
    print('配置文件已经成功保存在 {}'.format(ext_conf_path))
    if 'import' in main_conf:
        main_conf_imports = set(main_conf['import'])
    else:
        main_conf_imports = set()
    if ext_conf_path in main_conf_imports:
        return
    main_conf_imports.add(ext_conf_path)
    main_conf['import'] = list(main_conf_imports)
    save_json(main_conf_path, main_conf, indent=4)


if __name__ == '__main__':
    main()
