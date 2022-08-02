#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import argparse
import logging
import json
import os
from os import path
from shutil import copyfile
import re
import sys
from typing import Dict, Generator, Tuple
from jinja2 import Template

env = {}


def normalize_config(conf: Dict):
    if 'import' not in conf:
        conf['import'] = []
    if 'defines' not in conf:
        conf['defines'] = {}


def import_conf(conf: Dict):
    '''
    导入外部配置
    '''
    normalize_config(conf)
    for p in conf['import']:
        with open(p, encoding=env['encode']) as f:
            c: Dict = json.load(f)
            normalize_config(c)
            if len(c['import']) > 0:
                import_conf(c)
            for k, v in c['defines'].items():
                if k in conf['defines']:
                    continue
                conf['defines'][k] = v
    conf['import']=[]


def path_parse(prefix: str, pattern: str, context: Dict, **kwargs) -> Generator[Tuple[Dict, str], None, None]:
    '''
    用context里的变量和pattern解析

    例1:  prefix="aa" pattern="{{a}}-{{b}}" context={"a":"G","b":[0,1,2]}。输出 [ "aaG0" ,"aaG1","aaG2"]
    '''
    last_index = 0
    for i in re.finditer(r'{{([^}]*)}}', pattern):
        start, end = i.span()
        prefix += pattern[last_index:start]
        last_index = end
        k = i.group(1).strip()
        if k.isdigit():
            k = int(k)
            if k == 0:
                prefix += kwargs['last_dir']
            elif k > 0:
                prefix += kwargs['old_val'][k-1]
            else:
                prefix += kwargs['old_val'][k]
            continue

        val = context.get(k, '')
        if k not in context:
            logging.warning(f'变量{k}不存在')
            continue
        if type(val) is list:
            # TODO val 元素不为 str 时没考虑 ??? 直接用 __val__
            i, n = 0, len(val)
            # 添加局部上下文
            context['__arr__'].append(val)
            context['__len__'].append(n)
            for v in val:
                context['__index__'].append(i)
                context['__val__'].append(v)
                yield from path_parse(prefix + str(v), pattern=pattern[end:], context=context, **kwargs)
                context['__index__'].pop()
                context['__val__'].pop()
                i += 1
            context['__arr__'].pop()
            context['__len__'].pop()
            return
        context['__arr__'].append(val)
        context['__len__'].append(None)
        context['__index__'].append(None)
        context['__val__'].append(val)
        prefix += val

    yield context, prefix+pattern[last_index:]


def core_processor(template_path: str, output_path: str, context: Dict) -> None:
    '''
    解析template_path路径下的模板文件,并输出结果到output_path。

    template_path 和 output_path 分别为已经解析的模板路径和输出的文件路径。
    正常情况下template_path 和 output_path都不应有未解析的变量。
    context 为当前的上下文。context 默认有__arr__, __len__, __val__, __index__

    注: output_path 结尾不能有/
    '''
    if not os.path.exists(template_path):
        logging.error(f'对应{template_path}路径的模板不存在')
        sys.exit(1)
    is_file = os.path.isfile(template_path)
    if is_file and template_path.endswith('.jinja2'):
        output_path = output_path[:-7]
    if os.path.exists(output_path) and (
        os.path.isfile(output_path)
    ):  # isfile 防止重报误报
        logging.warning(f'{output_path} 已经存在,已经覆盖旧文件')

    if os.path.exists(output_path) and (is_file ^ os.path.isfile(output_path)):
        logging.error(f'解析出错{template_path}和{output_path}不对应,应同为文件或文件夹')
        sys.exit(2)
    if is_file:
        # 如果是文件
        if template_path.endswith('.jinja2'):
            context['__path__'] = output_path
            context['__file__'] = os.path.basename(output_path)
            # 如果是模板文件
            with open(template_path, 'r', encoding=env['encode']) as input_file, open(output_path, 'w', encoding=env['encode']) as output_file:
                t: Template = Template(input_file.read())
                output_file.write(t.render(context))
            del context['__path__'], context['__file__']
        else:
            copyfile(template_path, output_path)
    else:
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        # 如果是文件夹
        listdir, i = os.listdir(template_path), 0
        for item in listdir:
            next_template_path = path.join(template_path, item)
            old_val, last_dir, old_index = context['__val__'], path.basename(
                output_path), context['__index__']
            old_len = context['__len__']
            old_arr = context['__arr__']
            # 不能连等,否则会用同一个引用
            context['__len__'] = []
            context['__index__'] = []
            context['__val__'] = []
            context['__arr__'] = []
            for next_context, next_output_path in path_parse(prefix=output_path, pattern='/'+item, context=context, old_val=old_val, last_dir=last_dir, old_index=old_index):
                core_processor(next_template_path,
                               next_output_path, context=next_context)
            i += 1
            context['__len__'] = old_len
            context['__index__'] = old_index
            context['__val__'] = old_val
            context['__arr__'] = old_arr
        pass
    pass


def main():
    parser = argparse.ArgumentParser(
        'j2generator', description='A general file generator using jinja2 syntax')
    parser.add_argument("-t", "--template", help="模板的根路径", default='templates')
    parser.add_argument("-c", "--config", help="配置文件路径", default='j2g.json')
    parser.add_argument("-e", "--encode", help="默认编码", default='utf8')
    parser.add_argument("-v", "--verbose", help="详细信息", action='store_true')
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    env['template_dir'] = args.template
    env['config_path'] = args.config
    env['encode'] = args.encode
    logging.info('以{}编码读取{}为配置文件'.format(env['encode'], env['config_path']))
    with open(env['config_path'], 'r', encoding=env['encode'])as f:
        conf = json.load(f)
        import_conf(conf)
    logging.debug('公共变量 {}'.format(conf['defines']))
    for item in conf['pathMappings']:
        template_path = path.abspath(
            path.join(env['template_dir'], item['name']))
        output_path = path.abspath(item['path'])
        logging.debug('template_path: {} , output_path: {}'.format(
                      template_path, output_path))
        import_conf(item)
        local_ctx = item['defines']
        for k, v in conf['defines'].items():
            if k in local_ctx:
                continue
            local_ctx[k] = v
        logging.debug(' {} 当前变量 {}'.format(item['name'], local_ctx))
        local_ctx['__arr__'] = []
        local_ctx['__len__'] = []
        local_ctx['__index__'] = []
        local_ctx['__val__'] = []
        core_processor(template_path=template_path,
                       output_path=output_path, context=local_ctx)
        del local_ctx


if __name__ == '__main__':
    # main()
    print(sys.path)
