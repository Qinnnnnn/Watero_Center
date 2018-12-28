#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
File : hello_world_server.py
Author : Zerui Qin
CreateDate : 2018-12-28 10:00:00
LastModifiedDate : 2018-12-28 10:00:00
Note : WebSocket服务
"""

import socket
import time

from src.websockets.websocket import WebSocketConnection
from utils.log import log_debug


class WebSocketServer:
    """
    基于Socket的WebSocket服务器
    接受TCP连接之后启动子线程处理WebSocket Connection连接
    """

    def __init__(self):
        """
        初始化
        """
        self.index = 1  # WebSocket连接的index标识
        self.socket = None  # WebSocket的socket句柄
        self.conn_map = dict()

    def run(self, host, port, debug=False):
        """
        启动WebSocket服务器
        :param host: 服务器主机地址
        :param port: 服务器主机端口
        :param debug: 是否为调试模式
        :return:
        """

        log_debug.logger.info('WebSocket服务器启动')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建socket句柄

        while True:  # 初始化socket
            log_debug.logger.info('WebServer服务器开始监听 {0}:{1}'.format(host, port))
            try:
                self.socket.bind((host, port))  # Socket绑定到IP地址和端口
                self.socket.listen(5)  # 设置socket最大TCP连接挂起数
                break  # Socket绑定成功结束循环
            except OSError as exp:  # 需绑定的端口不可用
                log_debug.logger.error('WebSocket服务器启动失败: {0}'.format(exp.strerror))
                time.sleep(5)

        while True:  # 监听端口，新连接开启子线程处理
            conn, address = self.socket.accept()  # 服务器响应请求，返回WebSocket Client的socket句柄和地址
            websocket = WebSocketConnection(conn_map=self.conn_map, index=self.index, conn=conn, host=address[0],
                                            remote=address, debug=debug)  # 根据连接的客户信息, 启动WebSocket连接线程
            websocket.start()  # 启动线程
            self.conn_map[self.index] = conn  # Socket句柄写入WebSocket连接映射表
            self.index += 1
