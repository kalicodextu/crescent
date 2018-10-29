#!/usr/bin/python env
# -*- coding: utf-8 -*-

import pexpect

from setting import logger


class ExceptSsh(Exception):
    def __init__(self, value):
        super(ExceptSsh, self).__init__(value)
        self.value = value

    def __str__(self):
        return str(self.value)


class SSH_Base(object):
    def __init__(self, log_name):
        self.log_path = './log/' + log_name
        self.__fout = open(self.log_path, 'w')
        self.__fout.close()
        print '#' * 60

    def ssh_base(self, ip, user, password, port, prompt):
        self.__fout = open(self.log_path, 'a')
        logger.info('Login with SSH')
        cmd = 'ssh -l %s %s -p %s' % (user, ip, port)
        logger.debug('pexpect spawn: %s', cmd)
        self.child = pexpect.spawn(cmd)
        self.child.logfile_read = self.__fout
        expect_string = "['(?i)host key verification failed',\
         '(?i)are you sure you want to continue connecting',\
         '(?i)password',\
         %s,\
         pexpect.TIMEOUT,\
         pexpect.EOF]" % prompt
        logger.debug('expect: %s', expect_string)
        i = self.child.expect([
            '(?i)host key verification failed',
            '(?i)are you sure you want to continue connecting', '(?i)password',
            prompt, pexpect.TIMEOUT, pexpect.EOF
        ])
        if i == 0:
            # Remote host identification has changed
            logger.debug('i == 0')
            try:
                info = self.child.before
                logger.debug('info:%s', info)
                key1 = 'Add correct host key in '
                key2 = ' to get rid of this message'
                index1 = info.index(key1) + len(key1)
                index2 = info.index(key2, index1)
                key3 = info[index1:index2]
                cmd2 = 'ssh-keygen -f "%s" -R %s' % (key3, ip)
                child2 = pexpect.spawn(cmd2)  # remove with: cmd
                child2.logfile_read = self.__fout
                child2.expect(pexpect.EOF)
            except Exception as e:
                ex = str(e)
                raise ExceptionRunin(ex)
            # Do it again
            logger.debug('pexpect spawn: %s', cmd)
            self.child = pexpect.spawn(cmd)
            self.child.logfile_read = self.__fout
            logger.debug('expect: %s', expect_string)
            i = self.child.expect([
                '(?i)host key verification failed',
                '(?i)are you sure you want to continue connecting',
                '(?i)password', prompt, pexpect.TIMEOUT, pexpect.EOF
            ])
            if i == 0:
                # This can not happend again, so there must be some error.
                logger.debug('i == 0')
                ex = 'ERROR! host key verification failed.'
                raise ExceptionRunin(ex)

        if i == 1:  # In this case SSH does not have the public key cached.
            logger.debug('i == 1')
            logger.info('send yes')
            self.child.sendline('yes')
            logger.debug('expect: %s', expect_string)
            i = self.child.expect([
                '(?i)host key verification failed',
                '(?i)are you sure you want to continue connecting',
                '(?i)password', prompt, pexpect.TIMEOUT, pexpect.EOF
            ])
        if i == 0 or i == 1:
            logger.debug('i == 0 or i == 1')
            # This can not happend again, so there must be some error.
            ex = 'ERROR! could not login with SSH.'
            raise ExceptionRunin(ex)
        if i == 2:
            logger.debug('i == 2')
            try:
                logger.debug('send password: %s', password)
                self.child.sendline(password)
                logger.debug('expect: [%s, password:]', prompt)
                j = self.child.expect([prompt, 'password:'])
                if j == 0:
                    logger.debug('j == 0')
                    # Entered the bmc, ok
                    logger.info('Login in successfully.')
                    return 0
                elif j == 1:
                    logger.debug('j == 1')
                    # password incorrect
                    logger.debug('incorrect password: %s', password)
                    ex = 'ERROR! could not login with SSH.'
                    raise ExceptionRunin(ex)
            except Exception as e:
                ex = str(e)
                logger.critical(ex)
                ex = 'ERROR! could not login with SSH.'
                raise ExceptionRunin(ex)
        if i == 3:
            # This may happen if a public key was setup to automatically login.
            # But beware, the COMMAND_PROMPT at this point is very trivial and
            # could be fooled by some output in the MOTD or login message.
            logger.debug('i == 3')
            logger.info('Login successfully.')
            return 0
        if i == 4:  # Timeout
            logger.debug('i == 4')
            ex = 'ERROR! login with SSH TIMEOUT.'
            logger.critical(self.child.before)
            raise ExceptionRunin('Exception: EOF!')
        if i == 5:  # EOF
            logger.debug('i == 5')
            ex = 'ERROR! login with SSH EOF.'
            logger.critical(self.child.before)
            raise ExceptionRunin(ex)
