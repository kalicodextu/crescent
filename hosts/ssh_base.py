#!/usr/bin/python env
# -*- coding: utf-8 -*-

import pexpect

from setting import logger
from xylogger import BaseLogger

class ExceptSsh(Exception):


class SSH_Base():
    def __init__(self):     
        self.__fout = open('./log', 'w')
        self.__fout.close()
        print '#' * 60

    def ssh_base(self, ip, user, password, password2, port, prompt):
        self.__fout = open('./log', 'a')
        logging.info('Login with SSH')
        cmd = 'ssh -l %s %s -p %s' % (user, ip, port)
        logging.debug('pexpect spawn: %s', cmd)
        self.child = pexpect.spawn(cmd)
        self.child.logfile_read = self.__fout
        expect_string = "['(?i)host key verification failed',\
         '(?i)are you sure you want to continue connecting',\
         '(?i)password',\
         %s,\
         pexpect.TIMEOUT,\
         pexpect.EOF]" % prompt
        logger.debug('expect: %s', expect_string)
        i = self.child.expect(
            ['(?i)host key verification failed',
             '(?i)are you sure you want to continue connecting',
             '(?i)password',
             prompt,
             pexpect.TIMEOUT,
             pexpect.EOF])
        if i == 0:
            # Remote host identification has changed
            logging.debug('i == 0')
            try:
                info = self.child.before
                logging.debug('info:%s', info)
                key1 = 'Add correct host key in '
                key2 = ' to get rid of this message'
                index1 = info.index(key1) + len(key1)
                index2 = info.index(key2, index1)
                key3 = info[index1: index2]
                cmd2 = 'ssh-keygen -f "%s" -R %s' % (
                    key3, ip)
                child2 = pexpect.spawn(cmd2)  # remove with: cmd
                child2.logfile_read = self.__fout
                child2.expect(pexpect.EOF)
            except Exception as e:
                ex = str(e)
                raise ExceptionRunin(ex)
            # Do it again
            logging.debug('pexpect spawn: %s', cmd)
            self.child = pexpect.spawn(cmd)
            self.child.logfile_read = self.__fout
            logging.debug('expect: %s', expect_string)
            i = self.child.expect(
                ['(?i)host key verification failed',
                 '(?i)are you sure you want to continue connecting',
                 '(?i)password',
                 prompt,
                 pexpect.TIMEOUT,
                 pexpect.EOF])
            if i == 0:
                # This can not happend again, so there must be some error.
                logging.debug('i == 0')
                ex = 'ERROR! host key verification failed.'
                raise ExceptionRunin(ex)

        if i == 1:  # In this case SSH does not have the public key cached.
            logging.debug('i == 1')
            logging.info('send yes')
            self.child.sendline('yes')
            logging.debug('expect: %s', expect_string)
            i = self.child.expect(
                ['(?i)host key verification failed',
                 '(?i)are you sure you want to continue connecting',
                 '(?i)password',
                 prompt,
                 pexpect.TIMEOUT,
                 pexpect.EOF])
        if i == 0 or i == 1:
            logging.debug('i == 0 or i == 1')
            # This can not happend again, so there must be some error.
            ex = 'ERROR! could not login with SSH.'
            raise ExceptionRunin(ex)
        if i == 2:
            logging.debug('i == 2')
            try:
                if (password2 != ''):
                    logging.debug('send password2: %s', password2)
                    self.child.sendline(password2)
                    logging.debug('expect: [%s, password:]', prompt)
                    j = self.child.expect([prompt, 'password:'])
                    if j == 0:
                        logging.debug('j == 0')
                        # Entered the bmc, ok
                        logging.info('Login in successfully.')
                        return 0
                    elif j == 1:
                        logging.debug('j == 1')
                        # Try another password.
                        logging.debug('send password: %s', password)
                        self.child.sendline(password)
                        logging.debug('expect: [%s, Enter current password:]', prompt)
                        k = self.child.expect([prompt, 'Enter current password:'])
                        if k == 0:
                            # Entered the bmc, ok
                            logging.debug('k == 0')
                            logging.info('Login successfully.')
                            return 0
                        elif k == 1:
                            # Need to change the password
                            logging.debug('k == 1')
                            logging.debug('Need to change the password.')
                            logging.debug('send password: %s', password)
                            self.child.sendline(password)
                            logging.debug('expect: Enter new password:')
                            m = self.child.expect(['Enter new password:', pexpect.TIMEOUT])
                            if m == 1:
                                logging.debug('m == 1')
                                ex = 'ERROR! could not find string [Enter new password:]'
                                logging.critical(self.child.before)
                                raise ExceptionRunin(ex)
                            logging.debug('send new password: %s', password2)
                            self.child.sendline(password2)
                            logging.debug('expect:  Re-enter new password:')
                            m = self.child.expect(['Re-enter new password:', pexpect.TIMEOUT])
                            if m == 1:
                                logging.debug('m == 1')
                                ex = 'ERROR! could not find string [Re-enter new password:]'
                                logging.critical(self.child.before)
                                raise ExceptionRunin(ex)
                            logging.debug('send new password again: %s', password2)
                            self.child.sendline(password2)
                            logging.debug('expect:  Password updated successfully')
                            m = self.child.expect(['Password updated successfully', pexpect.TIMEOUT])
                            if m == 1:
                                logging.debug('m == 1')
                                ex = 'ERROR! could not find string [Password updated successfully]'
                                logging.critical(self.child.before)
                                raise ExceptionRunin(ex)
                            logging.debug('expect:  %s', prompt)
                            m = self.child.expect([prompt, pexpect.TIMEOUT])
                            if m == 0:
                                logging.debug('m == 0')
                                logging.info('Login successfully.')
                                return 0
                            elif m == 1:
                                logging.debug('m == 1')
                                ex = 'ERROR! could not find prompt: %s' % prompt
                                logging.critical(self.child.before)
                                raise ExceptionRunin(ex)
                    else:
                        # no password2
                        logging.debug('no password2')
                        logging.debug('send password: %s', password)
                        self.child.sendline(password)
                        logging.debug('expect: [%s, password:]', prompt)
                        j = self.child.expect(prompt, pexpect.TIMEOUT)
                        if j == 0:
                            logging.debug('j == 0')
                            # Entered the bmc, ok
                            logging.info('Login in successfully.')
                            return 0
                        elif j == 1:
                            logging.debug('j == 1')
                            ex = 'ERROR! could not find prompt: %s' % prompt
                            logging.critical(self.child.before)
                            raise ExceptionRunin(ex)
            except Exception as e:
                ex = str(e)
                logging.critical(ex)
                ex = 'ERROR! could not login with SSH.'
                raise ExceptionRunin(ex)
        if i == 3:
            # This may happen if a public key was setup to automatically login.
            # But beware, the COMMAND_PROMPT at this point is very trivial and
            # could be fooled by some output in the MOTD or login message.
            logging.debug('i == 3')
            logging.info('Login successfully.')
            return 0
        if i == 4:  # Timeout
            logging.debug('i == 4')
            ex = 'ERROR! login with SSH TIMEOUT.'
            logging.critical(self.child.before)
            raise ExceptionRunin('Exception: EOF!')
        if i == 5:  # EOF
            logging.debug('i == 5')
            ex = 'ERROR! login with SSH EOF.'
            logging.critical(self.child.before)
            raise ExceptionRunin(ex)
