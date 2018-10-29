#!/usr/bin/env python
# -*- coding:utf-8 -*-
from gevent import monkey
monkey.patch_all()
import gevent, docker, yaml

from docker import errors
from settings import logger, config
from pymongo import MongoClient

class ContainerStart():
    def __init__(self, name):
        self.name = name
        self.docker_client = docker.DockerClient(
            base_url='unix://var/run/docker.sock')

    def get_containerObj(self):
        logger.info('check ' + self.name + ' ...')
        containerObjs = self.docker_client.containers    
        try:
            containerObj = containerObjs.get(self.name)
        except errors.NotFound as ex:
            logger.info(str(ex))
            logger.info('continue')
            return False, None
        else:
            return True, contaninerObj




    def container_init(self):
        logger.info('stop ' + self.name + ' ...')
        flag, containerObjs = self.get_containerObj    
        if not flag:
            return True
        if containerObj.status == 'running':
            containerObj.stop()
        containerObj.remove(force=True) # if container status not exited
        images = containerObj.image.tags
        imageObjs = self.docker_client.images
        for image in images:
            imageObjs.remove(image=image, force=True)
        return True
