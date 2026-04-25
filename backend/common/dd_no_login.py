#!/user/bin/env python
# -*- conding:utf-8 -*-


from common import dd_config
from common.dd_config import api2_1_0_config, api1_0_client_config
from alibabacloud_dingtalk.oauth2_1_0 import models as dingtalkoauth_2__1__0_models
from alibabacloud_dingtalk.contact_1_0 import models as dingtalkcontact__1__0_models
from alibabacloud_tea_util import models as util_models
from config import perceptionpro_cfg as ppc
import requests


class DDNoLogin:
    def dd_login(self, authcode):
        client = api2_1_0_config()
        get_user_token_request = dingtalkoauth_2__1__0_models.GetUserTokenRequest(
            client_id=ppc.DD_H5_APPLICATION_CLIENT_ID,
            client_secret=ppc.DD_H5_APPLICATION_CLIENT_SECRET,
            code=authcode,
            refresh_token=authcode,
            grant_type='authorization_code'

        )
        test = client.get_user_token(get_user_token_request).body.access_token
        client_info = api1_0_client_config()
        get_user_headers = dingtalkcontact__1__0_models.GetUserHeaders()
        get_user_headers.x_acs_dingtalk_access_token = test
        user_info = client_info.get_user_with_options('me', get_user_headers, util_models.RuntimeOptions())
        union_id = user_info.body.union_id
        return union_id

    def get_user_id(self, union_id=None, corp_id=None):
        token = dd_config.get_app_access_token()
        if union_id:
            url = 'https://oapi.dingtalk.com/topapi/user/getbyunionid'
            resp = requests.post(url, params={'access_token': token}, json={'unionid': union_id})
            return resp.json()['result']['userid']
        else:
            url = 'https://oapi.dingtalk.com/topapi/v2/user/getuserinfo'
            resp = requests.post(url, params={'access_token': token}, json={'code': corp_id})
            return resp.json()['result']['userid']

    def user_info(self, union_id=None, corp_id=None):
        token = dd_config.get_app_access_token()
        user_id = self.get_user_id(union_id, corp_id)
        url = 'https://oapi.dingtalk.com/topapi/v2/user/get'
        resp = requests.post(url, params={'access_token': token}, json={'userid': user_id}).json()['result']
        # print(resp)
        return {
            'dd_user_id': resp['userid'],
            'username': resp['name'],
            'phone_number': resp['mobile'],
            'avatar': resp.get('avatar', ''),
        }
