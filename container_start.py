#!/usr/bin/env python
# -*- coding:utf-8 -*-
from gevent import monkey
monkey.patch_all()

import gevent, docker, yaml

compose = None
with open('./docker-compose.yml') as f:
    compose = yaml.load(f)
