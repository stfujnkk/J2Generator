# mysqlgen

用于连接mysql 数据库，生成对应的数据表信息用于生成对应的类。需要在配置文件里定义实体类名称和对应的表名。

运行前先安装依赖
```json
pip install PyMySQL==1.0.2
```


修改`j2g.json`配置如下

其中db为数据连接的配置，entities和tables分别为类名列表和对应的表名

```json
{
    "$schema": "https://raw.githubusercontent.com/stfujnkk/J2Generator/main/schema.json",
    "pathMappings": [],
    "defines": {
        "entities": [
            "Student",
            "Class"
        ],
        "tables": [
            "t_learn_student",
            "t_learn_class"
        ]
    },
    "db": {
        "host": "localhost",
        "user": "root",
        "password":"123456",
        "database": "fingard",
        "charset": "utf8",
        "port": 3306
    }
}
```

命令如下

```bash
python mysqlgen [-h] [-o OUTPUT] [-e ENCODE] main_conf_path
```

其中`main_conf_path`为j2g配置文件路径。

"C:\Users\stfujnkk\Desktop\test\J2Generator\examples\student-management\student-management.md"

"C:\Users\stfujnkk\Desktop\test\J2Generator\tools\mysqlgen.md"

完整的生成示例参考 [student-management](../examples/student-management/student-management.md)
