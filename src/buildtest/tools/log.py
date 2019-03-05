############################################################################
#
#  Copyright 2017-2019
#
#  https://github.com/HPC-buildtest/buildtest-framework
#
#  This file is part of buildtest.
#
#  buildtest is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  buildtest is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with buildtest.  If not, see <http://www.gnu.org/licenses/>.
#############################################################################


"""
Methods related to buildtest logging
"""
import os
import shutil
import logging
from datetime import datetime

from buildtest.tools.config import logID, config_opts


class BuildTestError(Exception):
    """Class responsible for error handling in buildtest."""
    def __init__(self, msg, *args):
        if args:
            msg = msg % args
        self.msg = msg

    def __str__(self):
        return(repr(self.msg))


def init_log():
    """ initialize log file attributes """
    logfile = datetime.now().strftime("buildtest_%H_%M_%d_%m_%Y.log")
    BUILDTEST_LOGDIR = config_opts['BUILDTEST_LOGDIR']

    logpath = os.path.join(BUILDTEST_LOGDIR,logfile)

	# if log directory is not present create it automatically
    if not os.path.exists(BUILDTEST_LOGDIR):
        os.makedirs(BUILDTEST_LOGDIR)
        print ("Creating Log directory: ", BUILDTEST_LOGDIR)

    logger = logging.getLogger(logID)
    fh = logging.FileHandler(logpath)
    formatter = logging.Formatter('%(asctime)s [%(filename)s:%(lineno)s - %(funcName)5s() ] - [%(levelname)s] %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.setLevel(logging.DEBUG)

    return logger, logpath, logfile


def clean_logs():
    """ Delete log directory. this method implements
        buildtest --clean-logs option"""
    BUILDTEST_LOGDIR = config_opts['BUILDTEST_LOGDIR']
    if os.path.exists(BUILDTEST_LOGDIR):
        shutil.rmtree(BUILDTEST_LOGDIR)
        print ("Removing log directory %s", BUILDTEST_LOGDIR)