import subprocess
import time
import os
import sys
from typing import List, Tuple, Dict, Set
from datetime import datetime
import re
import threading
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

#配置项
TEST_JAR_FILES = [
                  # '.jar/赵骥远.jar',
                  # '.jar/天枢星.jar',
                  # '.jar/天璇星.jar',
                  # '.jar/天权星.jar',
                  # '.jar/玉衡星.jar',
                  # '.jar/开阳星.jar',
                  # '.jar/摇光星.jar',
                  '.jar/洞明星.jar'
                  #'.jar/开阳星.jar'
                  # '.jar/赵骥远旧版.jar',
                  # '.jar/赵骥远新版400.jar',
                  # '.jar/赵骥远新版395.jar',
                  # '.jar/朱城宇旧版.jar',
                  # '.jar/朱城宇新版.jar',
                  # '.jar/朱城宇未踹人.jar',
                  # '.jar/孙琦航.jar',
                  # '.jar/江亦轩less.jar',
                  # '.jar/江亦轩新版.jar',
                  # '.jar/罗春宇.jar',
                  # '.jar/罗天翼.jar',
                  # '.jar/向滢澔.jar',
                  # '.jar/孔祥骐.jar',
                  # '.jar/江亦轩hw_5_v2.jar',
                  ]  # 多个JAR文件

DEFAULT_TEST_COUNT = 100
DEFAULT_REQUEST_COUNT = 200
ERROR_OUTPUT_DIR = 'error_cases'
INPUT_OUTPUT_DIR = 'test_inputs'
TEMP_INPUT_FILE = 'temp_input.txt'
TEMP_OUTPUT_FILE = 'temp_output.txt'
SINGLE_INSTANCE_TEST = True  # 单例测试模式开关
MAX_THREADS = 10  # 最大并发线程数
TIMEOUT_SECONDS = 120  # 超时时间(秒)

# 线程安全的共享变量
total_tests = 0
passed_tests = 0
failed_tests = 0
test_times = {}
avg_completion_times = {}  # 新增：平均完成时间
power_consumptions = {}  # 新增：系统耗电量
lock = threading.Lock()


class TestEvaluator:
    def __init__(self):
        self.start_time = time.time()
        os.makedirs(ERROR_OUTPUT_DIR, exist_ok=True)
        os.makedirs(INPUT_OUTPUT_DIR, exist_ok=True)

    def print_red(self, text: str):
        """红色输出错误信息"""
        sys.stderr.write(f"\033[91m{text}\033[0m\n")
        sys.stderr.flush()

    def print_green(self, text: str):
        """绿色输出信息"""
        sys.stdout.write(f"\033[92m{text}\033[0m\n")
        sys.stdout.flush()

    def print_info(self, text: str):
        """蓝色输出信息"""
        sys.stdout.write(f"\033[94m{text}\033[0m\n")
        sys.stdout.flush()

    def generate_input_data(self, m: int) -> List[str]:
        """生成输入数据"""
        if not SINGLE_INSTANCE_TEST:
            from data_generator import generate_passenger_requests
            return generate_passenger_requests(m)
        try:
            with open('test.txt', 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            self.print_red("单例测试模式开启，但未找到test.txt文件")
            sys.exit(1)

    def run_jar_program(self, input_data: List[str], test_num: int, jar_file: str) -> Tuple[str, bool, float]:
        """运行.jar程序，使用os.system重定向输入输出"""
        input_filename = f"test_input_{test_num}.txt"
        output_filename = f"test_output_{test_num}_{os.path.basename(jar_file)}.txt"

        # 写入输入文件
        with open(input_filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(input_data))

        start_time = time.time()
        last_print_time = start_time

        # 使用os.system运行程序并重定向输入输出
        cmd = f'java -jar {jar_file} < {input_filename} > {output_filename}'

        # 在后台运行命令
        process = subprocess.Popen(cmd, shell=True)

        # 实时显示运行时间
        thread_name = threading.current_thread().name
        while process.poll() is None:
            current_time = time.time()
            if current_time - start_time > TIMEOUT_SECONDS:
                process.kill()
                self.print_red(f"程序运行超时(>{TIMEOUT_SECONDS}秒)，已终止")
                return "", False, TIMEOUT_SECONDS

            if current_time - last_print_time >= 0.1:  # 每0.1秒更新一次
                elapsed = current_time - start_time
                # 使用线程名称来区分输出
                sys.stdout.write(f"\r线程 {thread_name} - 程序运行中... 已用时: {elapsed:.2f}秒")
                sys.stdout.flush()
                last_print_time = current_time
            time.sleep(0.05)  # 稍微降低CPU使用率

        # 获取返回码
        return_code = process.returncode
        elapsed = time.time() - start_time
        sys.stdout.write("\n")  # 换行

        # 读取输出文件
        try:
            with open(output_filename, 'r', encoding='utf-8') as f:
                output = f.read()
        except FileNotFoundError:
            output = ""

        # 清理临时文件
        try:
            os.remove(input_filename)
        except OSError:
            pass
        try:
            os.remove(output_filename)
        except OSError:
            pass

        self.print_info("=== 程序输出结束 ===")
        return output, return_code == 0, elapsed

    def is_output_correct(self, input_data: List[str], jar_output: str) -> Tuple[bool, float, float]:
        """验证输出正确性并计算评价指标"""
        self.print_info("\n=== 开始验证输出正确性 ===")

        try:
            # 解析输入数据
            passengers = self._parse_input_data(input_data)
            if not passengers:
                return False, 0.0, 0.0

            # 解析输出数据
            events = self._parse_output_data(jar_output)
            if not events:
                return False, 0.0, 0.0

            # 初始化电梯状态和乘客状态
            elevators = {i: self._init_elevator_state() for i in range(1, 7)}
            passenger_states = {pid: {'current_floor': data['from_floor'],
                                      'in_elevator': False,
                                      'elevator_id': data['elevator_id'],
                                      'to_floor': data['to_floor'],
                                      'completed': False,
                                      'request_time': data['timestamp'],
                                      'complete_time': 0.0,
                                      'priority': 1.0}  # 默认优先级为1.0
                                for pid, data in passengers.items()}

            # 初始化耗电量统计
            power_consumption = 0.0

            # 验证事件序列并计算指标
            for event in events:
                # 统计耗电量
                if event['event_type'] == 'ARRIVE':
                    power_consumption += 0.4  # 移动一层耗电0.4
                elif event['event_type'] in ['OPEN', 'CLOSE']:
                    power_consumption += 0.1  # 开关门耗电0.1

                # 处理不同类型的事件
                handler = getattr(self, f'_handle_{event["event_type"].lower()}', None)
                if handler:
                    if not handler(event, elevators, passenger_states):
                        return False, 0.0, 0.0

                    # 记录乘客完成时间
                    if event['event_type'] == 'OUT' and event['floor'] == passenger_states[event['passenger_id']][
                        'to_floor']:
                        passenger_states[event['passenger_id']]['complete_time'] = event['timestamp']

            # 验证最终状态
            if not self._validate_final_state(passenger_states):
                return False, 0.0, 0.0

            # 计算平均完成时间
            total_priority = sum(p['priority'] for p in passenger_states.values())
            avg_completion_time = 0.0
            for pid, p in passenger_states.items():
                if p['completed']:
                    wait_time = p['complete_time'] - p['request_time']
                    weighted_wait = wait_time * (p['priority'] / total_priority)
                    avg_completion_time += weighted_wait

            return True, avg_completion_time, power_consumption

        except Exception as e:
            self.print_red(f"验证过程中发生错误: {str(e)}")
            return False, 0.0, 0.0
        finally:
            self.print_info("=== 验证结束 ===")

    def _parse_input_data(self, input_data: List[str]) -> dict:
        """解析输入数据"""
        passengers = {}
        for line in input_data:
            parts = re.split(r'[-\]]', line.strip())
            if len(parts) < 10:
                continue
            try:
                passenger_id = parts[1]
                passengers[passenger_id] = {
                    'timestamp': float(parts[0][1:]),
                    'from_floor': parts[5],
                    'to_floor': parts[7],
                    'elevator_id': int(parts[9]),
                    'completed': False,
                    'current_floor': parts[5]  # 新增当前楼层
                }
            except (ValueError, IndexError) as e:
                self.print_red(f"输入数据解析错误: {line} - {str(e)}")
                return {}
        return passengers

    def _parse_output_data(self, jar_output: str) -> list:
        """解析输出数据"""
        events = []
        for line in [l.strip() for l in jar_output.split('\n') if l.strip()]:
            parts = re.split(r'[-\]]', line)
            if len(parts) < 3:
                self.print_red(f"输出格式错误: {line}")
                return []

            try:
                event = {
                    'timestamp': float(parts[0][1:]),
                    'event_type': parts[1],
                    'elevator_id': int(parts[3] if parts[1] in ['ARRIVE', 'OPEN', 'CLOSE'] else parts[4])
                }

                if parts[1] in ['IN', 'OUT']:
                    event.update({
                        'passenger_id': parts[2],
                        'floor': parts[3]
                    })
                else:
                    event['floor'] = parts[2]

                events.append(event)
            except (ValueError, IndexError) as e:
                self.print_red(f"输出数据解析错误: {line} - {str(e)}")
                return []
        return events

    def _init_elevator_state(self):
        """初始化电梯状态"""
        return {
            'current_floor': 'F1',
            'state': 'CLOSE',
            'passengers': set(),
            'last_arrive_time': 0.0,
            'last_open_time': 0.0,
            'last_close_time': 0.0
        }

    def _validate_events(self, events, elevators, passenger_states):
        """验证事件序列"""
        last_timestamp = 0.0
        valid_floors = {'B4', 'B3', 'B2', 'B1', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7'}

        for event in events:
            # 验证基础属性
            if not self._validate_basic_event_properties(event, last_timestamp, valid_floors, elevators):
                return False

            # 处理不同类型的事件
            handler = getattr(self, f'_handle_{event["event_type"].lower()}', None)
            if handler and not handler(event, elevators, passenger_states):
                return False

            last_timestamp = event['timestamp']
        return True

    def _validate_basic_event_properties(self, event, last_timestamp, valid_floors, elevators):
        """验证事件基本属性"""
        if event['timestamp'] < last_timestamp:
            self.print_red(f"时间戳错误: {event['timestamp']} < {last_timestamp}")
            return False

        if event['elevator_id'] not in elevators:
            self.print_red(f"无效电梯ID: {event['elevator_id']}")
            return False

        if event['floor'] not in valid_floors:
            self.print_red(f"无效楼层: {event['floor']}")
            return False

        return True

    def _handle_arrive(self, event, elevators, _):
        """处理ARRIVE事件"""
        elevator_id = event['elevator_id']
        elevator = elevators[elevator_id]

        if elevator['state'] != 'CLOSE':
            self.print_red(f"电梯{elevator_id}移动时门是开的")
            return False

        current_num = self.floor_to_num(elevator['current_floor'])
        new_num = self.floor_to_num(event['floor'])

        if abs(new_num - current_num) != 1:
            self.print_red(f"电梯{elevator_id}一次移动多层: {elevator['current_floor']} -> {event['floor']}")
            return False

        if elevator['last_arrive_time'] > 0:
            time_diff = event['timestamp'] - elevator['last_arrive_time']
            if time_diff < abs(new_num - current_num) * 0.39:
                self.print_red(f"电梯{elevator_id}移动太快: {time_diff:.2f}s")
                return False

        elevator.update({
            'current_floor': event['floor'],
            'last_arrive_time': event['timestamp']
        })
        return True

    def _handle_open(self, event, elevators, _):
        """处理OPEN事件"""
        elevator_id = event['elevator_id']
        elevator = elevators[elevator_id]

        if elevator['state'] == 'OPEN':
            self.print_red(f"电梯{elevator_id}已经开门")
            return False

        if elevator['current_floor'] != event['floor']:
            self.print_red(f"电梯{elevator_id}不在楼层{event['floor']}却尝试开门")
            return False

        elevator.update({
            'state': 'OPEN',
            'last_open_time': event['timestamp']
        })
        return True

    def _handle_close(self, event, elevators, _):
        """处理CLOSE事件"""
        elevator_id = event['elevator_id']
        elevator = elevators[elevator_id]

        if elevator['state'] == 'CLOSE':
            self.print_red(f"电梯{elevator_id}已经关门")
            return False

        if elevator['current_floor'] != event['floor']:
            self.print_red(f"电梯{elevator_id}不在楼层{event['floor']}却尝试关门")
            return False

        if event['timestamp'] - elevator['last_open_time'] < 0.39:
            self.print_red(f"电梯{elevator_id}开关门时间太短")
            return False

        elevator.update({
            'state': 'CLOSE',
            'last_close_time': event['timestamp']
        })
        return True

    def _handle_in(self, event, elevators, passenger_states):
        """处理IN事件"""
        elevator_id = event['elevator_id']
        elevator = elevators[elevator_id]
        passenger_id = event['passenger_id']

        if passenger_id not in passenger_states:
            self.print_red(f"未知乘客ID: {passenger_id}")
            return False

        passenger = passenger_states[passenger_id]

        checks = [
            (elevator['state'] != 'OPEN', f"乘客{passenger_id}尝试进入未开门的电梯{elevator_id}"),
            (passenger_id in elevator['passengers'], f"乘客{passenger_id}已经在电梯{elevator_id}里"),
            (passenger['current_floor'] != event['floor'], f"乘客{passenger_id}不在楼层{event['floor']}"),
            (passenger['elevator_id'] != elevator_id, f"乘客{passenger_id}进入了非指定电梯{elevator_id}"),
            (len(elevator['passengers']) >= 6, f"电梯{elevator_id}已满(6人)")
        ]

        for condition, error_msg in checks:
            if condition:
                self.print_red(error_msg)
                return False

        elevator['passengers'].add(passenger_id)
        passenger_states[passenger_id]['in_elevator'] = True
        return True

    def _handle_out(self, event, elevators, passenger_states):
        """处理OUT事件"""
        elevator_id = event['elevator_id']
        elevator = elevators[elevator_id]
        passenger_id = event['passenger_id']

        if passenger_id not in passenger_states:
            self.print_red(f"未知乘客ID: {passenger_id}")
            return False

        passenger = passenger_states[passenger_id]

        checks = [
            (elevator['state'] != 'OPEN', f"乘客{passenger_id}尝试离开未开门的电梯{elevator_id}"),
            (passenger_id not in elevator['passengers'], f"乘客{passenger_id}不在电梯{elevator_id}里")
        ]

        for condition, error_msg in checks:
            if condition:
                self.print_red(error_msg)
                return False

        elevator['passengers'].remove(passenger_id)
        passenger_states[passenger_id]['in_elevator'] = False
        passenger_states[passenger_id]['current_floor'] = event['floor']

        # 检查是否到达目标楼层
        if event['floor'] == passenger['to_floor']:
            passenger_states[passenger_id]['completed'] = True
            passenger_states[passenger_id]['complete_time'] = event['timestamp']

        return True

    def _validate_final_state(self, passenger_states):
        """验证最终状态"""
        for pid, passenger in passenger_states.items():
            if not passenger['completed']:
                self.print_red(f"乘客{pid}未到达目的地{passenger['to_floor']} (最后在{passenger['current_floor']})")
                return False
        return True

    def floor_to_num(self, floor: str) -> int:
        """楼层转数字"""
        return 1 - int(floor[1:]) if floor.startswith('B') else int(floor[1:])

    def save_error_case(self, input_data: List[str], jar_output: str, error_msg: str, test_num: int, jar_file: str):
        """保存错误用例"""
        filename = f"{ERROR_OUTPUT_DIR}/error_case_{test_num}_{os.path.basename(jar_file)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"=== 输入数据 ===\n{'\n'.join(input_data)}\n\n")
            f.write(f"=== 程序输出 ===\n{jar_output}\n\n")
            if error_msg:
                f.write(f"=== 错误信息 ===\n{error_msg}\n")
        self.print_red(f"错误用例已保存到: {filename}")

    def run_test(self, m: int, test_num: int):
        """执行单次测试"""
        print(f"\n=== 准备测试 {test_num} ===")
        input_data = self.generate_input_data(m)

        # 保存输入数据到test_inputs目录
        input_filename = f"{INPUT_OUTPUT_DIR}/test_input_{test_num}.txt"
        with open(input_filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(input_data))

        results = {}
        for jar_file in TEST_JAR_FILES:
            print(f"运行.jar程序 {jar_file} (java -jar {jar_file} < {input_filename})...")
            output, success, elapsed = self.run_jar_program(input_data, test_num, jar_file)
            time.sleep(0.1)

            if not success:
                error_type = "程序运行超时" if elapsed >= TIMEOUT_SECONDS else "程序运行错误"
                self.print_red(f"程序 {jar_file} {error_type}")
                self.save_error_case(input_data, output, error_type, test_num, jar_file)
                results[jar_file] = (False, elapsed, 0.0, 0.0)
            else:
                is_correct, avg_completion_time, power_consumption = self.is_output_correct(input_data, output)
                if not is_correct:
                    self.print_red(f"程序 {jar_file} 输出结果不正确!")
                    self.save_error_case(input_data, output, "输出验证失败", test_num, jar_file)
                    self.print_red(f"测试 {test_num} 对于 {jar_file} 失败!")
                    results[jar_file] = (False, elapsed, 0.0, 0.0)
                else:
                    self.print_green(f"测试 {test_num} 对于 {jar_file} 通过!")
                    self.print_info(f"平均完成时间: {avg_completion_time:.2f}s, 系统耗电量: {power_consumption:.2f}")
                    results[jar_file] = (True, elapsed, avg_completion_time, power_consumption)

        return results

    def update_stats(self, results: Dict[str, Tuple[bool, float, float, float]], test_num: int):
        """更新统计信息"""
        global passed_tests, failed_tests, test_times, avg_completion_times, power_consumptions
        with lock:
            for jar_file, (result, elapsed, avg_time, power) in results.items():
                if jar_file not in test_times:
                    test_times[jar_file] = []
                    avg_completion_times[jar_file] = []
                    power_consumptions[jar_file] = []

                if result:
                    passed_tests += 1
                else:
                    failed_tests += 1

                test_times[jar_file].append(elapsed)
                avg_completion_times[jar_file].append(avg_time)
                power_consumptions[jar_file].append(power)

    def calculate_rankings(self):
        """计算并返回各项指标的排名"""
        # 计算每个指标的平均值
        time_avgs = {jar: np.mean(times) for jar, times in test_times.items()}
        completion_avgs = {jar: np.mean(times) for jar, times in avg_completion_times.items()}
        power_avgs = {jar: np.mean(powers) for jar, powers in power_consumptions.items()}

        # 按值排序并返回排名
        time_rank = sorted(time_avgs.items(), key=lambda x: x[1])
        completion_rank = sorted(completion_avgs.items(), key=lambda x: x[1])
        power_rank = sorted(power_avgs.items(), key=lambda x: x[1])

        return time_rank, completion_rank, power_rank

    def print_rankings(self):
        """输出各项指标的排名"""
        time_rank, completion_rank, power_rank = self.calculate_rankings()

        print("\n=== 运行时间排名 ===")
        for rank, (jar, time_avg) in enumerate(time_rank, 1):
            print(f"{rank}. {os.path.basename(jar)}: {time_avg:.2f}秒")

        print("\n=== 平均完成时间排名 ===")
        for rank, (jar, completion_avg) in enumerate(completion_rank, 1):
            print(f"{rank}. {os.path.basename(jar)}: {completion_avg:.2f}秒")

        print("\n=== 系统耗电量排名 ===")
        for rank, (jar, power_avg) in enumerate(power_rank, 1):
            print(f"{rank}. {os.path.basename(jar)}: {power_avg:.2f}")

    def plot_runtime(self):
        """绘制运行时间图表"""
        if not test_times:
            return

        test_numbers = list(range(1, len(list(test_times.values())[0]) + 1))
        plt.figure(figsize=(10, 6))

        for jar_file, times in test_times.items():
            plt.plot(test_numbers, times, marker='o', label=os.path.basename(jar_file))

        plt.xlabel('测试数据编号')
        plt.ylabel('运行时间 (秒)')
        plt.title('程序运行时间')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('运行时间.png', bbox_inches='tight')
        plt.close()
        print("运行时间图表已保存为 运行时间.png")

    def plot_completion_time(self):
        """绘制平均完成时间图表"""
        if not avg_completion_times:
            return

        test_numbers = list(range(1, len(list(avg_completion_times.values())[0]) + 1))
        plt.figure(figsize=(10, 6))

        for jar_file, times in avg_completion_times.items():
            plt.plot(test_numbers, times, marker='o', label=os.path.basename(jar_file))

        plt.xlabel('测试数据编号')
        plt.ylabel('平均完成时间 (秒)')
        plt.title('乘客平均完成时间')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('平均完成时间.png', bbox_inches='tight')
        plt.close()
        print("平均完成时间图表已保存为 平均完成时间.png")

    def plot_power_consumption(self):
        """绘制系统耗电量图表"""
        if not power_consumptions:
            return

        test_numbers = list(range(1, len(list(power_consumptions.values())[0]) + 1))
        plt.figure(figsize=(10, 6))

        for jar_file, powers in power_consumptions.items():
            plt.plot(test_numbers, powers, marker='o', label=os.path.basename(jar_file))

        plt.xlabel('测试数据编号')
        plt.ylabel('系统耗电量')
        plt.title('系统耗电量')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('系统耗电量.png', bbox_inches='tight')
        plt.close()
        print("系统耗电量图表已保存为 系统耗电量.png")

    def calculate_scores(self):
        """计算综合得分"""
        # 计算每个指标的平均值
        time_avgs = {jar: np.mean(times) for jar, times in test_times.items()}
        completion_avgs = {jar: np.mean(times) for jar, times in avg_completion_times.items()}
        power_avgs = {jar: np.mean(powers) for jar, powers in power_consumptions.items()}

        # 计算基准值
        def calculate_baselines(values):
            Xavg = np.mean(list(values))
            Xmin = min(values)
            Xmax = max(values)
            basemin = 0.1 * Xavg + 0.9 * Xmin
            basemax = 0.1 * Xavg + 0.9 * Xmax
            return basemin, basemax

        time_basemin, time_basemax = calculate_baselines(time_avgs.values())
        completion_basemin, completion_basemax = calculate_baselines(completion_avgs.values())
        power_basemin, power_basemax = calculate_baselines(power_avgs.values())

        # 定义评分函数
        def r(x, basemin, basemax):
            if x <= basemin:
                return 1.0
            elif x > basemax:
                return 0.0
            else:
                return (basemax - x) / (basemax - basemin)

        # 计算每个JAR文件的综合得分
        scores = {}
        for jar in TEST_JAR_FILES:
            r_time = r(time_avgs[jar], time_basemin, time_basemax)
            r_completion = r(completion_avgs[jar], completion_basemin, completion_basemax)
            r_power = r(power_avgs[jar], power_basemin, power_basemax)
            total_score = 15 * (0.3 * r_time + 0.3 * r_completion + 0.4 * r_power)
            scores[jar] = total_score

        # 按得分排序
        ranked_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked_scores

    def plot_scores(self, ranked_scores):
        """绘制综合得分柱状图"""
        jars = [os.path.basename(jar) for jar, _ in ranked_scores]
        scores = [score for _, score in ranked_scores]

        plt.figure(figsize=(10, 6))
        bars = plt.bar(jars, scores, color='skyblue')

        # 添加数据标签
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2., height,
                     f'{height:.2f}',
                     ha='center', va='bottom')

        plt.xlabel('JAR文件')
        plt.ylabel('综合得分')
        plt.title('电梯调度程序综合得分排名')
        plt.xticks(rotation=45)
        plt.grid(True, axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig('scores_ranking.png')
        print("综合得分排名图已保存为 scores_ranking.png")

    def run_test_suite(self, n: int, m: int):
        """运行测试套件"""
        global total_tests, passed_tests, failed_tests, test_times, avg_completion_times, power_consumptions
        with lock:
            total_tests = n * len(TEST_JAR_FILES)
            passed_tests = 0
            failed_tests = 0
            test_times = {}
            avg_completion_times = {}
            power_consumptions = {}

        # 清空目录
        os.system(f'rm -rf {ERROR_OUTPUT_DIR}/*')
        os.system(f'rm -rf {INPUT_OUTPUT_DIR}/*')
        os.makedirs(ERROR_OUTPUT_DIR, exist_ok=True)
        os.makedirs(INPUT_OUTPUT_DIR, exist_ok=True)

        print(f"\n=== 开始测试套件 ===")
        print(f"总测试次数: {n}")
        print(f"每次测试请求数: {m}")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"输入数据将保存到: {INPUT_OUTPUT_DIR}/")
        print(f"错误用例将保存到: {ERROR_OUTPUT_DIR}/")
        print(f"超时设置: {TIMEOUT_SECONDS}秒")

        test_range = range(1, n + 1)
        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            futures = []
            for i in test_range:
                futures.append(executor.submit(self.run_test, m, i))

            for future in futures:
                results = future.result()
                self.update_stats(results, i)

        with lock:
            total_time = time.time() - self.start_time if self.start_time else 0

            # 绘制三个独立的图表
            self.plot_runtime()
            self.plot_completion_time()
            self.plot_power_consumption()

            # 输出各项指标排名
            self.print_rankings()

            # 计算并显示综合得分
            ranked_scores = self.calculate_scores()
            self.plot_scores(ranked_scores)

            print("\n=== 综合得分排名 ===")
            for rank, (jar, score) in enumerate(ranked_scores, 1):
                print(f"{rank}. {os.path.basename(jar)}: {score:.2f}分")

        print(f"\n=== 测试套件完成 ===")
        print(f"总测试次数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        accuracy = passed_tests / (failed_tests + passed_tests) * 100 if total_tests else 0.0
        print(f"正确率: {accuracy:.1f}%")

        if accuracy == 100.0:
            print("恭喜！所有测试用例全部通过！")


def main():
    print("=== 自动评测机 ===")
    print(f"将测试的JAR文件: {', '.join(TEST_JAR_FILES)}")
    print(f"测试次数: {DEFAULT_TEST_COUNT}")
    print(f"每次测试请求数: {DEFAULT_REQUEST_COUNT}")
    print(f"超时设置: {TIMEOUT_SECONDS}秒")
    os.system('rm -f test_input*.txt')

    evaluator = TestEvaluator()
    evaluator.run_test_suite(DEFAULT_TEST_COUNT, DEFAULT_REQUEST_COUNT)
    os.system('rm -f test_output*')


if __name__ == "__main__":
    # 设置中文字体支持
    matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    matplotlib.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

    main()