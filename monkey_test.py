#!/usr/bin/env python
# encoding: utf-8

"""
@version: python2.7
@author: qingbo.wang
@mail: qb.wang@signway.cn
@file: monkey_test.py
@time: 2017/12/13 17:40
@desc:
1、adb命令，安装apk;
2、执行monkey脚本命令；
3、输出测试报告；
4、卸载apk
"""

import os
import sys
import time

WORKSPACE = os.path.abspath(".")
CONFIG_FILE = os.path.join(WORKSPACE, 'config.txt')
sys.path.append(CONFIG_FILE)


# 获取配置信息
def get_work_config():
    print("read file", "r")
    with open(CONFIG_FILE) as f:
        lines = f.readlines()
    config = {}

    for line in lines:
        if line.strip().startswith("#") or len(line.strip()) < 3:
            continue
        elif ":" not in line or line.count(":") > 1:
            print("!!! please check this line: ", line)
            break
        else:
            try:
                line = line.replace("\n", "").strip()
                line_split = line.split(":")
                if line_split.__sizeof__() > 1:
                    if line_split[0] == 'device':
                        config['device'] = line_split[1]
                    elif line_split[0] == 'app_name':
                        config["app_name"] = line_split[1]
                    elif line_split[0] == 'package_name':
                        config["package_name"] = line_split[1]
                    elif line_split[0] == 'main_activity':
                        config["main_activity"] = line_split[1]
                    elif line_split[0] == 'monkey_click_count':
                        config["monkey_click_count"] = line_split[1]
                    elif line_split[0] == 'execute_count':
                        config["execute_count"] = line_split[1]
            except BaseException, e:
                print e
                print("!!! please check this line: ", line)

    print("config : %s" % config)
    return config


# 安装apk
def install_apk(config):
    device_addr = config.get("device")
    print("Ready to start installing %s.apk" % config.get("package_name"))

    if device_addr:
        install_device_apk = "adb -s %s install -r %s\\apk\\%s" \
                             % (device_addr, WORKSPACE, config.get("app_name"))
    os.popen(install_device_apk)
    print("apk %s install successful!" % config.get("package_name"))  # 卸载apk


def uninstall_apk(config):
    device_addr = config.get("device")
    print("Ready to uninstalling %s.apk" % config.get("package_name"))

    if device_addr:
        uninstall_device_apk = "adb -s %s uninstall %s" \
                               % (config.get("device"), config.get("package_name"))
        os.popen(uninstall_device_apk)
        print("apk %s uninstall successful!" % config.get("package_name"))


# 启动apk
def start_app(config):
    print("start %s,please wait" % config.get('package_name'))
    start_app_cmd = "adb -s %s shell am start -n %s/%s" \
                    % (config.get('device'), config.get('package_name'), config.get('main_activity'))
    os.popen(start_app_cmd)


# 杀掉apk进程
def kill_test_app(config):
    force_stopapp = "adb -s %s shell am force-stop %s" \
                    % (config.get(
        'device'), config.get('package_name'))
    os.popen(force_stopapp)


# 执行monkey用例
def execute_monkey(config):
    # kill_test_app()
    monkey_cmd = "adb -s %s shell monkey -p %s -s 10 --ignore-timeouts " \
                 "--pct-appswitch 15 --pct-nav 3 --pct-trackball 10 --pct-motion 30 " \
                 "--pct-touch 40 --pct-anyevent 2 --throttle 600 -v -v -v %s" \
                 % (config.get("device"), config.get("package_name"), config.get("monkey_click_count"))
    os.popen(monkey_cmd)


# 创建测试报告
def create_test_report():
    print("create bugreport file")
    bug_report = "adb -s %s shell bugreport > %s\\bugreport.txt" \
                 % (config.get("device"), WORKSPACE)
    os.popen(bug_report)

    print("create bugreport file ,done")

    chk_test_report = "java -jar %s\\chkbugreport.jar %s\\bugreport.txt" \
                      % (WORKSPACE, WORKSPACE)
    os.popen(chk_test_report)


config = get_work_config()
# install_apk(config)
# start_app(config)
time.sleep(5)

for i in range(int(config.get("execute_count"))):
    print("======execute monkey test case:loop = %s - %s======" % (config.get("execute_count"), (i + 1)))
    execute_monkey(config)
    time.sleep(3)

# 输出报告
create_test_report()

print("Completion of the current monkey testing")

# 卸载apk
# uninstall_apk(config)
raw_input("Enter key to close")