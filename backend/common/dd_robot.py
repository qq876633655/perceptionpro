# -*- coding: utf-8 -*-
"""
Time:2023/5/19 18:08
Author:yanglei
File:dd_robot.py
"""

import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
import json

from config import perceptionpro_cfg as ppc
from alibabacloud_dingtalk.robot_1_0 import models as dingtalkrobot__1__0_models
from alibabacloud_tea_util import models as util_models
from common import dd_config


def dd_h5_robot(user_ids, msg) -> None:
    client = dd_config.api1_0_config()
    batch_send_otoheaders = dingtalkrobot__1__0_models.BatchSendOTOHeaders()
    batch_send_otoheaders.x_acs_dingtalk_access_token = dd_config.get_app_access_token()
    msg_param = json.dumps(msg, ensure_ascii=False)
    robot_code = ppc.DD_H5_APPLICATION_CLIENT_ID
    batch_send_otorequest = dingtalkrobot__1__0_models.BatchSendOTORequest(
        robot_code=robot_code,
        user_ids=user_ids,
        msg_key='sampleText',
        msg_param=msg_param
    )
    client.batch_send_otowith_options(batch_send_otorequest, batch_send_otoheaders, util_models.RuntimeOptions())


def dd_webhook(secret, webhook):
    timestamp = str(round(time.time() * 1000))
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    webhook += f"&timestamp={timestamp}&sign={sign}"
    return webhook


def send_message(payload, webhook):
    status = True
    response = requests.post(webhook, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
    if "ok" not in response.text:
        status = None
    return status


def _version_release_dd(instance, title, at_mobiles, prod_secret, prod_webhook, is_at_all=False):
    file_url = f"{ppc.PER_PRO_LOCAL_SERVER_URL}{instance.version_file.url}" if instance.version_file else '-'
    creator = instance.created_by.username if instance.created_by else '-'
    payload = {
        "msgtype": "text",
        "text": {
            "content": (
                f"【{title}版本发布】\n"
                f"版本号：{instance.version_num}\n"
                f"发版人：{creator}\n"
                f"版本文件：{file_url}\n"
                f"研发提测：\n{instance.dev_test_result or '-'}"
            )
        },
        "at": {"atMobiles": at_mobiles, "isAtAll": is_at_all},
    }
    if ppc.ENV == "dev":
        webhook = dd_webhook(ppc.TEST_SECRET, ppc.TEST_WEBHOOK)
    else:
        webhook = dd_webhook(prod_secret, prod_webhook)
    return send_message(payload, webhook)


def per_version_release_dd(instance, is_at_all=False):
    return _version_release_dd(instance, "感知",
                               ppc.VERSIONS_AT_MOBILES,
                               ppc.V4_VERSIONS_SECRET, ppc.V4_VERSIONS_WEBHOOK,
                               is_at_all)


def loc_version_release_dd(instance, is_at_all=False):
    return _version_release_dd(instance, "定位",
                               ppc.LOC_VERSIONS_AT_MOBILES,
                               ppc.LOC_VERSIONS_SECRET, ppc.LOC_VERSIONS_WEBHOOK,
                               is_at_all)


def ctl_version_release_dd(instance, is_at_all=False):
    return _version_release_dd(instance, "控制",
                               ppc.CTL_VERSIONS_AT_MOBILES,
                               ppc.CTL_VERSIONS_SECRET, ppc.CTL_VERSIONS_WEBHOOK,
                               is_at_all)


if __name__ == '__main__':
    dd_h5_robot('2130203330851554', {"content": "测试消息"})
    # dd_h5_robot('01176928686834238522')
