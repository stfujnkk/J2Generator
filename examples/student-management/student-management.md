## student-management 生成示例

测试数据库脚本如下

```mysql
DROP TABLE IF EXISTS T_LEARN_STUDENT;
DROP TABLE IF EXISTS T_LEARN_CLASS;

create table T_LEARN_CLASS (
  urid VARCHAR(32) NOT NULL COMMENT 'URID' PRIMARY KEY,
  CODE VARCHAR(32) NOT NULL COMMENT '班级代码',
  NAME VARCHAR(32) NOT NULL COMMENT '班级名称',
  tenantid INT NOT NULL COMMENT '租户id',
  isactive CHAR(1) NOT NULL COMMENT '是否有效',
  createdby VARCHAR(32) default 0 NOT NULL COMMENT '创建人',
  createdon TIMESTAMP default CURRENT_TIMESTAMP NOT NULL COMMENT '创建时间',
  lastmodifiedby VARCHAR(32) default 0 NOT NULL COMMENT '修改人',
  lastmodifiedon TIMESTAMP default CURRENT_TIMESTAMP NOT NULL COMMENT '修改时间',
  rowversion INT default 1 NOT NULL COMMENT '版本号' CHECK(rowversion>0 AND rowversion<10000),
  memo VARCHAR(256) COMMENT '备注'
)ENGINE=InnoDB DEFAULT CHARSET=UTF8MB4 COMMENT '班级';

create table T_LEARN_STUDENT (
  urid VARCHAR(32) PRIMARY KEY COMMENT 'URID',
  tenantid INT NOT NULL COMMENT '租户id',
  classid VARCHAR(32) NOT NULL COMMENT '班级id',
  code VARCHAR(32) NOT NULL COMMENT '员工编号',
  name VARCHAR(32) NOT NULL COMMENT '员工姓名',
  sex CHAR(1) NOT NULL COMMENT '性别：1-男，2-女',
  age INT NOT NULL COMMENT '年龄',
  height FLOAT NOT NULL COMMENT '身高',
  memo VARCHAR(256) COMMENT '备注',
  createdby VARCHAR(32) DEFAULT '0' NOT NULL COMMENT '创建人',
  createdon TIMESTAMP default CURRENT_TIMESTAMP NOT NULL COMMENT '创建时间',
  lastmodifiedby VARCHAR(32) DEFAULT '0' NOT NULL COMMENT '修改人',
  lastmodifiedon TIMESTAMP default CURRENT_TIMESTAMP NOT NULL COMMENT '修改时间',
  rowversion INT default 1 NOT NULL COMMENT '版本号' CHECK(rowversion>0 AND rowversion<10000),
  CONSTRAINT fk_per_learn_class FOREIGN KEY (CLASSID) REFERENCES T_LEARN_CLASS (URID)
)ENGINE=InnoDB DEFAULT CHARSET=UTF8MB4 COMMENT '学生';
```

进入`student-management`目录，windows运行`start.cmd`脚本,`linux` 运行`start.sh`。

执行完成后会看到生成了个`ats` 文件夹`ext.json`和`j2g.json.bak`文件,`ats`里面即生成的代码。

`j2g.json.bak`为配置文件的备份。`ext.json`为提取的数据库字段信息。