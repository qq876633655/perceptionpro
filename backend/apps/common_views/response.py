from django.conf import settings
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError, AuthenticationFailed, PermissionDenied, NotAuthenticated
from rest_framework.renderers import JSONRenderer


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    code = 5000
    msg = "服务器异常"
    data = None

    if response is not None:

        # =========================
        # 1️⃣ 参数校验错误（核心优化）
        # =========================
        if isinstance(exc, ValidationError):
            code = 1001

            error_map = {}

            if isinstance(response.data, dict):
                for field, messages in response.data.items():
                    if isinstance(messages, list):
                        error_map[field] = messages
                    else:
                        error_map[field] = [str(messages)]

            elif isinstance(response.data, list):
                error_map["non_field_errors"] = response.data

            else:
                error_map["error"] = [str(response.data)]

            msg = "参数校验失败"
            data = error_map

        # =========================
        # 2️⃣ 认证失败
        # =========================
        elif isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
            code = 2001
            msg = "未认证或登录已过期"

        # =========================
        # 3️⃣ 权限不足
        # =========================
        elif isinstance(exc, PermissionDenied):
            code = 2003
            msg = "没有权限"

        # =========================
        # 4️⃣ 其他 DRF 异常
        # =========================
        else:
            code = 5000
            msg = response.data.get("detail", "请求失败")

        response.data = {
            "code": code,
            "msg": msg,
            "data": data
        }

        return response


class APIResponse(Response):
    def __init__(self, data=None, msg="success", code=0, status=200):
        res = {
            "code": code,
            "msg": msg,
            "data": data
        }
        super().__init__(res, status=status)


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        # 返回原始数据结构，包含分页元信息
        return Response({
            "results": data,
            "count": self.page.paginator.count,
            "page": self.page.number,
            "page_size": self.get_page_size(self.request),
            "total_pages": self.page.paginator.num_pages,  # 可选
        })


class CustomJSONRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response')

        if hasattr(response, 'streaming_content'):
            return super().render(data, accepted_media_type, renderer_context)

        # ✅ 204 No Content 必须返回空 body（HTTP 规范）
        if response and response.status_code == 204:
            return b''

        if isinstance(data, dict) and "code" in data:
            return super().render(data, accepted_media_type, renderer_context)

        if response and response.status_code >= 400:
            return super().render(data, accepted_media_type, renderer_context)

        wrapped_data = {
            "code": 0,
            "msg": "success",
            "data": None
        }

        # ✅ 分页处理
        if isinstance(data, dict) and "results" in data:
            wrapped_data["data"] = data.get("results", [])

            wrapped_data["pagination"] = {
                "count": data.get("count"),
                "page": data.get("page"),
                "page_size": data.get("page_size"),
                "total_pages": data.get("total_pages"),
            }

        else:
            wrapped_data["data"] = data

        return super().render(wrapped_data, accepted_media_type, renderer_context)
