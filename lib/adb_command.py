import os
import json
import time
import re
from config.mappoint import clickcard
import lib.api as api

with open('config.json', 'r') as f:
    config = json.load(f)
adb_path = config['adb_path']
device_id = config['device_id']
adb_head = config['adb_head']
appid = 'com.shenlan.m.reverse1999' 

def touch(x, y):
    #print(f'click {x} {y}')
    print(os.system(f'{adb_head} shell input tap {x} {y}'))


def touch(point):
    #print(f'click {point[0]} {point[1]}')
    print(os.system(f'{adb_head} shell input tap {point[0]} {point[1]}'))


def swipe(p1, p2):
    #print(f'swipe from  {p1[0]} {p1[1]} to {p2[0]} {p2[1]}')
    print(
        os.system(f'{adb_head} shell input touchscreen swipe {p1[0]} {p1[1]} {p2[0]} {p2[1]} 100'))

def is_game_on():
    '''检测游戏是否在前台'''
    with open('config.json', 'r') as f:
        config = json.load(f)
    adb_path = config['adb_path'] 
    command = (f'{adb_head} shell dumpsys window windows')
    try:
        process = os.popen(command)
        output = process.read()
        process.close()
        if appid not in output:
            # 应用不在前台，运行应用
            print("游戏不在前台，正在启动")
            os.popen(f'{adb_head} shell monkey -p {appid} -c android.intent.category.LAUNCHER 1')
            time.sleep(8)
        else:
            # 处理输出
            print('应用已在前台')
    except Exception as e:
        print(f'Error: {e}')

def get_bluestacks_adb_port():
    # 读取bluestacks.conf文件
    bluestacks_adb_port_keys = config.get('bluestacks_adb_port_keys', [])
    bluestacks_conf_path = config.get('bluestacks_conf_path', 'C:/ProgramData/BlueStacks_nxt_cn/bluestacks.conf')
    if not os.path.exists(bluestacks_conf_path):
        print(f'Error: 文件"{bluestacks_conf_path}"不存在')
    else:
        with open(bluestacks_conf_path, 'r') as f:
            conf = f.read()
        # 使用正则表达式匹配adb端口号
        for key in bluestacks_adb_port_keys:
            match = re.search(rf'{key}="(\d+)"', conf)
            if match:
                adb_port = match.group(1)
                return adb_port
    return None

def check_device_connection():
    with open('config.json', 'r') as f:
        config = json.load(f)
    adb_path = config['adb_path']
    # 通过验证adb devices命令的输出结果中List of devices attached下面是否有设备状态为device判断是否有设备连接
    device = None  # 初始化device变量为None
    output = os.popen(f'{adb_path} devices').read().strip().split('\n')
    if len(output) <= 1 or output[0] != 'List of devices attached':
        print('Error: 无设备，尝试连接adb_address')
        if 'adb_address' in config and config['adb_address']:
            device = config['adb_address']
            os.system(f'{adb_path} connect {device}')
            output = os.popen(f'{adb_path} devices').read().strip().split('\n')
            if len(output) <= 1 or output[0] != 'List of devices attached':
                print('Error: 无法连接adb_address，尝试连接蓝叠')
                blurestack=connect_bluestack()
                if not blurestack:
                    return None
                else:
                    return blurestack
            else:
                print(f'已连接设备：{device}')
                config['device_id'] = device
                api.write_config()
                return device
        else:
            print('Error:adb_address为空，尝试连接蓝叠')
            blurestack=connect_bluestack()
            if not blurestack:
                return None
            else:
                return blurestack
    else:
        for line in output[1:]:
            if not line.endswith('\tdevice'):
                continue
            elif line.endswith('\tdevice'):
                device =line.split('\t')[0]
                break
        if not device:
            print('Error: 无设备，尝试连接adb_address')
            if 'adb_address' in config and config['adb_address'].strip():
                device = config['adb_address']
                os.system(f'{adb_path} connect {device}')
                output = os.popen(f'{adb_path} devices').read().strip().split('\n')
                if len(output) <= 1 or output[0] != 'List of devices attached':
                    print('Error: 无法连接adb_address，尝试连接蓝叠')
                    blurestack=connect_bluestack()
                    if not blurestack:
                        return None
                    else:
                        return blurestack
                else:
                    print(f'已连接设备：{device}')
                    config['device_id'] = device
                    api.write_config()
                    return device
            else:
                print('Error:adb_address为空，尝试连接蓝叠')
                blurestack=connect_bluestack()
                if not blurestack:
                    return None
                else:
                    return blurestack
        else:
            print(f'已连接设备：{device}')
            api.write_config()
            return device

def connect_bluestack():
    adb_path = config['adb_path']
    device = '127.0.0.1:' + str(get_bluestacks_adb_port())
    os.system(f'{adb_path} connect {device}')
    output = os.popen(f'{adb_path} devices').read().strip().split('\n')
    if len(output) <= 1 or output[0] != 'List of devices attached':
        print('Error: 无法连接蓝叠(列表为空))')
        return None
    else:
        config['adb_address'] = device
        print(f'已连接设备：{device}')
        config['device_id'] = device
        api.write_config()
        return device
            
def is_device_connected():
    device=None
    # 检查adb路径是否存在
    if 'adb_path' in config and os.path.exists(config['adb_path']):
        adb_path = config['adb_path']
    else:
        project_path = os.path.abspath(os.path.dirname(__file__))
        adb_path = os.path.join(project_path, 'adb\\adb.exe')
        config['adb_path']=adb_path
        api.write_config()
    # 检查adb是否存在
    result = os.system(f'{adb_path} version')
    if result != 0:
        print('Error: config.json有关adb的设置有误')
    else:
        device = check_device_connection()
        if 'device_id' in config and config['device_id'].strip():
            adb_head = f'{adb_path} -s {device_id}'
        else:
            adb_head = f'{adb_path}'
    config['adb_head'] = adb_head
    api.write_config()
    return device
    
            