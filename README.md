##  简介

一个使用jinja2语法的通用文件生成器

## 安装

```bash
git clone https://github.com/stfujnkk/J2Generator
cd J2Generator
python setup.py install
# 获取帮助
j2g -h
```
## 示例

- [student-management](examples/student-management/student-management.md)

## 快速开始

使用时会默认读取当前目录下的`jsg.json`作为配置文件。默认的模板路径为当前目录下的`templates`文件夹。模板文件以jinja2为后缀。生成时会去除后缀。语法细节参考[jinja2文档](http://docs.jinkan.org/docs/jinja2/)

初始环境如下

```txt
.
├── j2g.json
└── templates
```

`j2g.json`内容如下

```json
{
    "$schema": "https://raw.githubusercontent.com/stfujnkk/J2Generator/main/schema.json",
    "pathMappings": [],
    "defines": {}                                                                                           }
```

如果我想在build目录下生成G-1,G-2,A-1,A-2文件。

可以定义两变量`a`和`b`。

配置文件修改如下

```json
{
    "$schema": "https://raw.githubusercontent.com/stfujnkk/J2Generator/main/schema.json",
    "pathMappings": [{
        "name":"t1",
        "path":"build"                                                                                                                              }],
    "defines": {
        "a":["G","A"],
        "b":[0,1]
    }
}
```

修改目录如下

```txt
.
├── j2g.json
└── templates
 └── t1
     └── {{a}}-{{b}}.jinja2
```

执行结果如下

```txt
.
├── build
│   ├── A-0
│   ├── A-1
│   ├── G-0
│   └── G-1
├── j2g.json
└── templates
 └── t1
     └── {{a}}-{{b}}.jinja2
```

## 参考

### 基本参数

> usage: j2generator [-h] [-t TEMPLATE] [-c CONFIG] [-e ENCODE] [-v]
>
> A general file generator using jinja2 syntax
>
> optional arguments:
>   -h, --help            show this help message and exit
>   -t TEMPLATE, --template TEMPLATE
>                         模板的根路径
>   -c CONFIG, --config CONFIG
>                         配置文件路径
>   -e ENCODE, --encode ENCODE
>                         文件编码
>   -v, --verbose         详细信息

### 配置

一个最简配置如下。配置了 **$schema** 项在[VSCODE](https://code.visualstudio.com/) 里打开文件可以获得完整的 **配置约束** 和 **语法支持** 。

```json
{
    "$schema": "https://raw.githubusercontent.com/stfujnkk/J2Generator/main/schema.json",
    "pathMappings": [
        {
            "name": "db_config_path",
            "path": "test/build/db",
            "defines": {},
            "import": []
        }
    ],
    "defines": {
    },
    "import": []
}
```

#### defines （非必须）

`defines` 里可以定义任意的`json`对象。defines里的对象将作为模板的参数传入。其中`defines`里的变量遵循就近原则。比如`pathMappings`里的`defines`会覆盖最外层的同名变量。



#### import （非必须）

import 里为外部配置文件的路径列表。程序会合并多个配置文件的`pathMappings`和 `defines`。如果`pathMappings`的有几项`name`重复。只会选择最近的配置。

```json
{
    "$schema": "https://raw.githubusercontent.com/stfujnkk/J2Generator/main/schema.json",
    "pathMappings": [
        {
            "name": "db_config_path",
            "path": "test/build/db",
            "defines": {
                // 2
            },
            "import": ["c.json","d.json"]
        }
    ],
    "defines": {
        // 1
    },
    "import": ["a.json","b.json"]
}
```

对于上面配置的`db_config_path`文件夹下的模板，各个区域的变量的优先级从大到小为: `2区域` >  `c.json` > `d.json` > `1区域 `> `a.json` > `b.json`。

#### pathMappings

`pathMappings` 下的列表的`name`和`path`分别对应模板的路径和生成文件的路径

如下图，当name为`db_config_path`，path 为 `build/db`时，`templates/db_config_path` 下的模板生成的文件就会输出到 `build/db` 文件夹下。

```txt
├─build
│  ├─db
│  ├─entity
│  │  ├─dao
│  │  │  └─impl
│  │  └─dto
│  ├─jsp
│  │  └─StudentMgr
│  │      ├─ClassManage
│  │      └─StudentManage
│  └─service
│      └─impl
└─templates
 ├─db_config_path
 ├─entity_path
 │  ├─dao
 │  │  └─impl
 │  └─dto
 ├─jsp_path
 │  └─{{project_name}}
 │      └─{{entities}}Manage
 └─service_path
     └─impl
```

其中`project_name`会根据变量替换为实际路径。如果`project_name`是个数组。比如`project_name=['a','b']`。则会生成两个文件夹。如果路径里有更多变量就会生成更多路径。

#### 上下文变量

配置文件里定义的变量，对于个同个`pathMappings`项的模板值都是一样的。这样就无法细粒度的操作模板。因此有如下`上下文变量`。

- \_\_index__ 记录选择的变量序号(如果是数组)
- \_\_len__ 记录选择的每个变量的长度(如果是数组)
- \_\_val__ 记录选择的每个变量的值
- \_\_arr__ 记录选择的每个变量的待选择的集合
- \_\_file__ 为当前文件名称
- \_\_path__ 为当前路径

举个例子：

假设有如下变量：`a='foo',b=['01','02'],c=['A','B']`。

对于模板文件`{{a}}-{{b}}-{{c}}.txt.jinja2`当生成文件为`foo-01-A.txt`时。

`__index__` 值为 `[None,0,0]`;

`__arr__` 值为 `['foo',['01','02'],['A','B']]`;

`__val__`的值为`['foo','01','A']`;

 `__len__`的值为`[None,2,2]`

---

对于路径又有情况些不同，当生成的模板路径为`{{a}}{{b}}/{{1}}Add.jsp`。

当生成路径为`foo01/{{1}}.jsp`时。`{{1}}` 会用`'foo'`替代。如果时`{{2}}`则是`01`，`{{0}}`则是`foo01`。

## 辅助工具

- [mysqlgen](tools/mysqlgen.md) 用于连接mysql 数据库，生成对应的数据表信息用于生成对应的类

