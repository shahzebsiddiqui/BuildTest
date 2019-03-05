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
All CMake related functions necessary for writing configuration when writing
the tests.
"""


import os
import shutil
import logging

from buildtest.tools.config import config_opts, logID
from buildtest.tools.file import create_dir, create_file,string_in_file
from buildtest.tools.utility import get_appname, get_appversion


def init_CMakeList(filename):
    """ This method writes the content of BUILDTEST_ROOT/CMakeLists.txt. """

    header = """
cmake_minimum_required(VERSION 2.8)
include(CTest)
ENABLE_TESTING()
add_subdirectory(""" + config_opts['BUILDTEST_TESTDIR'] + ")"

    try:

        fd=open(filename, 'w')
        fd.write(header)
        fd.close()
    except FileNotFoundError as err_msg:
        print(err_msg)
        raise


def update_cmakelists(filename, tag):
    """ This method updates CMakeLists.txt with tag add_subdirectory() that has
        name of subdirectory where CMakeList.txt resides.

        :param filename: CMakeLists.txt that needs to be updated
        :param tag: Name of the subdirectory to be be added in CMakeLists.txt
    """
    fd=open(filename, 'r')
    content=fd.read().strip().split("\n")
    cmd="add_subdirectory("+tag+")"
    if cmd not in content:
        fd.close()
        fd=open(filename, 'a')
        fd.write(cmd+"\n")
        fd.close()
    else:
        fd.close()

def add_test_to_CMakeLists(app_destdir,subdir,cmakelist,testname):
    """ This method inserts the add_test() command in CMakeLists.txt used for
        adding tests so ctest can run the test.
    """

    fd=open(cmakelist,'a')
    add_test_str=""

    logger = logging.getLogger(logID)

    shell_type = config_opts['BUILDTEST_SHELL']

    appname = get_appname()
    appversion = get_appversion()


    # if YAML files are in subdirectory of config directory then update CMakeList
    # in app_destdir to add tag "add_subdirectory" for subdirectory so CMakeList
    # can find tests in subdirectory
    if subdir != "":
        # only update the app_destdir/CMakeLists.txt if subdirectory doesn't exist. This avoids
        # writing duplicate values when there are multiple tests in subdirectory
        parent_cmakelist = os.path.join(app_destdir,"CMakeLists.txt")
        cmake_content = "add_subdirectory(" + subdir + ") \n"
        ret = string_in_file(cmake_content, parent_cmakelist)
        if not ret:
            fd1=open(parent_cmakelist, 'a')
            fd1.write(cmake_content)
            fd1.close()

        # the string add_test in CMakeLists allows you to test script with ctest. The NAME tag is
        # <name>-<version>-<toolchain-name>-<toolchain-version>-<subdir>-<testname>. This
        # naming scheme should allow buildtest to reuse same YAML configs for multiple version
        # built with any toolchains. Subdirectories come in handy when you need to organize tests
        # effectively to avoid naming conflict



    add_test_str = "add_test(NAME {}-{}-{} \t COMMAND {} {} ".format(appname, appversion,testname, shell_type, testname)
    add_test_str += "\t WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR} ) \n"

    if not string_in_file(add_test_str, cmakelist):
        fd.write(add_test_str)

    fd.close()
    logger.debug("Updating File " + cmakelist + " with: " + add_test_str + "\n")


def setup_software_cmake():

    logger = logging.getLogger(logID)
    BUILDTEST_TESTDIR = config_opts['BUILDTEST_TESTDIR']
    BUILDTEST_CLEAN_BUILD = config_opts['BUILDTEST_CLEAN_BUILD']

    name = get_appname()
    version = get_appversion()

    # if top level software directory is not present, create it
    test_ebapp_dir = os.path.join(BUILDTEST_TESTDIR, "ebapp")

    # variables to reference each subdirectory in <software>/<version>
    test_name_dir = os.path.join(test_ebapp_dir, name)
    test_version_dir = os.path.join(test_name_dir, version)


    # BUILDTEST_TESTDIR/CMakeLists.txt
    test_cmakelist = os.path.join(BUILDTEST_TESTDIR, "CMakeLists.txt")

    # BUILDTEST_TESTDIR/ebapps/CMakeLists.txt
    test_ebapp_cmakelist = os.path.join(test_ebapp_dir, "CMakeLists.txt")

    # CMakeLists.txt files in <software>/<version>/<toolchain-name>/<toolchain-version>
    test_name_cmakelist = os.path.join(test_name_dir, "CMakeLists.txt")
    test_version_cmakelist = os.path.join(test_version_dir, "CMakeLists.txt")

    test_destdir = test_version_dir


    logger.debug("----------------------------------------")
    logger.debug("EB Directory Assignments")
    logger.debug("----------------------------------------")

    logger.debug("EB Directory in $BUILDTEST_TESTDIR: %s ", test_ebapp_dir)
    logger.debug("EB Application Directory: %s", test_name_dir)
    logger.debug("EB Application Version Directory: %s", test_version_dir)

    logger.debug("\n")
    logger.debug("Test Directory for EB Application: %s ", test_destdir)

    logger.debug("\n\n")

    logger.debug("----------------------------------------")
    logger.debug("EB CMakeList Assignments")
    logger.debug("----------------------------------------")

    logger.debug("$BUILDTEST_TESTDIR CMakeList Path: %s ", test_cmakelist)
    logger.debug("EB Application CMakeList Path: %s ", test_name_cmakelist)
    logger.debug("EB Application Version CMakeList Path: %s", test_version_cmakelist)


    # if test directory exist, delete and recreate it inorder for reproducible test builds

    if BUILDTEST_CLEAN_BUILD:
        if os.path.isdir(test_destdir):
            shutil.rmtree(test_destdir)
            logger.debug("Removing test directory before creating test: %s", test_destdir)

    # create directories if they don't exist
    # Directory Format: <software>/<version>/toolchain-name>/<toolchain-version>
    create_dir(test_ebapp_dir)
    create_dir(test_name_dir)
    create_dir(test_version_dir)


    # create CMakeList.txt file in each directory of $BUILDTEST_ROOT/<software>/<version>/<toolchain-name>/<toolchain-version> if it doesn't exist
    create_file(test_cmakelist)
    create_file(test_ebapp_cmakelist)
    create_file(test_name_cmakelist)
    create_file(test_version_cmakelist)


    # update CMakeLists.txt with tags add_subdirectory(ebapp)
    update_cmakelists(test_cmakelist, "ebapp")

    # update CMakeLists.txt with tags add_subdirectory(X) where X=name|version|toolchain-name|toolchain-version
    update_cmakelists(test_ebapp_cmakelist, name)
    update_cmakelists(test_name_cmakelist, version)

    print(os.path.join(test_destdir,"CMakeLists.txt"))
    return test_destdir, os.path.join(test_destdir,"CMakeLists.txt")

def setup_system_cmake(pkg):
    BUILDTEST_TESTDIR = config_opts['BUILDTEST_TESTDIR']
    BUILDTEST_CLEAN_BUILD = config_opts['BUILDTEST_CLEAN_BUILD']

    # top level system directory and system package directory
    test_system_dir=os.path.join(BUILDTEST_TESTDIR,"system")
    test_destdir=os.path.join(BUILDTEST_TESTDIR,"system",pkg)

    # top level CMakeLists.txt in testing directory
    test_cmakelist = os.path.join(BUILDTEST_TESTDIR,"CMakeLists.txt")

    # CMakeLists.txt that contains all system package directories to process
    test_cmakelist_pkg = os.path.join(BUILDTEST_TESTDIR,"system","CMakeLists.txt")

    # CMakeLists.txt that contais the actual tests (add_test)
    test_cmakelist_destdir=os.path.join(test_destdir,"CMakeLists.txt")

    logger = logging.getLogger(logID)

    logger.debug("Variables Assignments")
    logger.debug("----------------------------------")
    logger.debug("SYSTEM Test Directory: %s ", test_system_dir)
    logger.debug("Testscript Destination Directory: %s", test_destdir)
    logger.debug("CMakeList for BUILDTEST_TESTDIR: %s ", test_cmakelist)
    logger.debug("CMakeList for $BUILDTEST_TESTDIR/system: %s",  test_cmakelist_pkg)
    logger.debug("CMakeList for $BUILDTEST_TESTDIR/system/%s: %s" , pkg, test_cmakelist_destdir)

    if BUILDTEST_CLEAN_BUILD:
        # if testdirectory exist, delete and recreate it inorder for reproducible test builds
        if os.path.isdir(test_destdir):
            shutil.rmtree(test_destdir)
            logger.debug("Removing directory: %s before creating tests ", test_destdir)

    # create the directories if they don't exist
    create_dir(test_system_dir)
    create_dir(test_destdir)

    # create CMakeLists.txt files if they are not present
    create_file(test_cmakelist)
    create_file(test_cmakelist_pkg)
    create_file(test_cmakelist_destdir)

    # update the CMakeLists.txt with the tag add_subdirectory(system)
    update_cmakelists(test_cmakelist, "system")
    #update CMakeLists.txt with the tag add_subdirectory(pkg) where pkg is the application name
    update_cmakelists(test_cmakelist_pkg, pkg)

    logger.debug("Updating %s with add_subdirectory(system)", test_cmakelist)
    logger.debug("Updating %s with add_subdirectory(%s)", test_cmakelist_pkg,pkg)

    return test_destdir,test_cmakelist_destdir