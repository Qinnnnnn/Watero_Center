#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
File : server.py
Author : Zerui Qin
CreateDate : 2018-12-28 10:00:00
LastModifiedDate : 2018-12-28 10:00:00
Note : WebSocket服务
"""

import socket
import time

from src.websockets.connection import Connection
from src.websockets.push_service import PushService
from src.websockets.rpc_service import RpcService
from utils.log import log_debug


class WebSocketServer:
    """
    基于TCP Socket的WebSocket服务器
    接受连接之后启动子线程处理Connection连接、Push任务和RPC Server任务
    """

    def __init__(self):
        """
        初始化
        """
        self.index = 0  # WebSocket连接索引
        self.socket = None  # Socket句柄
        self.conn_map = dict()  # WebSocket连接映射表

    def run(self, host, port, debug=False):
        """
        启动WebSocket服务器
        :param host: 服务器IP地址
        :param port: 服务器主机端口
        :param debug: 是否为调试模式
        :return:
        """

        log_debug.logger.info('RPC 服务启动')
        rpc_service = RpcService()  # 实例化RPC服务线程
        rpc_service.start()  # 启动线程

        log_debug.logger.info('Push 服务启动')
        push_service = PushService(conn_map=self.conn_map)  # 实例化WebSocket主动推送服务
        push_service.start()  # 启动线程

        log_debug.logger.info('WebSocket 服务启动')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建socket句柄
        while True:  # 初始化socket
            log_debug.logger.info(f'WebSocket 服务监听 {host}:{port}')
            try:
                self.socket.bind((host, port))  # Socket绑定IP地址和端口
                self.socket.listen(5)  # 设置socket最大TCP连接挂起数
                break
            except OSError as exp:
                log_debug.logger.error(f'WebSocket 服务启动失败: {exp.strerror}')
                time.sleep(5)

        while True:  # 监听端口，新连接开启子线程处理
            conn, address = self.socket.accept()  # 服务器响应请求，返回socket句柄和主机地址
            connection = Connection(conn_map=self.conn_map, index=self.index, conn=conn, host=address[0],
                                    remote=address, debug=debug)  # 实例化WebSocket被动响应线程
            connection.start()  # 启动线程
            self.conn_map[str(self.index)] = conn  # Socket句柄写入WebSocket连接映射表
            self.index += 1
