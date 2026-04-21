# # -*- coding: utf-8 -*-
# """
# Time:2022/9/15 18:37
# Author:YANGLEI
# File:auth.py
# """
# from django.utils.deprecation import MiddlewareMixin
# from django.shortcuts import HttpResponse, redirect
# import requests
#
#
# class AuthMiddleware(MiddlewareMixin):
#     """中间件 认证身份信息"""
#
#     def process_request(self, request):
#         # print(request.path_info)
#         # 只有有账号的人可以创建新的账号，没有账号的人只能登录现场问题处理，避免非部门人员创建账号
#         # white_list = ["/login/", "/image/code/", "/book/", "/demo/", "/media/editor/", "/gf/", "/media/temp/",
#         #             "/media/versions/", '/no_sign_in/', '/media/ctl_versions/', '/media/loc_versions/',
#         #              '/media/rb_versions/', '/media/gf_versions/',"/dd/no_sign_in/","/dd/corp_id/","/dd/login_index/"]
#         white_list = ["/login/", "/image/code/", "/book/", "/demo/", "/media/editor/", "/media/temp/",
#                       "/media/versions/", '/media/ctl_versions/', '/media/loc_versions/',
#                       '/media/rb_versions/', '/media/gf_versions/', "/dd/no_sign_in/", "/dd/corp_id/",
#                       "/dd/login_index/", "/reset/pwd/", '/media/res_sim/bak/', '/st/agv_test_task/add_test_result/']
#
#         # 只有钉钉账户或者有账号密码的用户才能登陆
#
#         # if request.path_info in white_list:
#         #     return
#         for i in white_list:
#             if i in request.path_info:
#                 return
#         info_dict = request.session.get("info")
#         if info_dict:
#             return
#         return redirect('/login/')
#
#     def process_response(self, request, response):
#         return response
