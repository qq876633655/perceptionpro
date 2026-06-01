#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Jenkins 自动发版脚本 —— 将编译产物上传到 perceptionpro 平台。

支持模块：per（感知） / loc（定位） / ctl（控制）

用法示例：
    python publish_version.py \
        --url http://10.20.24.62:7898 \                 
        --module loc \
        --username 18325815905 \
        --password Yl202103 \
        --version-num v5.2.3 \
        --versions-type feature,release \
        --apply-project 主线版本 \
        --dev-test-result "测试版本接口" \
        --version-file /home/user/temp/VNDebug-linux-x86_64.tar.gz

可选参数：
    --dev-test-result 研发提测，默认空

说明：
    脚本始终以退出码 0 结束，发版失败只打印警告，不影响编译流水线状态。
    可通过日志中的 [SUCCESS] / [WARN] 关键字判断发版是否成功。
    
    地址（--url）必填项，必须是平台地址http://10.20.24.62:7898，不能带 /api 之类的路径。
    模块（--module）必填项，必须是 per / loc / ctl 之一，分别对应感知、定位、控制模块。
    账号密码（--username / --password）必填项，必须是perpro账号密码，否则登录失败会跳过发版。
    版本号（--version-num）必填项，必须是字母、数字、._-组合的字符串，且在数据库中唯一，否则会报错。
    版本类型（--versions-type）必填项，必须是 feature/dev/test/hotfix/release 中的一个或多个，逗号分隔。
    适用版本（--apply-project）必填项。常见值有：主线版本、装卸车版本、st版本、e35版本
    研发提测（--dev-test-result）选填项，release note
    版本文件（--version-file）必填项，必须是已存在的文件路径，否则发版会失败。
"""

import argparse
import json
import sys
import os

try:
    import requests
except ImportError:
    print('[WARN] 缺少依赖 requests，跳过发版。请在 Jenkins 节点执行：pip install requests')
    sys.exit(0)

VALID_MODULES = ('per', 'loc', 'ctl')
VALID_TYPES   = {'feature', 'dev', 'test', 'hotfix', 'release'}

MODULE_LABEL = {'per': '感知', 'loc': '定位', 'ctl': '控制'}


def warn(msg):
    """打印警告，不终止程序。"""
    print(f'[WARN] {msg}', flush=True)


def info(msg):
    print(f'[INFO] {msg}', flush=True)


def parse_args():
    parser = argparse.ArgumentParser(description='perceptionpro 自动发版脚本')
    parser.add_argument('--url',             required=True,  help='平台地址，如 http://10.20.24.62:7898')
    parser.add_argument('--module',          required=True,  choices=VALID_MODULES, help='模块：per / loc / ctl')
    parser.add_argument('--username',        required=True,  help='平台账号（手机号）')
    parser.add_argument('--password',        required=True,  help='平台密码')
    parser.add_argument('--version-num',     required=True,  help='版本号，仅允许字母、数字、._-')
    parser.add_argument('--versions-type',   required=True,
                        help='版本类型，逗号分隔，可选值：feature,dev,test,hotfix,release')
    parser.add_argument('--version-file',    required=True,  help='版本文件路径')
    parser.add_argument('--apply-project',   default='主线版本', help='适用专项，默认"主线版本"')
    parser.add_argument('--dev-test-result', default='',     help='研发提测内容')
    return parser.parse_args()


def get_token(base_url, username, password):
    """用账号密码换取 JWT access token，失败返回 None。"""
    url = f'{base_url.rstrip("/")}/api/token/'
    try:
        resp = requests.post(url, json={'username': username, 'password': password}, timeout=15)
    except requests.RequestException as e:
        warn(f'连接平台失败，跳过发版：{e}')
        return None

    if resp.status_code != 200:
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        warn(f'平台登录失败（{resp.status_code}），请检查账号密码：{detail}')
        return None

    token = resp.json().get('access') or (resp.json().get('data') or {}).get('access')
    if not token:
        warn('登录响应中未找到 access token，跳过发版。')
        return None

    info('平台登录成功')
    return token


def publish(base_url, module, token, version_num, versions_type_list, apply_project,
            dev_test_result, version_file_path):
    """上传版本文件，成功返回 True，失败返回 False。"""
    url = f'{base_url.rstrip("/")}/api/{module}_version/'
    headers = {'Authorization': f'Bearer {token}'}

    if not os.path.isfile(version_file_path):
        warn(f'版本文件不存在，跳过发版：{version_file_path}')
        return False

    data = {
        'version_num':     version_num,
        'versions_type':   json.dumps(versions_type_list),  # JSON 字符串，与前端一致
        'apply_project':   apply_project,
        'dev_test_result': dev_test_result,
    }

    info(f'正在上传到 {url}')
    info(f'  模块     : {MODULE_LABEL.get(module, module)}')
    info(f'  版本号   : {version_num}')
    info(f'  版本类型 : {versions_type_list}')
    info(f'  适用专项 : {apply_project}')
    info(f'  文件     : {version_file_path}')

    try:
        with open(version_file_path, 'rb') as f:
            resp = requests.post(
                url,
                headers=headers,
                data=data,
                files={'version_file': (os.path.basename(version_file_path), f)},
                timeout=300,  # 大文件上传最多允许 5 分钟
            )
    except requests.RequestException as e:
        warn(f'上传请求失败，跳过发版：{e}')
        return False

    if resp.status_code in (200, 201):
        try:
            result = resp.json()
            inner = result.get('data') or result
            vid = inner.get('id', '-')
        except Exception:
            vid = '-'
        print(f'[SUCCESS] 发版成功，版本 ID：{vid}', flush=True)
        return True

    # 失败：打印服务端返回的详细原因
    try:
        detail = json.dumps(resp.json(), ensure_ascii=False, indent=2)
    except Exception:
        detail = resp.text
    warn(f'上传失败（HTTP {resp.status_code}），请检查以下错误后手动补传：\n{detail}')
    return False


def main():
    # argparse 参数错误时默认 sys.exit(2)，捕获后改为 [WARN] + exit 0
    try:
        args = parse_args()
    except SystemExit:
        warn('参数错误，跳过发版。请检查 --module / --versions-type 等参数是否正确。')
        sys.exit(0)

    # ── 校验 versions_type ────────────────────────────────────────
    raw_types = [t.strip() for t in args.versions_type.split(',') if t.strip()]
    invalid = set(raw_types) - VALID_TYPES
    if invalid:
        warn(f'版本类型包含不合法值 {invalid}，可选值：{VALID_TYPES}，跳过发版。')
        sys.exit(0)
    if not raw_types:
        warn('未指定版本类型，跳过发版。')
        sys.exit(0)

    # ── 登录 ──────────────────────────────────────────────────────
    token = get_token(args.url, args.username, args.password)
    if not token:
        sys.exit(0)  # 登录失败，警告已打印，正常退出

    # ── 上传 ──────────────────────────────────────────────────────
    publish(
        base_url           = args.url,
        module             = args.module,
        token              = token,
        version_num        = args.version_num,
        versions_type_list = raw_types,
        apply_project      = args.apply_project,
        dev_test_result    = args.dev_test_result,
        version_file_path  = args.version_file,
    )
    # 无论成功或失败，均以 0 退出，不影响编译流水线


if __name__ == '__main__':
    main()