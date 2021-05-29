from swift import gettext_ as _
from swift.common.swob import Request, Response
from swift.common.utils import split_path, Timestamp, quorum_size
from swift.proxy.controllers.base import get_container_info
from swift.proxy.controllers.obj import ReplicatedObjectController
from swift.common.swob import HTTPException, HTTPServerError, HTTPNotFound, HTTPBadRequest
from swift.common.storage_policy import POLICIES
from eventlet import Timeout
import requests
from io import BytesIO
import mimetypes

from pprint import pprint
import os
import json

class NDPObjectController(ReplicatedObjectController):
    def __init__(self, app, account_name, container_name, object_name, webhook_url,
                 **kwargs):
        super(ReplicatedObjectController, self).__init__(
            app, account_name, container_name, object_name)
        self.webhook_url = webhook_url

    # 检测是否为多副本策略
    def _check_policy(self, policy):
        # 目前只支持多副本存储策略
        if policy.policy_type != 'replication':
            return False
        return True

    # Put请求的重定向实现
    def _store_object(self, req, data_source, nodes, partition, outgoing_headers):
        # 目前只支持多副本存储策略
        container_info = self.container_info(
            self.account_name, self.container_name, req)
        policy_index = req.headers.get(
            'X-Backend-Storage-Policy-Index', container_info['storage_policy'])
        policy = POLICIES.get_by_index(policy_index)
        if not self._check_policy(policy):
            return HTTPBadRequest(request=req, body='Unsupported storage policy')
        if not nodes:
            return HTTPNotFound()

        # 获取存储位置的url
        url_suffix = os.path.join(str(partition), self.account_name, self.container_name, self.object_name)

        node = nodes[0]
        ip = 'http://' + node['ip'] + ':' + str(node['port'])
        obj_url = os.path.join(ip, node['device'], url_suffix)

        # 获取对象数据
        obj_data = BytesIO(data_source)

        # 向计算模块传输数据
        data = {'proxy_link': json.dumps(obj_url), 'obj_data': obj_data, 'headers': json.dumps(
            outgoing_headers), 'ndp_type': 'PUT'}
        resp = requests.post(url=self.webhook_url, data=data)

        return Response(request=req, body=resp.content)

    # Get请求的重定向实现
    def _get_or_head_response(self, req, node_iter, partition, policy):
        if not self._check_policy(policy):
            return HTTPBadRequest(request=req, body='Unsupported storage policy')

        if not node_iter:
            return HTTPNotFound()

        container_info = self.container_info(
            self.account_name, self.container_name, req)
        policy_index = req.headers.get(
            'X-Backend-Storage-Policy-Index', container_info['storage_policy'])
        obj_ring = self.app.get_object_ring(policy_index)
        partition, nodes = obj_ring.get_nodes(
            self.account_name, self.container_name, self.object_name)

        obj_urls = []
        url_suffix = os.path.join(
            str(partition), self.account_name, self.container_name, self.object_name)
        node = nodes[0]
        ip = 'http://' + node['ip'] + ':' + str(node['port'])
        url = os.path.join(ip, node['device'], url_suffix)
        obj_url = url

        with Timeout(180):
            try:
                data = {'proxy_link':obj_url, 'ndp_type': 'GET'}
                result = requests.post(self.webhook_url, data=data)
            except (Timeout):
                return HTTPException("NDP Timeout")
            else:
                return Response(request=req, body=result.content)


class WebhookMiddleware(object):
    def __init__(self, app, conf):
        self.app = app

    def __call__(self, env, start_response):
        req = Request(env)

        if 'x-webhook' in req.headers:
            try:
                (version, account_name, container_name, object_name) = \
                    split_path(req.path_info, 4, 4, True)
            except ValueError:
                # not an object request
                return self.app(env, start_response)

            webhook_url = req.headers['x-webhook']
            req.headers.pop('x-webhook')

            ndp_controller = NDPObjectController(
                self.app, account_name, container_name, object_name, webhook_url)

            if req.method == 'GET':
                return ndp_controller.GET(req)(env, start_response)

            if req.method == 'PUT':
                return ndp_controller.PUT(req)(env, start_response)

        return self.app(env, start_response)


def webhook_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def webhook_filter(app):
        return WebhookMiddleware(app, conf)
    return webhook_filter

