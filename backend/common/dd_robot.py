# -*- coding: utf-8 -*-
"""
Time:2023/5/19 18:08
Author:yanglei
File:dd_robot.py
"""

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
    robot_code = ppc.ROBOT_CODE
    batch_send_otorequest = dingtalkrobot__1__0_models.BatchSendOTORequest(
        robot_code=robot_code,
        user_ids=user_ids,
        msg_key='sampleText',
        msg_param=msg_param
    )
    client.batch_send_otowith_options(batch_send_otorequest, batch_send_otoheaders, util_models.RuntimeOptions())


if __name__ == '__main__':
    dd_h5_robot('2130203330851554', {"content": "测试消息"})
    # dd_h5_robot('01176928686834238522')
