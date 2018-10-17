#!/usr/bin/env python
# -*- coding:utf-8 -*-
from gevent import monkey
monkey.patch_all()

import socket, time, random

import gevent

socket.setdefaulttimeout(3)  # set timeout

class PortAssignment(object):
    def __init__(self):
        self.steady_ports = set()

    def socket_port(self, ip, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = s.connect_ex((ip, port))
        if result == 0:
            self.steady_ports.add(port)
    
    def ip_scan(self, ip):
        thread = []
        print u'开始扫描本机端口'
        start_time = time.time()

        print 'port: 10000 - 20000'
        for i in range(10000, 20000):
            thread.append(gevent.spawn(self.socket_port, ip, int(i)))
        gevent.joinall(thread)

        print 'port: 20000 - 30000'
        for i in range(20000, 30000):
            thread.append(gevent.spawn(self.socket_port, ip, int(i)))
        gevent.joinall(thread)

        print 'port: 30000 - 40000'
        for i in range(30000, 40000):
            thread.append(gevent.spawn(self.socket_port, ip, int(i)))
        gevent.joinall(thread)

        print 'port: 40000 - 50000'
        for i in range(40000, 50000):
            thread.append(gevent.spawn(self.socket_port, ip, int(i)))
        gevent.joinall(thread)

        print 'port: 50000 - 60000'
        for i in range(50000, 60000):
            thread.append(gevent.spawn(self.socket_port, ip, int(i)))
        gevent.joinall(thread)

        print 'port: 60000 - 65534'
        for i in range(60000, 65534):
            thread.append(gevent.spawn(self.socket_port, ip, int(i)))
        gevent.joinall(thread)

        print u'扫描端口完成，总共用时：%.2f' % (time.time() - start_time)
    
    def get_rand_port(self, url):
        self.ip_scan(url)
        while True:
            rand_port = random.randint(10000, 65534)
            if rand_port not in self.steady_ports:
                self.steady_ports.add(rand_porh)
                return rand_port
    

if __name__ == '__main__':
    assign = PortAssignment()
    port = assign.get_rand_port('localhost')
    print port
