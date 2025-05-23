import subprocess
import time
import os
import sys
from typing import List, Tuple, Dict, Set, Optional
from datetime import datetime
import re
import threading
import concurrent.futures
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import math
import traceback # Added for better error reporting
import matplotlib.font_manager # Import font_manager explicitly

# --- Configuration Items ---
TEST_JAR_FILES = [#'zjy.jar'
                  #'lyf.jar'
                  # 'zjy_100.jar',
                  # 'zjy_50.jar',
                  # 'zjy_20.jar',
                  # 'jyx.jar',
                  # 'hzy.jar'
                  'tianshuxing.jar'
                  ]
DEFAULT_TEST_COUNT = 200
DEFAULT_PASSENGER_COUNT = 61 # Adjusted default for mixed requests
DEFAULT_SCHE_COMMAND_COUNT = 6 # Adjusted default
DEFAULT_UPDATE_COMMAND_COUNT = 3 # Adjusted default for UPDATE commands
ERROR_OUTPUT_DIR = 'error_cases_hw6_update' # Updated directory name
INPUT_OUTPUT_DIR = 'test_inputs_hw6_update'
SINGLE_INSTANCE_TEST = False # Set to True to run only 'test.txt' once
MAX_THREADS = 6
TIMEOUT_SECONDS = 200
# Updated Data Generator Script Assumption:
# Assumes data_generator.py now takes 3 arguments: passenger_count, sche_command_count, update_command_count
DATA_GENERATOR_SCRIPT = 'data_generator.py' # Assuming it's in the same dir or PATH

ELEVATOR_COUNT = 6
FLOOR_MAP = {name: i for i, name in enumerate(['B4', 'B3', 'B2', 'B1', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7'])}
FLOOR_NAMES = {i: name for name, i in FLOOR_MAP.items()}
NUM_FLOORS = len(FLOOR_MAP)
DEFAULT_MOVE_TIME = 0.4  # Default speed: 0.4s per floor
UPDATED_MOVE_TIME = 0.2  # Speed after UPDATE-END
DOOR_TIME = 0.4 # Minimum time door stays open (open -> close) for standard ops
MAX_CAPACITY = 6
EPSILON = 1e-9
# HW6 Constants
SCHE_MAX_RESPONSE_TIME = 6.0 # Max time from ACCEPT to END
SCHE_DOOR_HOLD_TIME = 1.0 # Time door must stay open at SCHE target
SCHE_MAX_ARRIVES_BEFORE_BEGIN = 2 # Max ARRIVEs between ACCEPT and BEGIN
UPDATE_MAX_RESPONSE_TIME = 6.0 # Max time from UPDATE-ACCEPT to UPDATE-END
UPDATE_MAX_ARRIVES_BEFORE_BEGIN = 2 # Max ARRIVEs for EACH elevator between ACCEPT and BEGIN
UPDATE_DURATION_MIN = 1.0 # Minimum time between UPDATE-BEGIN and UPDATE-END

# --- Global State (Managed with Lock) ---
total_tests = 0
passed_tests = 0
failed_tests = 0 # Note: This specific variable isn't used directly in final report, derived instead
test_times: Dict[str, List[float]] = {}             # jar -> list of runtimes (seconds)
avg_completion_times: Dict[str, List[float]] = {}   # jar -> list of avg WT (seconds)
power_consumptions: Dict[str, List[float]] = {}     # jar -> list of total W (units)
lock = threading.Lock()

# ---------------------------------------------------------------------------
# calculate_scores() function remains largely the same, as it operates on
# the aggregated performance metrics (WT, Power, Time) which are still relevant.
# No changes needed here unless scoring weights are adjusted.
# ---------------------------------------------------------------------------
def calculate_scores():
    """Calculates composite score (max 15) based on avg valid WT, Power, Time for HW6."""
    # Create local copies for calculation
    with lock: # Ensure thread-safe access to global state
        local_test_times = {k: list(v) for k, v in test_times.items()}
        local_avg_completion_times = {k: list(v) for k, v in avg_completion_times.items()}
        local_power_consumptions = {k: list(v) for k, v in power_consumptions.items()}

    time_avgs, completion_avgs, power_avgs = {}, {}, {}
    valid_jars_for_scoring = set() # JARs with at least one valid WT or Power score

    for jar in TEST_JAR_FILES:
        # Filter valid numerical data, excluding NaN/Inf
        valid_times = [t for t in local_test_times.get(jar, []) if isinstance(t, (int, float)) and not math.isnan(t) and not math.isinf(t) and t > 0]
        valid_wts = [wt for wt in local_avg_completion_times.get(jar, []) if wt is not None and not math.isnan(wt) and not math.isinf(wt)]
        valid_powers = [p for p in local_power_consumptions.get(jar, []) if p is not None and not math.isnan(p) and not math.isinf(p)]

        # Mark JAR as valid for scoring if it has *any* valid performance metric
        if valid_wts or valid_powers:
             valid_jars_for_scoring.add(jar)

        # Calculate averages, default to infinity if no valid data
        time_avgs[jar] = np.mean(valid_times) if valid_times else float('inf')
        completion_avgs[jar] = np.mean(valid_wts) if valid_wts else float('inf')
        power_avgs[jar] = np.mean(valid_powers) if valid_powers else float('inf')

    if not valid_jars_for_scoring:
        print("警告: 没有JAR文件有成功通过的测试点，无法计算性能得分。")
        # Return all JARs with score 0, sorted by name
        return sorted([(jar, 0.0) for jar in TEST_JAR_FILES], key=lambda item: os.path.basename(item[0]))

    # --- Calculate Baselines (Min/Max) based ONLY on valid JARs ---
    def calculate_robust_baselines(values_dict):
        # Filter values from JARs that had at least one valid perf score and whose avg is not Inf/NaN
        vals = [v for jar, v in values_dict.items() if jar in valid_jars_for_scoring and not math.isinf(v) and not math.isnan(v)]
        if not vals: return float('inf'), float('-inf') # No valid values found across all valid JARs
        Xmin, Xmax = np.min(vals), np.max(vals)
        # Add epsilon if min and max are identical to avoid division by zero
        return (Xmin, Xmax) if abs(Xmax - Xmin) >= EPSILON else (Xmin, Xmin + EPSILON)

    # --- Normalization Function (Score 0-1, lower value is better -> higher score) ---
    def normalize_score(value, base_min, base_max):
        # Handle invalid inputs (value, or baselines)
        if value is None or math.isinf(value) or math.isnan(value): return 0.0
        if math.isinf(base_min) or math.isinf(base_max) or math.isnan(base_min) or math.isnan(base_max): return 0.0
        # Handle case where all valid values were the same
        if abs(base_max - base_min) < EPSILON:
            return 1.0 if abs(value - base_min) < EPSILON else 0.0 # Score 1 if at the single value, 0 otherwise

        # Clamp value to be within baseline range before normalization
        clamped_value = max(base_min, min(base_max, value))
        # Normalize: (Max - Value) / (Max - Min)
        score = (base_max - clamped_value) / (base_max - base_min)
        # Ensure score is within [0, 1] bounds due to potential float issues
        return max(0.0, min(1.0, score))

    # Calculate baselines using the helper
    time_base_min, time_base_max = calculate_robust_baselines(time_avgs)
    completion_base_min, completion_base_max = calculate_robust_baselines(completion_avgs)
    power_base_min, power_base_max = calculate_robust_baselines(power_avgs)

    # --- Calculate Weighted Score for each JAR ---
    scores = {}
    # Weights (adjust as needed)
    W_WT, W_POWER, W_TIME = 0.45, 0.35, 0.20
    MAX_SCORE = 15.0 # Max possible score

    for jar in TEST_JAR_FILES:
        # Only calculate score if JAR had valid performance data
        if jar in valid_jars_for_scoring:
            t_avg = time_avgs.get(jar, float('inf'))
            wt_avg = completion_avgs.get(jar, float('inf'))
            w_avg = power_avgs.get(jar, float('inf'))

            # Normalize each component
            norm_time = normalize_score(t_avg, time_base_min, time_base_max)
            norm_wt = normalize_score(wt_avg, completion_base_min, completion_base_max)
            norm_power = normalize_score(w_avg, power_base_min, power_base_max)

            # Calculate combined score
            combined_score = MAX_SCORE * (W_TIME * norm_time + W_WT * norm_wt + W_POWER * norm_power)
            # Final score is clamped between 0 and MAX_SCORE
            scores[jar] = max(0.0, min(MAX_SCORE, combined_score))
        else:
             # Assign score 0 if JAR never passed any test validly for WT/Power
             scores[jar] = 0.0

    # Return sorted list: Highest score first, then by JAR name
    return sorted(scores.items(), key=lambda item: (-item[1], os.path.basename(item[0])))


class TestEvaluator:
    def __init__(self):
        self.start_time = time.time()
        # Ensure directories exist
        os.makedirs(ERROR_OUTPUT_DIR, exist_ok=True)
        os.makedirs(INPUT_OUTPUT_DIR, exist_ok=True)
        # State specific to a single validation run
        self.current_errors: List[str] = []
        self.events: List[Dict] = [] # Parsed output events for the current validation
        self.elevators: Dict[int, Dict] = {} # Elevator state tracked during validation
        self.passenger_states: Dict[int, Dict] = {} # Passenger state tracked during validation
        self.input_passengers: Dict[int, Dict] = {} # Store parsed passenger requests
        self.input_sche_commands: List[Dict] = [] # Store parsed SCHE commands
        self.input_update_commands: List[Dict] = [] # Store parsed UPDATE commands

        # --- State for UPDATE validation ---
        # Track which ACCEPT pairs have seen BEGIN/END to enforce Rule 1
        # Key: (min(e1, e2), max(e1, e2), target_floor), Value: {'begin_seen': bool, 'end_seen': bool, 'accept_time': float}
        self.processed_update_accepts: Dict[Tuple[int, int, str], Dict] = {}


    def print_red(self, text: str):
        """Prints text in red to stderr."""
        sys.stderr.write(f"\033[91m{text}\033[0m\n"); sys.stderr.flush()

    def print_green(self, text: str):
        """Prints text in green to stdout."""
        sys.stdout.write(f"\033[92m{text}\033[0m\n"); sys.stdout.flush()

    def print_info(self, text: str):
        """Prints text in blue to stdout."""
        sys.stdout.write(f"\033[94m{text}\033[0m\n"); sys.stdout.flush()

    def generate_input_data(self, passenger_count: int, sche_command_count: int, update_command_count: int) -> List[str]:
        """Generates input data using the specified script or reads from test.txt if SINGLE_INSTANCE_TEST is True."""
        if SINGLE_INSTANCE_TEST:
            try:
                with open('test.txt', 'r', encoding='utf-8') as f:
                    self.print_info("单例测试模式: 从 test.txt 读取输入...")
                    return [l.strip() for l in f if l.strip()]
            except FileNotFoundError:
                self.print_red("错误: 单例测试模式开启，但未找到 'test.txt' 文件。"); sys.exit(1)
            except Exception as e:
                 self.print_red(f"读取 'test.txt' 时发生错误: {e}"); sys.exit(1)

        # Generate data using the script - Now expects 3 counts
        cmd = [sys.executable, DATA_GENERATOR_SCRIPT,
               str(passenger_count), str(sche_command_count), str(update_command_count)]
        try:
            self.print_info(f"执行数据生成脚本: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8')
            # Debug: Print first few lines of generated data
            # generated_lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
            # print("DEBUG Data Generator Output (first 5 lines):", file=sys.stderr)
            # for line in generated_lines[:5]: print(f"  {line}", file=sys.stderr)
            # print("---", file=sys.stderr)
            return [l.strip() for l in result.stdout.splitlines() if l.strip()]
        except FileNotFoundError:
            self.print_red(f"错误: 未找到数据生成脚本 '{DATA_GENERATOR_SCRIPT}'。请确保它在当前目录或系统PATH中。"); sys.exit(1)
        except subprocess.CalledProcessError as e:
            self.print_red(f"数据生成脚本执行错误 (返回码 {e.returncode}):\n--- STDOUT ---\n{e.stdout}\n--- STDERR ---\n{e.stderr}"); sys.exit(1)
        except Exception as e:
            self.print_red(f"生成输入数据时发生未知错误: {e}"); sys.exit(1)

    # run_jar_program remains the same as before
    def run_jar_program(self, input_data: List[str], test_num: int, jar_file: str) -> Tuple[str, bool, float]:
        """Runs a JAR file with given input, saves input/output, handles timeout, returns output, success status, and time."""
        base_name = f"test_{test_num}_{os.path.basename(jar_file).replace('.jar', '')}"
        input_filename = os.path.join(INPUT_OUTPUT_DIR, f"{base_name}_input.txt")
        output_filename = os.path.join(INPUT_OUTPUT_DIR, f"{base_name}_output.txt")

        # Save input data
        try:
            with open(input_filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(input_data))
        except IOError as e:
            self.print_red(f"无法写入输入文件 {input_filename}: {e}")
            return "", False, 0.0

        # Command modified to handle paths with spaces correctly
        cmd = ['java', '-jar', jar_file]
        start_proc_time = time.time()
        process = None # Initialize process to None
        thread_name = threading.current_thread().name
        success = False
        elapsed = 0.0
        stderr_output = ""

        try:
            self.print_info(f"[{thread_name}] 执行命令: java -jar \"{jar_file}\" < \"{input_filename}\" > \"{output_filename}\" (Timeout: {TIMEOUT_SECONDS}s)")

            with open(input_filename, 'r', encoding='utf-8') as infile, \
                 open(output_filename, 'w', encoding='utf-8') as outfile:

                process = subprocess.Popen(cmd, stdin=infile, stdout=outfile, stderr=subprocess.PIPE)
                try:
                    # Use communicate to properly wait and get stderr/stdout
                    # Decoding stderr with appropriate encoding and error handling
                    stdout_bytes, stderr_bytes = process.communicate(timeout=TIMEOUT_SECONDS)
                    elapsed = time.time() - start_proc_time
                    return_code = process.returncode
                    success = (return_code == 0)
                    # Try decoding stderr with common encodings, default to utf-8 with replacement on errors
                    try:
                        stderr_output = stderr_bytes.decode(sys.stderr.encoding or 'utf-8', errors='ignore')
                    except (UnicodeDecodeError, TypeError):
                        try:
                             stderr_output = stderr_bytes.decode('gbk', errors='ignore')
                        except (UnicodeDecodeError, TypeError):
                             stderr_output = str(stderr_bytes, errors='ignore') # Last resort: lossy string conversion

                    process = None # Process finished

                    if not success:
                        self.print_red(
                            f"[{thread_name}] 程序 {os.path.basename(jar_file)} 运行时错误 (返回码: {return_code}):\n--- STDERR ---\n{stderr_output}\n------------")

                except subprocess.TimeoutExpired:
                    elapsed = time.time() - start_proc_time # Record time until timeout triggered
                    self.print_red(
                        f"[{thread_name}] 程序 {os.path.basename(jar_file)} 运行超时 (>{TIMEOUT_SECONDS}s)，已终止 (PID: {process.pid if process else 'N/A'}).")
                    if process:
                        try:
                            process.kill() # Ensure process is terminated
                            # Try to capture any final stderr after kill signal
                            # Wait briefly to allow stderr buffer to flush after kill
                            time.sleep(0.1)
                            _, stderr_after_kill_bytes = process.communicate()
                            try:
                                stderr_output += "\n--- Stderr after Kill ---\n" + stderr_after_kill_bytes.decode(sys.stderr.encoding or 'utf-8', errors='ignore')
                            except (UnicodeDecodeError, TypeError):
                                stderr_output += "\n--- Stderr after Kill (decoding error) ---\n" + str(stderr_after_kill_bytes, errors='ignore')
                        except Exception as kill_err:
                            self.print_red(f"[{thread_name}] 终止超时进程时出错: {kill_err}")
                    success = False
                    elapsed = TIMEOUT_SECONDS # Report timeout duration

        except FileNotFoundError:
             self.print_red(f"[{thread_name}] 错误: 找不到 Java 可执行文件。请确保 Java 已安装并配置在系统 PATH 中。")
             success = False
             elapsed = time.time() - start_proc_time # Record failure time
        except Exception as e:
            elapsed = time.time() - start_proc_time
            self.print_red(f"[{thread_name}] 执行 {os.path.basename(jar_file)} 时发生意外错误: {e}")
            self.print_red(traceback.format_exc())
            success = False
            if process and process.poll() is None: # If process still running after unexpected error
                 try: process.kill()
                 except Exception: pass # Ignore errors during cleanup kill

        # Read output file regardless of success/failure for debugging
        output = ""
        if os.path.exists(output_filename):
            try:
                with open(output_filename, 'r', encoding='utf-8') as f:
                    output = f.read()
            except Exception as e:
                self.print_red(f"读取输出文件 {output_filename} 时出错: {e}")
        elif success:
            self.print_red(f"警告: 成功运行但未找到输出文件 {output_filename}")
        else: # Failed run, output file might not exist or be empty
            self.print_info(f"[{thread_name}] 程序运行失败，未找到或无法读取输出文件 {output_filename}")


        self.print_info(
            f"[{thread_name}] === 程序 {os.path.basename(jar_file)} {'正常' if success else '异常'}结束 (耗时 {elapsed:.2f}s) ===")
        # Add stderr to output if run failed and stderr is informative
        if not success and stderr_output and not output:
            output = f"[程序运行失败，未生成标准输出]\n--- STDERR ---\n{stderr_output}"
        elif not success and stderr_output:
             output += f"\n\n--- STDERR ---\n{stderr_output}"


        return output, success, elapsed

    # floor_to_num, num_to_floor, floor_distance remain the same
    def floor_to_num(self, floor_str: str) -> Optional[int]:
        return FLOOR_MAP.get(floor_str)

    def num_to_floor(self, floor_num: int) -> Optional[str]:
        return FLOOR_NAMES.get(floor_num)

    def floor_distance(self, floor1: str, floor2: str) -> int:
        n1, n2 = self.floor_to_num(floor1), self.floor_to_num(floor2)
        return abs(n1 - n2) if n1 is not None and n2 is not None else float('inf')

    def add_error(self, msg: str):
        """Adds a validation error message to the current list."""
        self.current_errors.append(msg)
        # self.print_red(f"错误: {msg}") # Optional immediate print

    def _parse_input_data(self, input_data: List[str]) -> bool:
        """
        Parses input lines, handling PRI, SCHE-command, and UPDATE requests.
        Stores parsed data in self.input_passengers, self.input_sche_commands, self.input_update_commands.
        Returns True if parsing succeeded without critical errors, False otherwise.
        """
        self.input_passengers = {}
        self.input_sche_commands = []
        self.input_update_commands = [] # Initialize list for UPDATE commands
        last_ts = -1.0
        has_any_request = False

        for line_num, line in enumerate(input_data, 1):
            timestamp = None
            parsed_this_line = False

            # Regex for PRI: [ time ] id-PRI-priority-FROM-floor-TO-floor
            match_pri = re.match(r'\[\s*(\d+\.\d+)\s*\]\s*(\d+)\s*-\s*PRI\s*-\s*(\d+)\s*-\s*FROM\s*-\s*([BF]\d+)\s*-\s*TO\s*-\s*([BF]\d+)', line)
            # Regex for SCHE-command: [ time ] SCHE-elevator_id-speed-target_floor
            match_sche_cmd = re.match(r'\[\s*(\d+\.\d+)\s*\]\s*SCHE\s*-\s*(\d+)\s*-\s*(\d+\.\d+)\s*-\s*([BF]\d+)', line)
            # Regex for UPDATE-command: [ time ] UPDATE-e1-e2-target_floor
            match_update_cmd = re.match(r'\[\s*(\d+\.\d+)\s*\]\s*UPDATE\s*-\s*(\d+)\s*-\s*(\d+)\s*-\s*([BF]\d+)', line) # Added UPDATE regex

            if match_pri:
                parsed_this_line = True
                ts_str, pid_str, pri_str, from_f, to_f = match_pri.groups()
                try:
                    timestamp = float(ts_str)
                    pid = int(pid_str)
                    priority = int(pri_str)
                    if pid in self.input_passengers:
                        self.add_error(f"输入行 {line_num}: 重复乘客ID {pid} -> '{line}'"); return False
                    if self.floor_to_num(from_f) is None:
                        self.add_error(f"输入行 {line_num}: PRI无效起始楼层 '{from_f}' -> '{line}'"); return False
                    if self.floor_to_num(to_f) is None:
                         self.add_error(f"输入行 {line_num}: PRI无效目标楼层 '{to_f}' -> '{line}'"); return False
                    if from_f == to_f:
                        self.add_error(f"输入行 {line_num}: PRI起始楼层与目标楼层相同 '{from_f}' -> '{line}'"); return False
                    if not (1 <= priority <= 100):
                         self.print_info(f"输入行 {line_num}: 警告 - PRI无效优先级 {priority} (允许范围 1-100), 但通常不直接使用 -> '{line}'")

                    self.input_passengers[pid] = {
                        'id': pid, 'from_floor': from_f, 'to_floor': to_f,
                        'request_time': timestamp, 'priority': priority,
                    }
                    has_any_request = True
                except ValueError:
                    self.add_error(f"输入行 {line_num}: PRI解析数值错误: '{line}'"); return False

            elif match_sche_cmd:
                parsed_this_line = True
                ts_str, eid_str, speed_str, floor_f = match_sche_cmd.groups()
                try:
                    timestamp = float(ts_str)
                    eid = int(eid_str)
                    speed = float(speed_str)
                    if not (1 <= eid <= ELEVATOR_COUNT):
                        self.add_error(f"输入行 {line_num}: SCHE指令无效电梯ID {eid} (允许范围 1-{ELEVATOR_COUNT}) -> '{line}'"); return False
                    if speed <= 0 + EPSILON:
                        self.add_error(f"输入行 {line_num}: SCHE指令无效速度 {speed:.4f} (必须为正) -> '{line}'"); return False
                    if self.floor_to_num(floor_f) is None:
                        self.add_error(f"输入行 {line_num}: SCHE指令无效目标楼层 '{floor_f}' -> '{line}'"); return False

                    self.input_sche_commands.append({
                        'time': timestamp, 'elevator_id': eid, 'speed': speed, 'target_floor': floor_f, 'line': line_num
                    })
                    has_any_request = True
                except ValueError:
                    self.add_error(f"输入行 {line_num}: SCHE指令解析数值错误: '{line}'"); return False

            elif match_update_cmd: # Handle UPDATE input
                parsed_this_line = True
                ts_str, e1_str, e2_str, floor_f = match_update_cmd.groups()
                try:
                    timestamp = float(ts_str)
                    e1 = int(e1_str)
                    e2 = int(e2_str)
                    if not (1 <= e1 <= ELEVATOR_COUNT) or not (1 <= e2 <= ELEVATOR_COUNT):
                         self.add_error(f"输入行 {line_num}: UPDATE指令无效电梯ID {e1}或{e2} (允许范围 1-{ELEVATOR_COUNT}) -> '{line}'"); return False
                    if e1 == e2:
                         self.add_error(f"输入行 {line_num}: UPDATE指令两个电梯ID相同 ({e1}) -> '{line}'"); return False
                    # Validate UPDATE target floor - must be B2 to F5 according to generator
                    # If generator changes, update this check. Assuming SCHE_TARGET_FLOORS is the valid set.
                    if floor_f not in ['B2', 'B1', 'F1', 'F2', 'F3', 'F4', 'F5']: # Check against allowed UPDATE floors
                         self.add_error(f"输入行 {line_num}: UPDATE指令无效目标/换乘楼层 '{floor_f}' (允许范围 B2-F5) -> '{line}'"); return False

                    self.input_update_commands.append({
                        'time': timestamp, 'elevator_id_A': e1, 'elevator_id_B': e2, 'target_floor': floor_f, 'line': line_num
                    })
                    has_any_request = True
                except ValueError:
                    self.add_error(f"输入行 {line_num}: UPDATE指令解析数值错误: '{line}'"); return False


            elif line.strip() and not re.match(r'\[\s*(\d+\.\d+)\s*\]\s*SCHE\s*-\s*[BF]\d+\s*-\s*(UP|DOWN)', line): # Ignore old SCHE-dir format
                # Non-empty line that didn't match known formats (and isn't old SCHE-dir)
                self.add_error(f"输入行 {line_num}: 无法解析的格式: '{line}'"); return False
            # else: ignore empty lines or old SCHE-dir lines

            # Check timestamp monotonicity across all parsed lines
            if timestamp is not None:
                 if timestamp < last_ts - EPSILON:
                     self.add_error(f"输入行 {line_num}: 时间戳非递减 ({timestamp:.4f} < {last_ts:.4f}) -> '{line}'"); return False
                 last_ts = timestamp

        # Check if any request was found at all
        if not has_any_request and not SINGLE_INSTANCE_TEST:
             is_zero_request_scenario = False
             if len(sys.argv) > 4: # script name + 3 counts
                 try:
                     if int(sys.argv[2]) == 0 and int(sys.argv[3]) == 0 and int(sys.argv[4]) == 0:
                         is_zero_request_scenario = True
                 except (IndexError, ValueError): pass

             if is_zero_request_scenario:
                 self.print_info("输入数据解析: 未找到任何请求 (符合预期，请求数量为0)。")
             else:
                 self.add_error("输入数据解析错误: 未找到任何有效的乘客(PRI)、调度(SCHE)或改造(UPDATE)请求。"); return False

        return True


    def _parse_output_data(self, jar_output: str) -> Optional[List[Dict]]:
        """Parses the JAR's output lines into structured event dictionaries, ignoring [LOG] lines."""
        events = []
        last_timestamp = -1.0
        # Add UPDATE patterns
        patterns = {
            'UPDATE_ACCEPT': re.compile(r'UPDATE-ACCEPT\s*-\s*(\d+)\s*-\s*(\d+)\s*-\s*([BF]\d+)'), # e1, e2, target_floor
            'UPDATE_BEGIN': re.compile(r'UPDATE-BEGIN\s*-\s*(\d+)\s*-\s*(\d+)'),                 # e1, e2
            'UPDATE_END': re.compile(r'UPDATE-END\s*-\s*(\d+)\s*-\s*(\d+)'),                   # e1, e2
            'SCHE_ACCEPT': re.compile(r'SCHE-ACCEPT\s*-\s*(\d+)\s*-\s*(\d+\.\d+)\s*-\s*([BF]\d+)'), # elevator_id, speed, target_floor
            'SCHE_BEGIN': re.compile(r'SCHE-BEGIN\s*-\s*(\d+)'), # elevator_id
            'SCHE_END': re.compile(r'SCHE-END\s*-\s*(\d+)'),      # elevator_id
            'RECEIVE': re.compile(r'RECEIVE\s*-\s*(\d+)\s*-\s*(\d+)'), # passenger_id, elevator_id
            'ARRIVE': re.compile(r'ARRIVE\s*-\s*([BF]\d+)\s*-\s*(\d+)'), # floor, elevator_id
            'OPEN': re.compile(r'OPEN\s*-\s*([BF]\d+)\s*-\s*(\d+)'),    # floor, elevator_id
            'CLOSE': re.compile(r'CLOSE\s*-\s*([BF]\d+)\s*-\s*(\d+)'),   # floor, elevator_id
            'IN': re.compile(r'IN\s*-\s*(\d+)\s*-\s*([BF]\d+)\s*-\s*(\d+)'), # passenger_id, floor, elevator_id
            'OUT': re.compile(r'(OUT-S|OUT-F)\s*-\s*(\d+)\s*-\s*([BF]\d+)\s*-\s*(\d+)'), # type(S/F), passenger_id, floor, elevator_id
        }
        for line_num, line in enumerate([l.strip() for l in jar_output.split('\n') if l.strip()], 1):
            # --- ADDED CHECK: Ignore lines containing [LOG] ---
            if '[LOG]' in line:
                continue
            # --- END ADDED CHECK ---

            match_ts = re.match(r'\[\s*(\d+\.\d+)\s*\](.*)', line)
            if not match_ts:
                self.add_error(f"输出格式错误 (无时间戳或格式不符): 第 {line_num} 行: '{line}'"); return None

            timestamp_str, rest = match_ts.groups()
            rest = rest.strip()
            try:
                timestamp = float(timestamp_str)
                if '.' not in timestamp_str or len(timestamp_str.split('.')[-1]) != 4:
                     is_integer_with_zeros = timestamp == int(timestamp) and timestamp_str.endswith('.0000')
                     is_float_with_trailing_zeros = (timestamp != int(timestamp) and len(timestamp_str.split('.')[-1]) == 4)
                     if not (is_integer_with_zeros or is_float_with_trailing_zeros):
                        self.add_error(f"输出格式错误 (时间戳非4位小数): 第 {line_num} 行 时间戳 '{timestamp_str}' in '{line}'"); return None
            except ValueError:
                self.add_error(f"输出格式错误 (无效时间戳 '{timestamp_str}'): 第 {line_num} 行: '{line}'"); return None

            if timestamp < last_timestamp - EPSILON:
                self.add_error(f"时间戳非递减错误: 第 {line_num} 行 {timestamp:.4f} < 上一行 {last_timestamp:.4f}"); return None
            last_timestamp = timestamp

            event_data = {'raw': line, 'timestamp': timestamp, 'line_num': line_num}
            matched_type = None
            match_event = None
            for etype, pattern in patterns.items():
                match = pattern.fullmatch(rest)
                if match:
                    matched_type = etype
                    match_event = match
                    break

            if not matched_type:
                if re.fullmatch(r'OUT\s*-\s*(\d+)\s*-\s*([BF]\d+)\s*-\s*(\d+)', rest):
                     self.add_error(f"输出格式错误: 使用了旧的 'OUT' 格式，应为 'OUT-S' 或 'OUT-F': 第 {line_num} 行 (事件部分: '{rest}')"); return None
                else:
                     self.add_error(f"无法解析的输出格式/事件类型: 第 {line_num} 行 (事件部分: '{rest}')"); return None

            event_data['event_type'] = matched_type.split('_')[0] # 'UPDATE', 'SCHE', 'ARRIVE', etc.

            groups = match_event.groups()
            try:
                # --- Field Parsing ---
                if matched_type == 'RECEIVE':
                    event_data['passenger_id'], event_data['elevator_id'] = map(int, groups)
                elif matched_type in ['ARRIVE', 'OPEN', 'CLOSE']:
                    event_data['floor'], event_data['elevator_id'] = groups[0], int(groups[1])
                elif matched_type == 'IN':
                    event_data['passenger_id'], event_data['floor'], event_data['elevator_id'] = int(groups[0]), groups[1], int(groups[2])
                elif matched_type == 'OUT':
                    out_subtype_str, pid_str, floor, eid_str = groups
                    event_data['sub_type'] = out_subtype_str.split('-')[1]
                    event_data['passenger_id'] = int(pid_str)
                    event_data['floor'] = floor
                    event_data['elevator_id'] = int(eid_str)
                elif matched_type == 'SCHE_ACCEPT':
                    event_data['sub_type'] = 'ACCEPT'
                    eid, speed_str, floor = groups
                    event_data['elevator_id'] = int(eid)
                    event_data['speed'] = float(speed_str)
                    event_data['target_floor'] = floor
                    if event_data['speed'] <= 0 + EPSILON:
                        self.add_error(f"输出解析错误: 无效SCHE速度 {event_data['speed']:.4f} in line {line_num}"); return None
                elif matched_type == 'SCHE_BEGIN':
                    event_data['sub_type'] = 'BEGIN'
                    event_data['elevator_id'] = int(groups[0])
                elif matched_type == 'SCHE_END':
                    event_data['sub_type'] = 'END'
                    event_data['elevator_id'] = int(groups[0])
                elif matched_type == 'UPDATE_ACCEPT':
                    event_data['sub_type'] = 'ACCEPT'
                    e1_str, e2_str, floor = groups
                    event_data['elevator_id_A'] = int(e1_str)
                    event_data['elevator_id_B'] = int(e2_str)
                    event_data['target_floor'] = floor
                    if event_data['elevator_id_A'] == event_data['elevator_id_B']:
                         self.add_error(f"输出解析错误: UPDATE-ACCEPT 电梯ID相同 {event_data['elevator_id_A']} in line {line_num}"); return None
                elif matched_type == 'UPDATE_BEGIN':
                    event_data['sub_type'] = 'BEGIN'
                    event_data['elevator_id_A'] = int(groups[0])
                    event_data['elevator_id_B'] = int(groups[1])
                    if event_data['elevator_id_A'] == event_data['elevator_id_B']:
                         self.add_error(f"输出解析错误: UPDATE-BEGIN 电梯ID相同 {event_data['elevator_id_A']} in line {line_num}"); return None
                elif matched_type == 'UPDATE_END':
                    event_data['sub_type'] = 'END'
                    event_data['elevator_id_A'] = int(groups[0])
                    event_data['elevator_id_B'] = int(groups[1])
                    if event_data['elevator_id_A'] == event_data['elevator_id_B']:
                         self.add_error(f"输出解析错误: UPDATE-END 电梯ID相同 {event_data['elevator_id_A']} in line {line_num}"); return None
                else:
                     self.add_error(f"内部解析错误: 未处理的匹配类型 '{matched_type}' in line {line_num}"); return None

                # --- Common Field Value Validation ---
                # Validate single elevator ID if present
                if 'elevator_id' in event_data:
                     eid = event_data['elevator_id']
                     if not (1 <= eid <= ELEVATOR_COUNT):
                         self.add_error(f"输出解析错误: 无效电梯ID {eid} (允许范围 1-{ELEVATOR_COUNT}) in line {line_num}"); return None
                # Validate elevator IDs A and B if present
                if 'elevator_id_A' in event_data:
                     eA = event_data['elevator_id_A']
                     eB = event_data['elevator_id_B']
                     if not (1 <= eA <= ELEVATOR_COUNT):
                         self.add_error(f"输出解析错误: 无效电梯A ID {eA} (允许范围 1-{ELEVATOR_COUNT}) in line {line_num}"); return None
                     if not (1 <= eB <= ELEVATOR_COUNT):
                         self.add_error(f"输出解析错误: 无效电梯B ID {eB} (允许范围 1-{ELEVATOR_COUNT}) in line {line_num}"); return None
                # Validate floor strings if present
                if 'floor' in event_data:
                    floor = event_data['floor']
                    if self.floor_to_num(floor) is None:
                         self.add_error(f"输出解析错误: 无效楼层 '{floor}' in line {line_num}"); return None
                # Validate target floor strings if present (SCHE or UPDATE)
                if 'target_floor' in event_data:
                     target_floor = event_data['target_floor']
                     if self.floor_to_num(target_floor) is None:
                         self.add_error(f"输出解析错误: 无效目标楼层 '{target_floor}' in line {line_num}"); return None
                     # Further check UPDATE target floor range if it's an UPDATE event
                     if event_data['event_type'] == 'UPDATE' and event_data['sub_type'] == 'ACCEPT':
                         if target_floor not in ['B2', 'B1', 'F1', 'F2', 'F3', 'F4', 'F5']:
                              self.add_error(f"输出解析错误: UPDATE-ACCEPT 无效目标/换乘楼层 '{target_floor}' (允许范围 B2-F5) in line {line_num}"); return None


                events.append(event_data)
            except (ValueError, IndexError, KeyError) as e: # Added KeyError
                self.add_error(f"输出数据字段解析/赋值错误 ({matched_type}): 第 {line_num} 行: '{line}' - 错误: {e}"); return None

        return events

    def _init_elevator_state(self, eid: int) -> Dict:
        """Initializes the state dictionary for a single elevator (HW6 + UPDATE version)."""
        return {
            'id': eid,              # Original elevator ID (1-6)
            'current_floor': 'F1',  # Start at F1
            'state': 'CLOSE',       # Door state: 'OPEN' or 'CLOSE'
            'passengers': set(),    # Set of passenger IDs currently inside
            'active_receives': set(), # Set of passenger IDs currently RECEIVED for this elevator (Rule 11)
            # --- Timestamps ---
            'last_arrive_time': 0.0,
            'last_open_time': 0.0,
            'last_close_time': 0.0,
            'last_move_start_time': 0.0,
            # --- Movement State ---
            'current_speed': DEFAULT_MOVE_TIME, # Speed for the *next* move
            'last_move_speed_used': DEFAULT_MOVE_TIME,
            # --- SCHE State ---
            'in_sche': False,
            'sche_accept_pending': False,
            'last_sche_accept_time': -1.0,
            'last_sche_accept_floor': None,
            'last_sche_accept_speed': None,
            'arrive_count_since_sche_accept': 0,
            'sche_begin_time': -1.0,
            'sche_target_floor': None,
            'sche_speed': None,
            'sche_hold_start_time': -1.0,
            # --- UPDATE State (New) ---
            'is_double_car': False,         # Is it currently part of an active pair?
            'double_car_role': None,        # 'A' or 'B' after UPDATE-END
            'partner_id': None,             # ID of the partner elevator
            'transfer_floor': None,         # The transfer floor defined by the UPDATE
            'in_update_process': False,     # Between UPDATE-BEGIN and UPDATE-END
            'update_accept_pending': False, # Received UPDATE-ACCEPT, waiting for BEGIN
            'last_update_accept_time': -1.0,# Timestamp of the relevant UPDATE-ACCEPT
            'last_update_accept_details': None, # Tuple: (e1, e2, target_floor) from the ACCEPT
            'arrive_count_since_update_accept': 0, # Arrives for *this* elevator since ACCEPT (Rule 3)
            'update_begin_time': -1.0,      # Timestamp of UPDATE-BEGIN
        }

    # --- Event Handlers ---
    # Modify existing handlers to check for UPDATE constraints (Rule 6, Rule 8)
    # Add new handler for UPDATE events

    def _handle_arrive(self, event, elevator):
        floor = event['floor']; timestamp = event['timestamp']; line_num = event['line_num']
        eid = elevator['id']

        # --- Rule 6 Check ---
        if elevator['in_update_process']:
            self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} ARRIVE: 处于 UPDATE 改造过程中 (BEGIN和END之间)，禁止移动 (ARRIVE)"); return False
        # --- End Rule 6 Check ---

        speed_used_for_this_move = elevator['current_speed']
        if elevator['state'] != 'CLOSE':
            self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} ARRIVE: 试图在门 '{elevator['state']}' 时移动到达 {floor}"); return False
        current_num = self.floor_to_num(elevator['current_floor'])
        new_num = self.floor_to_num(floor)
        if new_num is None or current_num is None:
             self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} ARRIVE: 内部错误 - 无效楼层编号 {floor} or {elevator['current_floor']}"); return False

        if abs(new_num - current_num) != 1:
             if new_num == current_num and abs(timestamp - elevator['last_move_start_time']) < EPSILON:
                 pass # Allow zero-time 'move' to same floor (e.g., immediately open after close)
             else:
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} ARRIVE: 非法移动 {elevator['current_floor']} -> {floor} (必须移动一层)"); return False
        else: # Normal one-floor move
            expected_move_time = speed_used_for_this_move
            move_start_time = elevator['last_move_start_time']
            time_diff = timestamp - move_start_time
            timing_tolerance = EPSILON * 10
            if time_diff < expected_move_time - timing_tolerance:
                self.add_error(
                    f"[{timestamp:.4f}] (Line {line_num}) E{eid} ARRIVE at {floor}: 移动太快 from {elevator['current_floor']}. "
                    f"耗时 {time_diff:.4f}s < 要求 {expected_move_time:.4f}s (速度: {speed_used_for_this_move:.4f}s/层). "
                    f"移动开始于 {move_start_time:.4f}"
                ); return False

            # --- Rule 3 & SCHE Arrive Count Check ---
            if elevator['sche_accept_pending']:
                elevator['arrive_count_since_sche_accept'] += 1
                if elevator['arrive_count_since_sche_accept'] > SCHE_MAX_ARRIVES_BEFORE_BEGIN:
                    self.add_error(
                        f"[{timestamp:.4f}] (Line {line_num}) E{eid} ARRIVE: SCHE-ACCEPT 后发生 > {SCHE_MAX_ARRIVES_BEFORE_BEGIN} 次 ARRIVE "
                        f"(自 {elevator['last_sche_accept_time']:.4f}) 仍未发出 SCHE-BEGIN"
                    ); return False
            if elevator['update_accept_pending']: # Check for UPDATE pending (Rule 3)
                 elevator['arrive_count_since_update_accept'] += 1
                 if elevator['arrive_count_since_update_accept'] > UPDATE_MAX_ARRIVES_BEFORE_BEGIN:
                     accept_details = elevator.get('last_update_accept_details', ('?','?','?'))
                     accept_time = elevator.get('last_update_accept_time', -1.0)
                     self.add_error(
                         f"[{timestamp:.4f}] (Line {line_num}) E{eid} ARRIVE: UPDATE-ACCEPT ({accept_details[0]}-{accept_details[1]}-{accept_details[2]} @ {accept_time:.4f}) 后发生 "
                         f"> {UPDATE_MAX_ARRIVES_BEFORE_BEGIN} 次 ARRIVE 仍未发出 UPDATE-BEGIN"
                     ); return False
            # --- End Arrive Count Check ---

            # --- Rule 8 Check (Double Car Movement) ---
            if elevator['is_double_car']:
                if elevator['partner_id'] is None or elevator['transfer_floor'] is None or elevator['double_car_role'] is None:
                     self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} ARRIVE: 内部状态错误 - 双轿厢状态不完整 (partner={elevator['partner_id']}, transfer={elevator['transfer_floor']}, role={elevator['double_car_role']})"); return False
                partner = self.elevators.get(elevator['partner_id'])
                if partner is None:
                     self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} ARRIVE: 内部状态错误 - 找不到伙伴电梯 {elevator['partner_id']} 的状态"); return False

                transfer_floor_num = self.floor_to_num(elevator['transfer_floor'])
                new_floor_num = self.floor_to_num(floor)

                # Range check
                if elevator['double_car_role'] == 'A' and new_floor_num < transfer_floor_num:
                     self.add_error(f"[{timestamp:.4f}] (Line {line_num}) 双轿厢 E{eid} (A角色, 换乘层 {elevator['transfer_floor']}) ARRIVE: 非法移动到下方楼层 {floor}"); return False
                if elevator['double_car_role'] == 'B' and new_floor_num > transfer_floor_num:
                     self.add_error(f"[{timestamp:.4f}] (Line {line_num}) 双轿厢 E{eid} (B角色, 换乘层 {elevator['transfer_floor']}) ARRIVE: 非法移动到上方楼层 {floor}"); return False

                # Collision/Crossing check (Check against partner's *current* floor)
                partner_floor_num = self.floor_to_num(partner['current_floor'])
                if partner_floor_num is None:
                     self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} ARRIVE: 内部状态错误 - 伙伴电梯 {elevator['partner_id']} 当前楼层 '{partner['current_floor']}' 无效"); return False

                # Check if the *new* state creates a conflict
                if elevator['double_car_role'] == 'A':
                    if new_floor_num <= partner_floor_num:
                        self.add_error(f"[{timestamp:.4f}] (Line {line_num}) 双轿厢冲突 E{eid} (A角色) ARRIVE at {floor}: 与伙伴 E{partner['id']} (B角色) 在 {partner['current_floor']} 或以下楼层发生冲突"); return False
                elif elevator['double_car_role'] == 'B':
                     if new_floor_num >= partner_floor_num:
                         self.add_error(f"[{timestamp:.4f}] (Line {line_num}) 双轿厢冲突 E{eid} (B角色) ARRIVE at {floor}: 与伙伴 E{partner['id']} (A角色) 在 {partner['current_floor']} 或以上楼层发生冲突"); return False
            # --- End Rule 8 Check ---

            # Update state after successful move validation
            elevator.update({
                'current_floor': floor, 'last_arrive_time': timestamp,
                'last_move_start_time': timestamp,
                'last_move_speed_used': speed_used_for_this_move
            })
            # Update passenger locations
            for pid in elevator['passengers']:
                if pid in self.passenger_states: self.passenger_states[pid]['current_floor'] = floor
                else: self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} ARRIVE: 内部状态错误 - 电梯内乘客 {pid} 不在乘客状态列表中")

        return True

    def _handle_open(self, event, elevator):
        floor = event['floor']; timestamp = event['timestamp']; line_num = event['line_num']
        eid = elevator['id']

        # --- Rule 6 Check ---
        if elevator['in_update_process']:
            self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} OPEN: 处于 UPDATE 改造过程中，禁止开门"); return False
        # --- End Rule 6 Check ---

        if elevator['state'] == 'OPEN':
            self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} OPEN at {floor}: 门已打开"); return False
        if elevator['current_floor'] != floor:
            self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} OPEN: 尝试在 {floor} 开门, 但电梯在 {elevator['current_floor']}"); return False
        min_open_time = max(elevator['last_arrive_time'], elevator['last_close_time'])
        if timestamp < min_open_time - EPSILON:
             self.add_error(
                 f"[{timestamp:.4f}] (Line {line_num}) E{eid} OPEN at {floor}: 开门时间 ({timestamp:.4f}) 早于 "
                 f"最近的到达 ({elevator['last_arrive_time']:.4f}) 或关门 ({elevator['last_close_time']:.4f})"
             ); return False
        if elevator['in_sche'] and floor != elevator['sche_target_floor']:
            self.add_error(
                f"[{timestamp:.4f}] (Line {line_num}) E{eid} OPEN at {floor}: SCHE 模式下 ({elevator['sche_target_floor']} 为目标) "
                f"禁止在非目标楼层开门"
            ); return False

        # --- Rule 8 Check (Double Car Opening Range) ---
        if elevator['is_double_car']:
             if elevator['transfer_floor'] is None or elevator['double_car_role'] is None:
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} OPEN: 内部状态错误 - 双轿厢状态不完整 (transfer={elevator['transfer_floor']}, role={elevator['double_car_role']})"); return False
             transfer_floor_num = self.floor_to_num(elevator['transfer_floor'])
             current_floor_num = self.floor_to_num(floor)
             if elevator['double_car_role'] == 'A' and current_floor_num < transfer_floor_num:
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) 双轿厢 E{eid} (A角色, 换乘层 {elevator['transfer_floor']}) OPEN: 禁止在换乘层以下楼层 {floor} 开门"); return False
             if elevator['double_car_role'] == 'B' and current_floor_num > transfer_floor_num:
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) 双轿厢 E{eid} (B角色, 换乘层 {elevator['transfer_floor']}) OPEN: 禁止在换乘层以上楼层 {floor} 开门"); return False
        # --- End Rule 8 Check ---

        elevator.update({'state': 'OPEN', 'last_open_time': timestamp})
        if elevator['in_sche'] and floor == elevator['sche_target_floor']:
             elevator['sche_hold_start_time'] = timestamp
        return True

    def _handle_close(self, event, elevator):
        floor = event['floor']; timestamp = event['timestamp']; line_num = event['line_num']
        eid = elevator['id']

        # --- Rule 6 Check ---
        if elevator['in_update_process']:
            self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} CLOSE: 处于 UPDATE 改造过程中，禁止关门"); return False
        # --- End Rule 6 Check ---

        if elevator['state'] == 'CLOSE':
            self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} CLOSE at {floor}: 门已关闭"); return False
        if elevator['current_floor'] != floor:
            self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} CLOSE: 尝试在 {floor} 关门, 但电梯在 {elevator['current_floor']}"); return False
        open_duration = timestamp - elevator['last_open_time']
        required_duration = DOOR_TIME
        is_at_sche_target = elevator['in_sche'] and floor == elevator['sche_target_floor']
        if is_at_sche_target:
            required_duration = SCHE_DOOR_HOLD_TIME
            if abs(elevator['sche_hold_start_time'] - elevator['last_open_time']) > EPSILON:
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} CLOSE: 内部状态错误 - SCHE 模式下关门时 hold_start_time ({elevator['sche_hold_start_time']:.4f}) 与 last_open_time ({elevator['last_open_time']:.4f}) 不符")

        duration_tolerance = EPSILON * 10
        if open_duration < required_duration - duration_tolerance:
            duration_type = "SCHE规定" if is_at_sche_target else "标准"
            self.add_error(
                f"[{timestamp:.4f}] (Line {line_num}) E{eid} CLOSE at {floor}: 开关门间隔太短 ({open_duration:.4f}s < {duration_type} {required_duration:.4f}s). "
                f"开门时间: {elevator['last_open_time']:.4f}"
            ); return False
        elevator.update({
            'state': 'CLOSE', 'last_close_time': timestamp,
            'last_move_start_time': timestamp
        })
        return True

    def _handle_in(self, event, elevator):
        pid = event['passenger_id']; floor = event['floor']
        timestamp = event['timestamp']; line_num = event['line_num']
        eid = elevator['id']

        # --- Rule 6 Check ---
        if elevator['in_update_process']:
            self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} IN P{pid}: 处于 UPDATE 改造过程中，禁止乘客进入"); return False
        # --- End Rule 6 Check ---

        if elevator['in_sche']:
            self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} IN P{pid}: SCHE 模式下禁止乘客进入"); return False

        # --- Rule 8 Check (Double Car Entry Range) ---
        if elevator['is_double_car']:
             if elevator['transfer_floor'] is None or elevator['double_car_role'] is None:
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} IN P{pid}: 内部状态错误 - 双轿厢状态不完整 (transfer={elevator['transfer_floor']}, role={elevator['double_car_role']})"); return False
             transfer_floor_num = self.floor_to_num(elevator['transfer_floor'])
             current_floor_num = self.floor_to_num(floor)
             passenger = self.passenger_states.get(pid)
             passenger_target_floor_num = self.floor_to_num(passenger['to_floor']) if passenger else None

             if passenger is None: # Check passenger exists first
                 if pid not in self.input_passengers:
                     self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} IN P{pid}: 乘客 {pid} 未在输入中定义"); return False
                 else: # Exists in input, maybe state tracking failed? Proceed cautiously.
                    self.print_info(f"警告: 乘客 {pid} 在输入中定义但无当前状态，继续检查进入 E{eid}")
                    self.passenger_states[pid] = {**self.input_passengers[pid], 'completed': False, 'current_floor': floor, 'in_elevator': False, 'elevator_id': None, 'complete_time': None, 'exited_sche_temp': False, 'temp_exit_floor': None}
                    passenger = self.passenger_states[pid]
                    passenger_target_floor_num = self.floor_to_num(passenger['to_floor'])

             if passenger_target_floor_num is None:
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} IN P{pid}: 内部错误 - 无法确定乘客 {pid} 的目标楼层"); return False

             # A car (>= transfer): Can only pick up passengers GOING TO >= transfer floor
             if elevator['double_car_role'] == 'A':
                 if current_floor_num < transfer_floor_num: # Should be caught by OPEN check, but redundant check
                      self.add_error(f"[{timestamp:.4f}] (Line {line_num}) 双轿厢 E{eid} (A角色) IN P{pid}: 尝试在非法区域 {floor} (<{elevator['transfer_floor']}) 让乘客进入"); return False
                 # Check passenger destination compatibility for Car A

             # B car (<= transfer): Can only pick up passengers GOING TO <= transfer floor
             if elevator['double_car_role'] == 'B':
                  if current_floor_num > transfer_floor_num: # Should be caught by OPEN check
                      self.add_error(f"[{timestamp:.4f}] (Line {line_num}) 双轿厢 E{eid} (B角色) IN P{pid}: 尝试在非法区域 {floor} (>{elevator['transfer_floor']}) 让乘客进入"); return False
                  # Check passenger destination compatibility for Car B
                  # --- End Rule 8 Check ---


        # --- Standard IN Checks (remain valid) ---
        if pid not in self.passenger_states: # Should have been handled above if double_car
             if pid not in self.input_passengers:
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} IN P{pid}: 乘客 {pid} 未在输入中定义"); return False
             else:
                 self.print_info(f"警告: 乘客 {pid} 在输入中定义，但未在当前状态中跟踪，允许进入 E{eid}")
                 self.passenger_states[pid] = { **self.input_passengers[pid], 'completed': False, 'current_floor': floor, 'in_elevator': False, 'elevator_id': None, 'complete_time': None, 'exited_sche_temp': False, 'temp_exit_floor': None}

        passenger = self.passenger_states[pid]
        if elevator['state'] != 'OPEN':
            self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} IN P{pid} at {floor}: 门 '{elevator['state']}' 时尝试进入"); return False
        if elevator['current_floor'] != floor:
            self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} IN P{pid}: 尝试在 {floor} 进入, 但电梯在 {elevator['current_floor']}"); return False
        passenger_logically_at_floor = (passenger['current_floor'] == floor)
        passenger_re_entering_after_outf = (passenger.get('exited_sche_temp', False) and passenger.get('temp_exit_floor') == floor)
        if not (passenger_logically_at_floor or passenger_re_entering_after_outf):
             self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} IN P{pid}: 乘客逻辑上不在楼层 {floor} (推断位置: {passenger['current_floor']}, 临时下车?: {passenger.get('exited_sche_temp', False)} @ {passenger.get('temp_exit_floor')}), 无法进入"); return False
        if passenger.get('in_elevator'):
            self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} IN P{pid}: 乘客已在电梯 {passenger.get('elevator_id', '?')} 内"); return False
        if pid in elevator['passengers']:
            self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} IN P{pid}: 乘客状态已在此电梯内 (内部集合不一致)"); return False
        if len(elevator['passengers']) >= MAX_CAPACITY:
            self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} IN P{pid}: 电梯已满 ({len(elevator['passengers'])}/{MAX_CAPACITY})"); return False
        if timestamp < elevator['last_open_time'] - EPSILON:
            self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} IN P{pid}: 进入时间 ({timestamp:.4f}) 早于 开门时间 ({elevator['last_open_time']:.4f})"); return False
        if elevator['last_close_time'] > elevator['last_open_time'] and timestamp > elevator['last_close_time'] + EPSILON :
             self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} IN P{pid}: 尝试在门已关闭后进入 (关门时间: {elevator['last_close_time']:.4f})"); return False
        # --- End Standard IN Checks ---

        elevator['passengers'].add(pid)
        passenger.update({'in_elevator': True, 'elevator_id': eid, 'exited_sche_temp': False, 'temp_exit_floor': None})
        return True


    def _handle_out(self, event, elevator):
        sub_type = event['sub_type']; pid = event['passenger_id']; floor = event['floor']
        timestamp = event['timestamp']; line_num = event['line_num']
        eid = elevator['id']

        # --- Rule 6 Check ---
        if elevator['in_update_process']:
            self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} OUT-{sub_type} P{pid}: 处于 UPDATE 改造过程中，禁止乘客离开"); return False
        # --- End Rule 6 Check ---

        # --- Standard OUT Pre-condition Checks ---
        if pid not in self.passenger_states:
             if pid not in self.input_passengers:
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} OUT-{sub_type} P{pid}: 乘客 {pid} 未在输入中定义"); return False
             else:
                  self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} OUT-{sub_type} P{pid}: 乘客 {pid} 在输入中定义，但未被成功跟踪状态"); return False
        passenger = self.passenger_states[pid]
        if elevator['state'] != 'OPEN':
             self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} OUT-{sub_type} P{pid} at {floor}: 门 '{elevator['state']}' 时尝试离开"); return False
        if elevator['current_floor'] != floor:
             self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} OUT-{sub_type} P{pid}: 尝试在 {floor} 离开, 但电梯在 {elevator['current_floor']}"); return False
        if not passenger.get('in_elevator') or passenger.get('elevator_id') != eid:
             other_eid_info = f" (状态显示在电梯 {passenger.get('elevator_id')})" if passenger.get('in_elevator') else " (状态显示不在电梯内)"
             self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} OUT-{sub_type} P{pid}: 乘客状态显示不在电梯 {eid} 内{other_eid_info}"); return False
        if pid not in elevator['passengers']:
             self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} OUT-{sub_type} P{pid}: 乘客状态与电梯内部乘客集合不一致"); return False
        if timestamp < elevator['last_open_time'] - EPSILON:
            self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} OUT-{sub_type} P{pid}: 离开时间 ({timestamp:.4f}) 早于 开门时间 ({elevator['last_open_time']:.4f})"); return False
        if elevator['last_close_time'] > elevator['last_open_time'] and timestamp > elevator['last_close_time'] + EPSILON :
             self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} OUT-{sub_type} P{pid}: 尝试在门已关闭后离开 (关门时间: {elevator['last_close_time']:.4f})"); return False
        # --- End Standard OUT Pre-condition Checks ---


        # --- Rule 8 Check (Double Car Exit Range) ---
        # Passengers should only exit within the valid range for that car
        if elevator['is_double_car']:
             if elevator['transfer_floor'] is None or elevator['double_car_role'] is None:
                  self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} OUT-{sub_type} P{pid}: 内部状态错误 - 双轿厢状态不完整 (transfer={elevator['transfer_floor']}, role={elevator['double_car_role']})"); return False
             transfer_floor_num = self.floor_to_num(elevator['transfer_floor'])
             current_floor_num = self.floor_to_num(floor)
             # A car should only let passengers out at >= transfer floor
             if elevator['double_car_role'] == 'A' and current_floor_num < transfer_floor_num:
                   self.add_error(f"[{timestamp:.4f}] (Line {line_num}) 双轿厢 E{eid} (A角色) OUT-{sub_type} P{pid}: 尝试在非法区域 {floor} (<{elevator['transfer_floor']}) 让乘客离开"); return False
             # B car should only let passengers out at <= transfer floor
             if elevator['double_car_role'] == 'B' and current_floor_num > transfer_floor_num:
                   self.add_error(f"[{timestamp:.4f}] (Line {line_num}) 双轿厢 E{eid} (B角色) OUT-{sub_type} P{pid}: 尝试在非法区域 {floor} (>{elevator['transfer_floor']}) 让乘客离开"); return False
        # --- End Rule 8 Check ---


        # --- Determine Correct OUT type (Rule: OUT-S/F based on destination match) ---
        final_destination_floor = passenger['to_floor']
        is_final_destination = (floor == final_destination_floor)
        required_out_type = 'S' if is_final_destination else 'F'
        if sub_type != required_out_type:
            reason = f"因为楼层 {floor} {'是' if is_final_destination else '不是'} 乘客的最终目的地 {final_destination_floor}"
            self.add_error(
                f"[{timestamp:.4f}] (Line {line_num}) E{eid} 使用了 OUT-{sub_type} P{pid} at {floor}: "
                f"判断应为 OUT-{required_out_type} ({reason})"
            ); return False
        # --- End OUT Type Check ---


        # --- Update State ---
        elevator['passengers'].remove(pid)
        passenger.update({'in_elevator': False, 'elevator_id': None, 'current_floor': floor})
        # --- Rule 11: Cancel RECEIVE on OUT ---
        if pid in elevator['active_receives']:
            elevator['active_receives'].remove(pid)
            # self.print_info(f"DEBUG: P{pid} removed from E{eid} active receives due to OUT at {timestamp:.4f}") # Optional debug

        if is_final_destination: # OUT-S
            if passenger['completed']:
                 self.print_info(f"[{timestamp:.4f}] (Line {line_num}) E{eid} OUT-S P{pid}: 乘客已标记为完成，但再次在目的地 {floor} 离开电梯 (警告)")
            passenger.update({'completed': True, 'complete_time': timestamp, 'exited_sche_temp': False})
        else: # OUT-F
            if passenger.get('exited_sche_temp'):
                 self.print_info(f"[{timestamp:.4f}] (Line {line_num}) E{eid} OUT-F P{pid}: 乘客已处于临时下车状态，再次在 {floor} (非目的地) 下车 (警告)")
            passenger.update({'completed': False, 'exited_sche_temp': True, 'temp_exit_floor': floor})

        return True


    def _handle_receive(self, event, elevator):
        pid = event['passenger_id']; timestamp = event['timestamp']; line_num = event['line_num']
        eid = elevator['id']

        # --- Rule 6 Check ---
        if elevator['in_update_process']:
            self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} RECEIVE P{pid}: 处于 UPDATE 改造过程中，禁止接收请求"); return False
        # --- End Rule 6 Check ---

        if elevator['in_sche']:
            self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} RECEIVE P{pid}: SCHE 模式下禁止接收新请求 (RECEIVE)"); return False
        if pid not in self.input_passengers:
             self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} RECEIVE P{pid}: 收到未知乘客ID {pid} 的请求 (不在输入中)"); return False

        # --- Rule 11 Implied Check: Should not RECEIVE if double-car and passenger destination incompatible ---
        if elevator['is_double_car']:
             if elevator['transfer_floor'] is None or elevator['double_car_role'] is None:
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} RECEIVE P{pid}: 内部状态错误 - 双轿厢状态不完整 (transfer={elevator['transfer_floor']}, role={elevator['double_car_role']})"); return False
             passenger = self.input_passengers.get(pid) # Check original request
             if passenger is None: # Should have been caught above, but double check
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} RECEIVE P{pid}: 内部错误 - 找不到输入乘客 {pid} 的信息"); return False

             transfer_floor_num = self.floor_to_num(elevator['transfer_floor'])
             passenger_target_floor_num = self.floor_to_num(passenger['to_floor'])

             if passenger_target_floor_num is None:
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} RECEIVE P{pid}: 内部错误 - 无法确定乘客 {pid} 的目标楼层 '{passenger['to_floor']}'"); return False

             # A car (>= transfer): Cannot RECEIVE passenger going below transfer
              # --- End Rule 11 Implied Check ---


        # --- Rule 11 State Update: Add to active receives ---
        elevator['active_receives'].add(pid)
        # self.print_info(f"DEBUG: P{pid} added to E{eid} active receives at {timestamp:.4f}") # Optional debug
        return True


    def _handle_sche(self, event, elevator):
        sub_type = event['sub_type']
        timestamp = event['timestamp']
        line_num = event['line_num']
        eid = elevator['id']

        # --- Rule 6 Check ---
        if elevator['in_update_process']:
             self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} SCHE-{sub_type}: 处于 UPDATE 改造过程中，禁止执行SCHE操作"); return False
        # --- End Rule 6 Check ---
        # --- Double Car Check ---
        if elevator['is_double_car']:
             self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} SCHE-{sub_type}: 双轿厢模式电梯，禁止执行SCHE操作"); return False
        # --- End Double Car Check ---

        if sub_type == 'ACCEPT':
            speed = event['speed']; target_floor = event['target_floor']
            if elevator['in_sche']:
                self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} SCHE-ACCEPT: 电梯当前正在执行SCHE任务 (始于 {elevator['sche_begin_time']:.4f}), 不能接受新SCHE请求"); return False
            if elevator['sche_accept_pending']:
                self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} SCHE-ACCEPT: 已有一个待处理的SCHE-ACCEPT请求 (自 {elevator['last_sche_accept_time']:.4f})"); return False
            # Prevent SCHE if UPDATE is pending for this elevator
            if elevator['update_accept_pending']:
                 accept_details = elevator.get('last_update_accept_details', ('?','?','?'))
                 accept_time = elevator.get('last_update_accept_time', -1.0)
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} SCHE-ACCEPT: 不能在有待处理的 UPDATE-ACCEPT ({accept_details[0]}-{accept_details[1]} @ {accept_time:.4f}) 时接受 SCHE 请求"); return False

            if self.floor_to_num(target_floor) is None:
                self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} SCHE-ACCEPT: 无效的目标楼层 '{target_floor}'"); return False
            if speed <= 0 + EPSILON:
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} SCHE-ACCEPT: 无效的速度 {speed:.4f}"); return False

            elevator.update({
                'sche_accept_pending': True, 'last_sche_accept_time': timestamp,
                'last_sche_accept_floor': target_floor, 'last_sche_accept_speed': speed,
                'arrive_count_since_sche_accept': 0
            })
            return True

        elif sub_type == 'BEGIN':
            if not elevator['sche_accept_pending']:
                self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} SCHE-BEGIN: 没有待处理的 SCHE-ACCEPT 请求"); return False
            if elevator['in_sche']:
                self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} SCHE-BEGIN: 电梯已处于SCHE模式 (自 {elevator['sche_begin_time']:.4f} 开始)"); return False
            if elevator['state'] != 'CLOSE':
                self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} SCHE-BEGIN: 必须在门关闭时开始SCHE模式 (当前: '{elevator['state']}')"); return False
            if timestamp < elevator['last_move_start_time'] - EPSILON:
                 self.add_error(
                     f"[{timestamp:.4f}] (Line {line_num}) E{eid} SCHE-BEGIN: 时间 ({timestamp:.4f}) 早于电梯可行动时间 "
                     f"({elevator['last_move_start_time']:.4f})"
                 ); return False
            if elevator['arrive_count_since_sche_accept'] > SCHE_MAX_ARRIVES_BEFORE_BEGIN:
                 self.add_error(
                     f"[{timestamp:.4f}] (Line {line_num}) E{eid} SCHE-BEGIN: 尝试开始SCHE，但在ACCEPT后已发生 "
                     f"{elevator['arrive_count_since_sche_accept']} 次 ARRIVE (超过允许的 {SCHE_MAX_ARRIVES_BEFORE_BEGIN})"
                 ); return False

            accepted_speed = elevator['last_sche_accept_speed']
            accepted_floor = elevator['last_sche_accept_floor']
            # --- Rule 11: Cancel RECEIVEs on SCHE-BEGIN ---
            if elevator['active_receives']:
                # self.print_info(f"DEBUG: E{eid} SCHE-BEGIN cancelling active receives: {elevator['active_receives']}") # Optional Debug
                elevator['active_receives'].clear()
            # --- End Rule 11 ---
            elevator.update({
                'in_sche': True, 'sche_accept_pending': False, 'sche_begin_time': timestamp,
                'current_speed': accepted_speed, 'sche_speed': accepted_speed,
                'sche_target_floor': accepted_floor,
                'arrive_count_since_sche_accept': 0,
                'sche_hold_start_time': -1.0,
                'last_move_start_time': timestamp
            })
            return True

        elif sub_type == 'END':
            if not elevator['in_sche']:
                self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} SCHE-END: 电梯不在SCHE模式，无法结束"); return False
            if elevator['current_floor'] != elevator['sche_target_floor']:
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} SCHE-END: 必须在SCHE目标楼层 ({elevator['sche_target_floor']}) 结束 (当前: {elevator['current_floor']})"); return False
            if elevator['state'] != 'CLOSE':
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} SCHE-END: 必须在门关闭时结束SCHE模式 (当前: '{elevator['state']}')"); return False
            if elevator['passengers']:
                 p_list = sorted(list(elevator['passengers']))
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} SCHE-END: 临时调度结束时电梯必须为空 (内有: {p_list})"); return False
            if timestamp < elevator['last_close_time'] - EPSILON:
                 self.add_error(
                     f"[{timestamp:.4f}] (Line {line_num}) E{eid} SCHE-END: 结束时间 ({timestamp:.4f}) 早于 "
                     f"在目标楼层关门时间 ({elevator['last_close_time']:.4f})"
                 ); return False
            if elevator['last_sche_accept_time'] < 0:
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} SCHE-END: 内部状态错误 - 找不到对应的SCHE-ACCEPT时间"); return False
            response_time = timestamp - elevator['last_sche_accept_time']
            if response_time > SCHE_MAX_RESPONSE_TIME + EPSILON:
                 self.add_error(
                     f"[{timestamp:.4f}] (Line {line_num}) E{eid} SCHE-END: SCHE响应时间 ({response_time:.4f}s) "
                     f"超过最大允许值 {SCHE_MAX_RESPONSE_TIME}s "
                     f"(自 ACCEPT @ {elevator['last_sche_accept_time']:.4f})"
                 ); return False
            # Reset state
            elevator.update({
                'in_sche': False, 'current_speed': DEFAULT_MOVE_TIME, # Reset speed
                'sche_begin_time': -1.0, 'sche_target_floor': None, 'sche_speed': None,
                'sche_hold_start_time': -1.0, 'last_sche_accept_time': -1.0,
                'last_sche_accept_floor': None, 'last_sche_accept_speed': None,
            })
            return True
        else:
             self.add_error(f"[{timestamp:.4f}] (Line {line_num}) E{eid} SCHE: 未知的SCHE子类型 '{sub_type}'"); return False

    def _handle_update(self, event, elevators: Dict[int, Dict]):
        """Handles UPDATE sub-events (ACCEPT, BEGIN, END). Needs access to all elevator states."""
        sub_type = event['sub_type']
        timestamp = event['timestamp']
        line_num = event['line_num']

        # Get elevator IDs involved (A and B might be the same as e1, e2 or swapped)
        # Use a consistent order (min, max) for tracking in processed_update_accepts
        e1 = event['elevator_id_A']
        e2 = event['elevator_id_B']
        e_min, e_max = min(e1, e2), max(e1, e2)

        # Check if elevators exist (should be caught by parser)
        elevator_1 = elevators.get(e1)
        elevator_2 = elevators.get(e2)
        if not elevator_1 or not elevator_2:
            self.add_error(f"[{timestamp:.4f}] (Line {line_num}) UPDATE-{sub_type}: 内部错误 - 找不到电梯 {e1} 或 {e2} 的状态"); return False

        # --- Rule 6 / Double Car Check: Cannot start UPDATE if already in process or double car ---
        if sub_type == 'ACCEPT':
             if elevator_1['in_update_process'] or elevator_2['in_update_process']:
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) UPDATE-ACCEPT {e1}-{e2}: 电梯 {e1 if elevator_1['in_update_process'] else e2} 已在 UPDATE 改造中，不能接受新请求"); return False
             if elevator_1['is_double_car'] or elevator_2['is_double_car']:
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) UPDATE-ACCEPT {e1}-{e2}: 电梯 {e1 if elevator_1['is_double_car'] else e2} 已是双轿厢模式，不能接受新改造请求"); return False
             if elevator_1['in_sche'] or elevator_2['in_sche']:
                  self.add_error(f"[{timestamp:.4f}] (Line {line_num}) UPDATE-ACCEPT {e1}-{e2}: 电梯 {e1 if elevator_1['in_sche'] else e2} 在 SCHE 模式中，不能接受 UPDATE 请求"); return False

        # --- Process based on sub_type ---
        if sub_type == 'ACCEPT':
            target_floor = event['target_floor']
            # Rule 2 Check (Partial): Ensure neither elevator has another *pending* ACCEPT
            if elevator_1['update_accept_pending'] or elevator_2['update_accept_pending']:
                 pending_e = e1 if elevator_1['update_accept_pending'] else e2
                 details = pending_e.get('last_update_accept_details', ('?','?','?'))
                 accept_time = pending_e.get('last_update_accept_time', -1.0)
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) UPDATE-ACCEPT {e1}-{e2}: 电梯 {pending_e} 已有待处理的 UPDATE-ACCEPT ({details[0]}-{details[1]} @ {accept_time:.4f})"); return False

            # Store pending state in *both* elevators
            accept_details = (e1, e2, target_floor)
            update_data = {
                'update_accept_pending': True,
                'last_update_accept_time': timestamp,
                'last_update_accept_details': accept_details,
                'arrive_count_since_update_accept': 0 # Reset counter
            }
            elevator_1.update(update_data)
            elevator_2.update(update_data)

            # Track globally for Rule 1 (use sorted IDs as key)
            tracking_key = (e_min, e_max, target_floor)
            if tracking_key in self.processed_update_accepts:
                 # This implies a second ACCEPT for the exact same pair/floor, likely an error in output or test data
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) UPDATE-ACCEPT {e1}-{e2}-{target_floor}: 收到重复的 ACCEPT 请求 (之前已有记录)"); return False
            self.processed_update_accepts[tracking_key] = {'begin_seen': False, 'end_seen': False, 'accept_time': timestamp}

            return True

        elif sub_type == 'BEGIN':
            # --- Rule 2 Check: Must have a corresponding pending ACCEPT ---
            if not elevator_1['update_accept_pending'] or not elevator_2['update_accept_pending']:
                 missing_e = e1 if not elevator_1['update_accept_pending'] else e2 if not elevator_2['update_accept_pending'] else 'both'
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) UPDATE-BEGIN {e1}-{e2}: 电梯 {missing_e} 没有待处理的 UPDATE-ACCEPT 请求"); return False
            # Check if the ACCEPT details match between the two elevators and the event
            accept_details1 = elevator_1['last_update_accept_details']
            accept_details2 = elevator_2['last_update_accept_details']
            if not accept_details1 or accept_details1 != accept_details2:
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) UPDATE-BEGIN {e1}-{e2}: 内部状态错误 - 两电梯的待处理 ACCEPT 信息不一致 ({accept_details1} vs {accept_details2})"); return False
            # Ensure the BEGIN IDs match the ACCEPT details (order doesn't matter)
            stored_e1, stored_e2, stored_floor = accept_details1
            if {e1, e2} != {stored_e1, stored_e2}:
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) UPDATE-BEGIN {e1}-{e2}: 事件中的电梯ID与待处理 ACCEPT ({stored_e1}-{stored_e2}) 不符"); return False

            # --- Rule 1 Check: Only one BEGIN per ACCEPT ---
            tracking_key = (e_min, e_max, stored_floor)
            if tracking_key not in self.processed_update_accepts:
                 # This implies BEGIN without ACCEPT, should be caught above, but safety check
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) UPDATE-BEGIN {e1}-{e2}: 找不到对应的 UPDATE-ACCEPT 记录 (key: {tracking_key})"); return False
            if self.processed_update_accepts[tracking_key]['begin_seen']:
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) UPDATE-BEGIN {e1}-{e2}: 对于 ACCEPT ({stored_e1}-{stored_e2}-{stored_floor}) 已收到过 UPDATE-BEGIN"); return False

            # --- Rule 3 Check (Arrive Count) ---
            # Checked individually in _handle_arrive, re-check aggregate here for safety
            if elevator_1['arrive_count_since_update_accept'] > UPDATE_MAX_ARRIVES_BEFORE_BEGIN:
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) UPDATE-BEGIN {e1}-{e2}: 电梯 {e1} 在 ACCEPT 后移动次数过多 ({elevator_1['arrive_count_since_update_accept']} > {UPDATE_MAX_ARRIVES_BEFORE_BEGIN})"); return False
            if elevator_2['arrive_count_since_update_accept'] > UPDATE_MAX_ARRIVES_BEFORE_BEGIN:
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) UPDATE-BEGIN {e1}-{e2}: 电梯 {e2} 在 ACCEPT 后移动次数过多 ({elevator_2['arrive_count_since_update_accept']} > {UPDATE_MAX_ARRIVES_BEFORE_BEGIN})"); return False

            # --- Rule 4 Check (Empty and Closed) ---
            if elevator_1['passengers'] or elevator_2['passengers']:
                 p_list = sorted(list(elevator_1['passengers'].union(elevator_2['passengers'])))
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) UPDATE-BEGIN {e1}-{e2}: 电梯必须为空才能开始改造 (内有: {p_list})"); return False
            if elevator_1['state'] != 'CLOSE' or elevator_2['state'] != 'CLOSE':
                 state_info = f"E{e1}:{elevator_1['state']}, E{e2}:{elevator_2['state']}"
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) UPDATE-BEGIN {e1}-{e2}: 两部电梯门必须都关闭才能开始改造 ({state_info})"); return False

            # Check timing relative to last action (e.g., CLOSE)
            min_begin_time = max(elevator_1['last_move_start_time'], elevator_2['last_move_start_time'])
            if timestamp < min_begin_time - EPSILON:
                self.add_error(f"[{timestamp:.4f}] (Line {line_num}) UPDATE-BEGIN {e1}-{e2}: 时间 ({timestamp:.4f}) 早于两电梯可行动时间 (E{e1} @ {elevator_1['last_move_start_time']:.4f}, E{e2} @ {elevator_2['last_move_start_time']:.4f})"); return False


            # --- Rule 11: Cancel RECEIVEs for both elevators ---
            if elevator_1['active_receives']:
                 # self.print_info(f"DEBUG: E{e1} UPDATE-BEGIN cancelling active receives: {elevator_1['active_receives']}")
                 elevator_1['active_receives'].clear()
            if elevator_2['active_receives']:
                 # self.print_info(f"DEBUG: E{e2} UPDATE-BEGIN cancelling active receives: {elevator_2['active_receives']}")
                 elevator_2['active_receives'].clear()
            # --- End Rule 11 ---

            # Update state for both elevators
            update_data = {
                'in_update_process': True,
                'update_accept_pending': False, # Clear pending flag
                'update_begin_time': timestamp,
                # Clear SCHE state just in case (though SCHE interaction is disallowed earlier)
                'in_sche': False, 'sche_accept_pending': False,
                'arrive_count_since_update_accept': 0, # Clear counter
            }
            elevator_1.update(update_data)
            elevator_2.update(update_data)

            # Mark BEGIN as seen for this ACCEPT
            self.processed_update_accepts[tracking_key]['begin_seen'] = True

            return True

        elif sub_type == 'END':
            # --- Rule 2 Check: Must be in update process ---
            if not elevator_1['in_update_process'] or not elevator_2['in_update_process']:
                 missing_e = e1 if not elevator_1['in_update_process'] else e2 if not elevator_2['in_update_process'] else 'both'
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) UPDATE-END {e1}-{e2}: 电梯 {missing_e} 未处于 UPDATE 改造过程中"); return False
            # Check if the BEGIN times match (should be identical if started together)
            if abs(elevator_1['update_begin_time'] - elevator_2['update_begin_time']) > EPSILON:
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) UPDATE-END {e1}-{e2}: 内部状态错误 - 两电梯的 UPDATE-BEGIN 时间不一致 ({elevator_1['update_begin_time']:.4f} vs {elevator_2['update_begin_time']:.4f})"); return False
            if elevator_1['update_begin_time'] < 0: # Should be set by BEGIN
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) UPDATE-END {e1}-{e2}: 内部状态错误 - 找不到对应的 UPDATE-BEGIN 时间"); return False

            # Find the corresponding ACCEPT details using the BEGIN time (or stored details)
            accept_details = elevator_1['last_update_accept_details'] # Get details from one elevator
            if not accept_details:
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) UPDATE-END {e1}-{e2}: 内部状态错误 - 找不到关联的 ACCEPT 详情"); return False
            stored_e1, stored_e2, target_floor = accept_details
            if {e1, e2} != {stored_e1, stored_e2}: # Ensure END IDs match original ACCEPT
                  self.add_error(f"[{timestamp:.4f}] (Line {line_num}) UPDATE-END {e1}-{e2}: 事件中的电梯ID与原始 ACCEPT ({stored_e1}-{stored_e2}) 不符"); return False

            # --- Rule 1 Check: Only one END per ACCEPT ---
            tracking_key = (e_min, e_max, target_floor)
            if tracking_key not in self.processed_update_accepts:
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) UPDATE-END {e1}-{e2}: 找不到对应的 UPDATE-ACCEPT 记录 (key: {tracking_key})"); return False
            if not self.processed_update_accepts[tracking_key]['begin_seen']:
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) UPDATE-END {e1}-{e2}: 在收到 UPDATE-BEGIN 之前收到了 UPDATE-END (for ACCEPT {tracking_key})"); return False
            if self.processed_update_accepts[tracking_key]['end_seen']:
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) UPDATE-END {e1}-{e2}: 对于 ACCEPT ({tracking_key}) 已收到过 UPDATE-END"); return False

            # --- Rule 5 Check (Duration) ---
            begin_time = elevator_1['update_begin_time']
            duration = timestamp - begin_time
            if duration < UPDATE_DURATION_MIN - EPSILON:
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) UPDATE-END {e1}-{e2}: 改造持续时间太短 ({duration:.4f}s < {UPDATE_DURATION_MIN}s). BEGIN 时间: {begin_time:.4f}"); return False

            # --- Rule 3 Check (Response Time) ---
            accept_time = elevator_1['last_update_accept_time']
            if accept_time < 0:
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) UPDATE-END {e1}-{e2}: 内部状态错误 - 找不到对应的 UPDATE-ACCEPT 时间"); return False
            response_time = timestamp - accept_time
            if response_time > UPDATE_MAX_RESPONSE_TIME + EPSILON:
                  self.add_error(
                      f"[{timestamp:.4f}] (Line {line_num}) UPDATE-END {e1}-{e2}: UPDATE 响应时间 ({response_time:.4f}s) "
                      f"超过最大允许值 {UPDATE_MAX_RESPONSE_TIME}s "
                      f"(自 ACCEPT @ {accept_time:.4f})"
                  ); return False

            # --- State Update after END ---
            # Mark process finished
            finish_update_data = {
                'in_update_process': False,
                'update_begin_time': -1.0,
                'last_update_accept_time': -1.0, # Clear accept info for this cycle
                'last_update_accept_details': None,
            }
            elevator_1.update(finish_update_data)
            elevator_2.update(finish_update_data)

            # --- Rule 9: Set Speed ---
            elevator_1['current_speed'] = UPDATED_MOVE_TIME
            elevator_2['current_speed'] = UPDATED_MOVE_TIME

            # --- Rule 7 & 8 Setup: Set Roles, Partner, Transfer Floor, and Final Position ---
            transfer_floor_num = self.floor_to_num(target_floor)
            if transfer_floor_num is None: # Should be caught by parser
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) UPDATE-END {e1}-{e2}: 内部错误 - 目标楼层 '{target_floor}' 无效"); return False

            # Determine A/B roles based on original IDs? Or fixed by e1/e2 in event?
            # Let's assume e1 from the event is designated 'A', e2 is 'B' for role assignment.
            elevator_A = elevators[e1]
            elevator_B = elevators[e2]

            expected_A_floor_num = transfer_floor_num + 1
            expected_B_floor_num = transfer_floor_num - 1
            expected_A_floor = self.num_to_floor(expected_A_floor_num)
            expected_B_floor = self.num_to_floor(expected_B_floor_num)

            # Check if expected floors are valid (e.g., A not above F7, B not below B4)
            if expected_A_floor is None:
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) UPDATE-END {e1}-{e2}: 改造后 A({e1}) 预期楼层 ({expected_A_floor_num}) 超出范围"); return False
            if expected_B_floor is None:
                 self.add_error(f"[{timestamp:.4f}] (Line {line_num}) UPDATE-END {e1}-{e2}: 改造后 B({e2}) 预期楼层 ({expected_B_floor_num}) 超出范围"); return False

            # Update state for A (e1)
            elevator_A.update({
                'is_double_car': True,
                'double_car_role': 'A',
                'partner_id': e2,
                'transfer_floor': target_floor,
                'current_floor': expected_A_floor,
                'last_move_start_time': timestamp, # Can move immediately from new position
                'last_arrive_time': timestamp # Treat END time as arrival at new floor for timing checks
            })
            # Update state for B (e2)
            elevator_B.update({
                'is_double_car': True,
                'double_car_role': 'B',
                'partner_id': e1,
                'transfer_floor': target_floor,
                'current_floor': expected_B_floor,
                'last_move_start_time': timestamp,
                'last_arrive_time': timestamp
            })

            # Mark END as seen for this ACCEPT
            self.processed_update_accepts[tracking_key]['end_seen'] = True

            return True
        else:
            self.add_error(f"[{timestamp:.4f}] (Line {line_num}) UPDATE: 未知的UPDATE子类型 '{sub_type}'"); return False


    # --- Main Validation Function ---

    def is_output_correct(self, input_data: List[str], jar_output: str) -> Tuple[bool, float, float]:
        """
        Validates the sequence of events against HW6+UPDATE rules, ignoring [LOG] lines.
        Returns: (is_correct, average_weighted_completion_time, total_power_consumption)
        """
        self.current_errors = []
        self.events = []
        self.elevators = {}
        self.passenger_states = {}
        self.input_passengers = {}
        self.input_sche_commands = []
        self.input_update_commands = []
        self.processed_update_accepts = {} # Reset for each validation run
        latest_event_time = 0.0

        try:
            # 1. Parse Input Data (Now includes UPDATE)
            if not self._parse_input_data(input_data):
                return False, np.nan, np.nan

            # 2. Parse Output Data (Now includes UPDATE and ignores LOG)
            self.events = self._parse_output_data(jar_output)
            if self.events is None: # Parsing failed
                 return False, np.nan, np.nan

            input_had_requests = bool(self.input_passengers or self.input_sche_commands or self.input_update_commands)
            if not self.events and input_had_requests:
                # Check if output *only* contained LOG lines
                if any('[LOG]' in line for line in jar_output.split('\n') if line.strip()):
                    self.add_error("验证错误: 程序仅输出了[LOG]信息，没有产生任何有效事件输出，但输入包含请求。")
                else:
                    self.add_error("验证错误: 程序未产生任何有效输出，但输入包含请求。")
                return False, np.nan, np.nan
            elif self.events:
                latest_event_time = self.events[-1]['timestamp']
            elif not input_had_requests:
                 self.print_info("验证信息: 输入和有效输出均为空，视为正确。")
                 return True, 0.0, 0.0 # Valid empty case

            # 3. Initialize Simulation State (Using updated _init_elevator_state)
            self.elevators = {i: self._init_elevator_state(i) for i in range(1, ELEVATOR_COUNT + 1)}
            self.passenger_states = {}
            for pid, data in self.input_passengers.items():
                 self.passenger_states[pid] = {
                     **data, 'completed': False, 'current_floor': data['from_floor'],
                     'in_elevator': False, 'elevator_id': None, 'complete_time': None,
                     'exited_sche_temp': False, 'temp_exit_floor': None
                 }

            # 4. Process Events Chronologically
            event_handlers = {
                'ARRIVE': self._handle_arrive, 'OPEN': self._handle_open,
                'CLOSE': self._handle_close, 'IN': self._handle_in,
                'OUT': self._handle_out, 'RECEIVE': self._handle_receive,
                'SCHE': self._handle_sche,
                'UPDATE': self._handle_update, # Add UPDATE handler
            }

            for event in self.events:
                etype = event['event_type']
                handler = event_handlers.get(etype)

                if handler:
                    # UPDATE handler needs all elevators, others need specific one(s)
                    if etype == 'UPDATE':
                        if not handler(event, self.elevators): # Pass the event and all elevators
                           return False, np.nan, np.nan
                    else:
                        # Find the relevant elevator ID (might be 'elevator_id', 'elevator_id_A', etc.)
                        eid = event.get('elevator_id') # Default for most events
                        if eid is not None:
                             if eid not in self.elevators:
                                 self.add_error(f"[{event['timestamp']:.4f}] (Line {event['line_num']}) 内部错误: 事件涉及未知电梯ID {eid}")
                                 return False, np.nan, np.nan
                             if not handler(event, self.elevators[eid]): # Pass event and single elevator state
                                 return False, np.nan, np.nan
                        elif etype == 'RECEIVE': # RECEIVE must have elevator_id
                             self.add_error(f"[{event['timestamp']:.4f}] (Line {event['line_num']}) 内部验证错误: RECEIVE 事件缺少必要的电梯ID")
                             return False, np.nan, np.nan
                        else: # Event type doesn't fit standard pattern (should not happen with parser)
                             self.add_error(f"[{event['timestamp']:.4f}] (Line {event['line_num']}) 内部验证错误: 事件 {etype} 无电梯ID且未被特殊处理")
                             return False, np.nan, np.nan
                else:
                     self.add_error(f"[{event['timestamp']:.4f}] (Line {event['line_num']}) 内部验证错误: 找不到事件处理器 for type '{etype}' (原始事件: {event['raw']})")
                     return False, np.nan, np.nan

            # 5. Final State Validation (Updated)
            if not self._validate_final_state(self.elevators, self.passenger_states):
                return False, np.nan, np.nan

            # 6. Calculate Performance Metrics (Updated Power Calc Needed)
            power_consumption = self._calculate_total_power(self.events)
            avg_weighted_time = self._calculate_avg_weighted_time(self.passenger_states)

            return True, avg_weighted_time, power_consumption

        except Exception as e:
            self.add_error(f"验证过程中发生意外内部错误: {type(e).__name__} - {e}")
            self.add_error("详细信息:")
            self.add_error(traceback.format_exc())
            return False, np.nan, np.nan

    def _validate_final_state(self, final_elevator_states, final_passenger_states):
        """Checks final state according to HW6+UPDATE rules."""
        all_ok = True
        # 1. Check Passengers (Same logic as before)
        if self.input_passengers:
            if not final_passenger_states and self.input_passengers:
                self.add_error("最终状态错误: 输入中有乘客，但最终乘客状态为空。")
                all_ok = False
            else:
                for pid, pstate in final_passenger_states.items():
                    if pid not in self.input_passengers:
                        self.add_error(f"最终状态错误: 乘客 {pid} 出现在最终状态中，但未在输入中定义。"); all_ok = False; continue
                    original_request = self.input_passengers[pid]
                    if not pstate.get('completed', False):
                        error_reason = f"未完成原始请求 (目标: {original_request.get('to_floor', '?')})"
                        if pstate.get('in_elevator'): error_reason += f" - 仍在电梯 {pstate.get('elevator_id', '?')} 内"
                        elif pstate.get('exited_sche_temp'): error_reason += f" - 处于临时下车状态 @{pstate.get('temp_exit_floor', '?')}"
                        else: error_reason += f" - 最后记录位置 @{pstate.get('current_floor', original_request.get('from_floor','?'))}"
                        self.add_error(f"最终状态错误: 乘客 {pid} {error_reason}"); all_ok = False
                    elif pstate.get('current_floor') != original_request.get('to_floor'):
                        self.add_error(f"最终状态错误: 乘客 {pid} 被标记为完成, 但最终记录位置 ({pstate.get('current_floor', '?')}) 与目标 ({original_request.get('to_floor', '?')}) 不符"); all_ok = False
                    if pstate.get('in_elevator') and pstate.get('completed', False):
                        self.add_error(f"最终状态错误: 乘客 {pid} 标记完成但结束时仍在电梯 {pstate.get('elevator_id', '?')} 内"); all_ok = False
                    if pstate.get('exited_sche_temp'):
                        self.add_error(f"最终状态错误: 乘客 {pid} 结束时处于临时下车状态 (在 {pstate.get('temp_exit_floor', '?')})"); all_ok = False
                missing_passengers = set(self.input_passengers.keys()) - set(final_passenger_states.keys())
                if missing_passengers and self.events: # Only error if there were events (program actually ran)
                     self.add_error(f"最终状态错误: 输入中的乘客 {sorted(list(missing_passengers))} 未在最终状态中找到。"); all_ok = False

        # 2. Check Elevators (Updated for UPDATE/DoubleCar)
        for eid, estate in final_elevator_states.items():
            if estate.get('state') != 'CLOSE':
                self.add_error(f"最终状态错误: 电梯 {eid} 结束时门未关闭 (状态: {estate.get('state', '?')})"); all_ok = False
            if estate.get('passengers'):
                p_list = sorted(list(estate['passengers']))
                self.add_error(f"最终状态错误: 电梯 {eid} 结束时仍有乘客: {p_list}"); all_ok = False
            if estate.get('in_sche'):
                 self.add_error(f"最终状态错误: 电梯 {eid} 结束时仍处于SCHE模式"); all_ok = False
            if estate.get('sche_accept_pending'):
                 self.add_error(f"最终状态错误: 电梯 {eid} 结束时有一个待处理的 SCHE-ACCEPT，未完成。"); all_ok = False
            # --- New UPDATE Checks ---
            if estate.get('in_update_process'):
                 self.add_error(f"最终状态错误: 电梯 {eid} 结束时仍处于UPDATE改造过程中"); all_ok = False
            if estate.get('update_accept_pending'):
                 details = estate.get('last_update_accept_details', '?')
                 self.add_error(f"最终状态错误: 电梯 {eid} 结束时有一个待处理的 UPDATE-ACCEPT ({details})，未完成。"); all_ok = False
            # If it's a double car, check its speed is correct
            if estate.get('is_double_car'):
                 if abs(estate.get('current_speed', -1) - UPDATED_MOVE_TIME) > EPSILON:
                     self.add_error(f"最终状态错误: 双轿厢电梯 {eid} 结束时速度 ({estate.get('current_speed', '?')}) 不是 {UPDATED_MOVE_TIME}"); all_ok = False
            # If not double car, check speed is default
            elif abs(estate.get('current_speed', -1) - DEFAULT_MOVE_TIME) > EPSILON:
                 # Allow if it's Inf (e.g., error state) or 0.0 (initial state before any move?)
                 current_speed = estate.get('current_speed', 0.0)
                 if not (math.isinf(current_speed) or abs(current_speed - 0.0) < EPSILON):
                      # Only flag if it's *not* default, and *not* infinity or zero
                      self.add_error(f"最终状态错误: 普通电梯 {eid} 结束时速度 ({current_speed}) 不是默认值 {DEFAULT_MOVE_TIME}"); all_ok = False


        # 3. Check global UPDATE state consistency
        for key, state in self.processed_update_accepts.items():
             e1, e2, floor = key
             # If ACCEPT was processed, BEGIN and END should both be seen or both unseen
             if state['begin_seen'] != state['end_seen']:
                  status = "BEGIN 已见但 END 未见" if state['begin_seen'] else "END 已见但 BEGIN 未见 (逻辑错误)"
                  self.add_error(f"最终状态错误: UPDATE 请求 ({e1}-{e2}-{floor} @ {state['accept_time']:.4f}) 未正确完成 ({status})"); all_ok = False

        return all_ok

    def _calculate_total_power(self, events: List[Dict]) -> float:
        """Calculates total power consumption based on HW6+UPDATE rules by re-simulating."""
        total_power = 0.0
        # Need a simulation state that tracks speed changes accurately
        power_calc_elevators = {i: self._init_elevator_state(i) for i in range(1, ELEVATOR_COUNT + 1)}
        sim_errors = []
        def add_sim_error(msg): sim_errors.append(msg)

        for event in events:
            etype = event['event_type']
            # Need to handle events affecting one or two elevators
            eids_involved = []
            if 'elevator_id' in event: eids_involved.append(event['elevator_id'])
            if 'elevator_id_A' in event: eids_involved.append(event['elevator_id_A'])
            if 'elevator_id_B' in event: eids_involved.append(event['elevator_id_B'])
            eids_involved = sorted(list(set(eids_involved))) # Unique sorted IDs

            if not eids_involved and etype != 'UPDATE': # UPDATE handled below
                 continue # Skip events not tied to an elevator (unless UPDATE)

            timestamp = event['timestamp']

            # --- Simulation Logic ---
            if etype == 'ARRIVE':
                eid = event['elevator_id']
                elevator_state = power_calc_elevators.get(eid)
                if not elevator_state: continue # Should not happen

                speed_used = elevator_state['current_speed']
                # Power: 0.4 for default (0.4s), 0.6 for SCHE/UPDATE speed (non-0.4s)
                power = 0.4 if abs(speed_used - DEFAULT_MOVE_TIME) < EPSILON else 0.6
                total_power += power

                # Update state
                elevator_state['current_floor'] = event['floor']
                elevator_state['last_arrive_time'] = timestamp
                elevator_state['last_move_start_time'] = timestamp
                elevator_state['last_move_speed_used'] = speed_used

            elif etype == 'OPEN':
                eid = event['elevator_id']
                elevator_state = power_calc_elevators.get(eid)
                if not elevator_state: continue
                total_power += 0.1
                elevator_state['state'] = 'OPEN'; elevator_state['last_open_time'] = timestamp

            elif etype == 'CLOSE':
                eid = event['elevator_id']
                elevator_state = power_calc_elevators.get(eid)
                if not elevator_state: continue
                total_power += 0.1
                elevator_state['state'] = 'CLOSE'; elevator_state['last_close_time'] = timestamp
                elevator_state['last_move_start_time'] = timestamp

            elif etype == 'SCHE':
                eid = event['elevator_id']
                elevator_state = power_calc_elevators.get(eid)
                if not elevator_state: continue
                sub_type = event.get('sub_type')
                if sub_type == 'ACCEPT':
                     # Store speed for potential BEGIN
                     elevator_state['last_sche_accept_speed'] = event['speed']
                elif sub_type == 'BEGIN':
                     accepted_speed = elevator_state.get('last_sche_accept_speed')
                     if accepted_speed is None: # Recover if possible
                          add_sim_error(f"PowerCalc SCHE BEGIN E{eid} @ {timestamp:.4f}: No accept speed stored.")
                          # Use speed from event itself if available (some error cases might output it)
                          accepted_speed = event.get('speed', DEFAULT_MOVE_TIME)
                          self.print_info(f"PowerCalc Recovery: Using speed {accepted_speed} for SCHE BEGIN E{eid}")
                     elevator_state['current_speed'] = accepted_speed
                     elevator_state['in_sche'] = True # Track state for END reset
                     elevator_state['last_move_start_time'] = timestamp
                elif sub_type == 'END':
                     elevator_state['current_speed'] = DEFAULT_MOVE_TIME # Reset speed
                     elevator_state['in_sche'] = False
                     elevator_state['last_sche_accept_speed'] = None # Clear stored speed

            elif etype == 'UPDATE':
                 sub_type = event.get('sub_type')
                 e1 = event['elevator_id_A']
                 e2 = event['elevator_id_B']
                 elevator_1 = power_calc_elevators.get(e1)
                 elevator_2 = power_calc_elevators.get(e2)
                 if not elevator_1 or not elevator_2: continue

                 if sub_type == 'ACCEPT':
                      # Store target floor and IDs for END's position update
                      accept_details = (e1, e2, event['target_floor'])
                      elevator_1['last_update_accept_details'] = accept_details
                      elevator_2['last_update_accept_details'] = accept_details
                      # No power change on ACCEPT
                 elif sub_type == 'BEGIN':
                      # No power change on BEGIN, just state change
                      elevator_1['in_update_process'] = True
                      elevator_2['in_update_process'] = True
                      elevator_1['last_move_start_time'] = timestamp # Mark when process starts
                      elevator_2['last_move_start_time'] = timestamp
                 elif sub_type == 'END':
                      # --- Speed change happens AFTER END for future moves ---
                      elevator_1['current_speed'] = UPDATED_MOVE_TIME
                      elevator_2['current_speed'] = UPDATED_MOVE_TIME
                      # --- Position change ---
                      accept_details = elevator_1.get('last_update_accept_details')
                      if accept_details:
                          e1_accept, e2_accept, target_floor = accept_details # Get the original pair from accept
                          # Find which elevator in the END event corresponds to e1_accept (becomes A)
                          # The event defines e1 as A, e2 as B for the purpose of roles/position
                          elevator_A = elevator_1 if e1 == e1_accept else elevator_2
                          elevator_B = elevator_2 if e1 == e1_accept else elevator_1
                          # Sanity check
                          if elevator_A['id'] == elevator_B['id']:
                               add_sim_error(f"PowerCalc UPDATE END {e1}-{e2} @ {timestamp:.4f}: Internal error - A and B are the same elevator ({elevator_A['id']}).")
                               continue

                          transfer_floor_num = self.floor_to_num(target_floor)
                          if transfer_floor_num is not None:
                              eA_floor = self.num_to_floor(transfer_floor_num + 1)
                              eB_floor = self.num_to_floor(transfer_floor_num - 1)
                              if eA_floor: elevator_A['current_floor'] = eA_floor
                              else: add_sim_error(f"PowerCalc UPDATE END {e1}-{e2} @ {timestamp:.4f}: Invalid calculated floor for A (num {transfer_floor_num + 1})")
                              if eB_floor: elevator_B['current_floor'] = eB_floor
                              else: add_sim_error(f"PowerCalc UPDATE END {e1}-{e2} @ {timestamp:.4f}: Invalid calculated floor for B (num {transfer_floor_num - 1})")

                              # Update partner ID and role based on assignment (e1=A, e2=B)
                              elevator_A['partner_id'] = elevator_B['id']
                              elevator_A['double_car_role'] = 'A'
                              elevator_B['partner_id'] = elevator_A['id']
                              elevator_B['double_car_role'] = 'B'
                              elevator_A['transfer_floor'] = target_floor
                              elevator_B['transfer_floor'] = target_floor

                          else: add_sim_error(f"PowerCalc UPDATE END {e1}-{e2} @ {timestamp:.4f}: Invalid target floor '{target_floor}' in stored details.")
                      else: add_sim_error(f"PowerCalc UPDATE END {e1}-{e2} @ {timestamp:.4f}: Missing accept details.")

                      # Update state for both elevators involved in the END event
                      elevator_1['in_update_process'] = False
                      elevator_2['in_update_process'] = False
                      elevator_1['is_double_car'] = True # Mark as double car permanently
                      elevator_2['is_double_car'] = True
                      elevator_1['last_move_start_time'] = timestamp # Can move from new pos
                      elevator_2['last_move_start_time'] = timestamp
                      elevator_1['last_arrive_time'] = timestamp # Treat as arrival for timing
                      elevator_2['last_arrive_time'] = timestamp
                      elevator_1['last_update_accept_details'] = None # Clear stored details
                      elevator_2['last_update_accept_details'] = None


        if sim_errors:
             self.print_red("警告: 在功率计算的状态模拟期间发生错误:")
             for err in sim_errors[:5]: self.print_red(f"  - {err}")
             if len(sim_errors) > 5: self.print_red(f"  ... ({len(sim_errors) - 5} more errors)")

        return total_power

    # _calculate_avg_weighted_time remains the same
    def _calculate_avg_weighted_time(self, final_passenger_states: Dict) -> float:
        """Calculates Average Weighted Completion Time based on original PRI requests."""
        total_weighted_time, total_priority_sum = 0.0, 0.0
        completed_count = 0

        if not self.input_passengers:
            return 0.0

        for pid, p_input_data in self.input_passengers.items():
            pstate = final_passenger_states.get(pid)
            if pstate and pstate.get('completed') and pstate.get('complete_time') is not None:
                completion_time = pstate['complete_time']
                request_time = p_input_data['request_time']
                if completion_time < request_time - EPSILON:
                    self.print_red(f"警告: 乘客 {pid} 完成时间 ({completion_time:.4f}) 早于 请求时间 ({request_time:.4f}). 使用 0 等待时间计算。")
                    wait_time = 0.0
                else:
                    wait_time = completion_time - request_time
                priority = max(1, p_input_data.get('priority', 1))
                total_weighted_time += wait_time * priority
                total_priority_sum += priority
                completed_count += 1

        if completed_count == 0:
             if self.input_passengers: self.print_red("警告: 没有乘客完成请求，无法计算平均加权完成时间。")
             return np.nan
        if total_priority_sum < EPSILON:
            # This case should only happen if all completed passengers had priority 0 (invalid input)
            # or if somehow only passengers with priority 0 completed.
            self.print_red(f"警告: 完成乘客的总优先级 ({total_priority_sum}) 接近于零，平均加权完成时间未定义。")
            return np.nan
        return total_weighted_time / total_priority_sum

    # save_error_case remains the same, maybe add ruleset clarification
    def save_error_case(self, input_data: List[str], jar_output: str, test_num: int, jar_file: str):
        """Saves input, output, and validation errors to a timestamped file."""
        ts = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = os.path.join(ERROR_OUTPUT_DIR, f"error_{test_num}_{os.path.basename(jar_file).replace('.jar','')}_{ts}.txt")
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"=== 测试编号: {test_num}, JAR: {os.path.basename(jar_file)} ===\n")
                f.write(f"=== 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
                f.write(f"=== 线程: {threading.current_thread().name} ===\n")
                f.write(f"=== HW6+UPDATE 验证规则集 ===\n") # Clarify ruleset

                f.write("\n=== 输入数据 ===\n")
                f.write('\n'.join(input_data))

                f.write("\n\n=== 程序输出 (原始) ===\n")
                f.write(jar_output if jar_output else "[程序无标准输出或输出文件为空]\n")

                f.write("\n\n=== 验证错误信息 ===\n")
                if self.current_errors:
                    for i, err_msg in enumerate(self.current_errors, 1):
                        f.write(f"{i}. {err_msg}\n")
                else:
                    f.write("(无特定验证错误信息记录，可能为运行时错误、超时、或验证器内部崩溃)\n")
            self.print_red(f"错误用例已保存到: {filename}")
        except Exception as e:
            self.print_red(f"保存错误用例文件 {filename} 时发生错误: {e}")

    # run_test needs to pass the update_count to generate_input_data
    def run_test(self, passenger_count: int, sche_command_count: int, update_command_count: int, test_num: int):
        """Generates data, runs all JARS, validates HW6+UPDATE output, collects results."""
        thread_name = threading.current_thread().name
        self.print_info(f"\n[{thread_name}] ===> 开始测试 {test_num} (PRI:{passenger_count}, SCHE_CMD:{sche_command_count}, UPDATE:{update_command_count}) <===")

        input_data = self.generate_input_data(passenger_count, sche_command_count, update_command_count)
        is_expected_empty = (passenger_count == 0 and sche_command_count == 0 and update_command_count == 0)
        if not input_data and not SINGLE_INSTANCE_TEST and not is_expected_empty:
             self.print_red(f"[{thread_name}] 测试 {test_num} 失败：无法生成输入数据。跳过此测试。")
             return {jar: (False, 0.0, np.nan, np.nan) for jar in TEST_JAR_FILES}
        elif not input_data and (is_expected_empty or SINGLE_INSTANCE_TEST):
             self.print_info(f"[{thread_name}] 测试 {test_num}: 使用空输入数据。")
             input_data = []

        results_for_this_test = {}
        for jar_file in TEST_JAR_FILES:
            jar_basename = os.path.basename(jar_file)
            self.print_info(f"[{thread_name}] 测试 {test_num} - 运行 JAR: {jar_basename} ...")

            # Use a fresh validator instance for each JAR run
            validator = TestEvaluator()
            output, run_success, elapsed_time = validator.run_jar_program(input_data, test_num, jar_file)
            time.sleep(0.05)

            is_correct = False
            avg_wt = np.nan
            power = np.nan
            validation_errors = []

            if not run_success:
                 if elapsed_time >= TIMEOUT_SECONDS - EPSILON: validator.add_error("程序运行超时。")
                 else: validator.add_error("程序未能成功运行 (非超时)。查看stderr了解详情。")
                 validation_errors = validator.current_errors
                 validator.save_error_case(input_data, output, test_num, jar_file)
            else:
                self.print_info(f"[{thread_name}] 测试 {test_num} - 验证 {jar_basename} 的输出 (HW6+UPDATE规则)...")
                # Pass the original output (including LOGs) for error saving, but validation ignores them
                is_correct, avg_wt_calc, power_calc = validator.is_output_correct(input_data, output)
                validation_errors = validator.current_errors

                if not is_correct:
                    validator.print_red(f"[{thread_name}] 测试 {test_num} - 程序 {jar_basename} 输出结果不正确!")
                    for i, err in enumerate(validation_errors[:5]): print(f"    错误 {i+1}: {err}", file=sys.stderr)
                    if len(validation_errors) > 5: print(f"    ... (共 {len(validation_errors)} 条错误)", file=sys.stderr)
                    validator.save_error_case(input_data, output, test_num, jar_file) # Save original output
                else:
                    validator.print_green(f"[{thread_name}] 测试 {test_num} 对于 {jar_basename} 通过! :)")
                    avg_wt = avg_wt_calc
                    power = power_calc
                    wt_str = f"{avg_wt:.4f}" if avg_wt is not None and not math.isnan(avg_wt) else "N/A"
                    power_str = f"{power:.1f}" if power is not None and not math.isnan(power) else "N/A"
                    validator.print_info(f"    性能指标 -> 耗时: {elapsed_time:.3f}s, 平均加权完成时间(WT): {wt_str}, 系统耗电量(W): {power_str}")

            results_for_this_test[jar_file] = (is_correct, elapsed_time, avg_wt, power)

        self.print_info(f"[{thread_name}] ===> 完成测试 {test_num} <===")
        return results_for_this_test

    # run_test_suite needs to accept update_count and pass it to run_test
    def run_test_suite(self, n: int, passenger_count: int, sche_command_count: int, update_command_count: int):
        """Manages the execution of multiple tests using a thread pool and aggregates results."""
        global total_tests, passed_tests, test_times, avg_completion_times, power_consumptions
        start_suite_time = time.time()

        with lock: # Reset global state
            total_tests, passed_tests = 0, 0
            test_times = {j: [] for j in TEST_JAR_FILES}
            avg_completion_times = {j: [] for j in TEST_JAR_FILES}
            power_consumptions = {j: [] for j in TEST_JAR_FILES}

        self.print_info("清理旧的输出和错误文件...")
        for dir_path in [ERROR_OUTPUT_DIR, INPUT_OUTPUT_DIR]:
            os.makedirs(dir_path, exist_ok=True)
            for f_name in os.listdir(dir_path):
                f_path = os.path.join(dir_path, f_name)
                if os.path.isfile(f_path):
                    try:
                        os.remove(f_path)
                    except OSError as e: (
                        print(f"警告: 无法删除旧文件 {f_path}: {e}", file=sys.stderr))

        print("\n" + "=" * 60)
        print("=== BUAA OO HW6+UPDATE 自动评测启动 ===")
        print(f"测试JAR包: {', '.join(map(os.path.basename, TEST_JAR_FILES))}")
        print(f"总测试次数 (n): {n}")
        if SINGLE_INSTANCE_TEST: print("模式: 单例测试 (使用 test.txt)")
        else: print(f"每次测试请求数 -> PRI: {passenger_count}, SCHE_CMD: {sche_command_count}, UPDATE: {update_command_count}")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"输入/输出目录: '{INPUT_OUTPUT_DIR}/'")
        print(f"错误用例目录: '{ERROR_OUTPUT_DIR}/'")
        print(f"超时设置: {TIMEOUT_SECONDS}秒"); print(f"最大并发线程数: {MAX_THREADS}")
        print("=" * 60 + "\n")

        actual_tests_to_run = n
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS, thread_name_prefix="TestWorker") as executor:
            future_to_testnum = {
                executor.submit(self.run_test, passenger_count, sche_command_count, update_command_count, i): i
                for i in range(1, actual_tests_to_run + 1)
            }
            num_completed = 0
            for future in concurrent.futures.as_completed(future_to_testnum):
                test_num = future_to_testnum[future]
                num_completed += 1
                try:
                    results_one_test = future.result()
                    self.update_stats(results_one_test, test_num)
                    self.print_info(f"--- 测试 {test_num}/{actual_tests_to_run} 处理完成 ({num_completed}/{actual_tests_to_run}) ---")
                except Exception as exc:
                    self.print_red(f'FATAL: 测试 {test_num} 执行时产生无法处理的异常: {exc}')
                    self.print_red(traceback.format_exc())
                    # Still attempt to update stats marking all as failed for this test
                    self.update_stats({jar: (False, np.nan, np.nan, np.nan) for jar in TEST_JAR_FILES}, test_num)


        suite_duration = time.time() - start_suite_time
        print("\n" + "=" * 60); print(f"=== 测试套件完成 (总耗时: {suite_duration:.2f}秒) ==="); print("=" * 60)

        with lock:
             total_attempted_jars = sum(len(v) for v in test_times.values())
             current_passed_tests = passed_tests
        if total_attempted_jars == 0: print("\n未记录任何测试结果。"); return

        print(f"总计尝试 JAR 运行次数: {total_attempted_jars} ({len(TEST_JAR_FILES)} JARs x {actual_tests_to_run} 测试)")
        print(f"总计通过 (验证成功): {current_passed_tests}")
        actual_failed_tests = total_attempted_jars - current_passed_tests
        print(f"总计失败 (运行或验证): {actual_failed_tests}")
        if total_attempted_jars > 0:
            accuracy = (current_passed_tests / total_attempted_jars) * 100
            print(f"总正确率: {accuracy:.1f}%")
            if accuracy == 100.0 and actual_failed_tests == 0: self.print_green("\n*** 恭喜！所有测试点全部通过！ ***\n")
            elif current_passed_tests == 0: self.print_red("\n*** 警告：所有完成的测试点均未通过验证。 ***\n")
        else: print("\n未完成任何测试点。"); return

        # Check for performance data
        with lock:
            has_valid_perf_data = any(any(v is not None and not math.isnan(v) for v in dl) for pd in [avg_completion_times, power_consumptions] for dl in pd.values() if dl)
            has_runtime_data = any(any(t is not None and not math.isnan(t) and t > 0 for t in tl) for tl in test_times.values() if tl)

        if has_valid_perf_data:
            try:
                print('\n--- 生成性能报告与图表 (HW6+UPDATE 指标) ---')
                self.print_rankings()
                ranked_scores = calculate_scores()
                self.plot_runtime()
                self.plot_completion_time()
                self.plot_power_consumption()
                self.plot_scores(ranked_scores)
                print("\n=== 综合性能得分排名 (满分15, 基于通过测试点的平均表现) ===")
                if ranked_scores:
                     max_len = max(len(os.path.basename(j)) for j, s in ranked_scores) if ranked_scores else 20
                     print(f"{'排名':<4} {'JAR 文件':<{max_len}} {'得分':<10} {'通过/运行次数'}"); print("-" * (max_len + 30))
                     for rank, (jar, score) in enumerate(ranked_scores, 1):
                         jar_name = os.path.basename(jar)
                         with lock:
                             # Count passes based on valid WT OR Power
                             pass_count_wt = sum(1 for wt in avg_completion_times.get(jar, []) if wt is not None and not math.isnan(wt))
                             pass_count_power = sum(1 for p in power_consumptions.get(jar, []) if p is not None and not math.isnan(p))
                             # A test contributes to scoring if EITHER WT or Power is valid. Let's approximate the 'pass count' for scoring as the max of the two.
                             # A better approach might be to count runs where *both* were valid, or where *at least one* was valid. Max is simpler here.
                             pass_count = max(pass_count_wt, pass_count_power)
                             total_run = len(test_times.get(jar, []))
                         pass_info = f"({pass_count}/{total_run})" if total_run > 0 else "(0/0)"
                         print(f"{rank:<4} {jar_name:<{max_len}} {score:<10.2f} {pass_info}")
                     print("-" * (max_len + 30))
                else: print("未能计算综合得分 (无有效的性能数据).")
                print('\n--- 报告图表生成完毕 ---')
            except Exception as plot_err:
                print(f"\n生成报告/图表时发生错误: {plot_err}", file=sys.stderr); print(traceback.format_exc(), file=sys.stderr)
        else:
            print("\n无有效的性能测试结果数据 (WT/Power)，无法生成性能排名或评分。")
            if has_runtime_data: print("仅绘制运行时间图表。"); self.plot_runtime()
            else: print("也无运行时间数据可绘制。")
        print("\n=== 评测结束 ===")

    # update_stats, calculate_rankings, print_rankings, plotting functions remain the same structure
    # They operate on the collected data (test_times, avg_completion_times, power_consumptions)
    # which are now populated considering the full HW6+UPDATE validation.
    # Ensure plot titles reflect the ruleset.

    def update_stats(self, results_one_test: Dict[str, Tuple[bool, float, Optional[float], Optional[float]]], test_num: int):
        """ Safely updates global statistics dictionaries based on results from one test run."""
        global passed_tests, total_tests
        with lock:
            for jar_file, result_tuple in results_one_test.items():
                total_tests += 1
                if len(result_tuple) != 4:
                     self.print_red(f"内部错误: Test {test_num} for {os.path.basename(jar_file)} 返回了格式错误的结果: {result_tuple}")
                     test_times.setdefault(jar_file, []).append(np.nan)
                     avg_completion_times.setdefault(jar_file, []).append(np.nan)
                     power_consumptions.setdefault(jar_file, []).append(np.nan)
                     continue
                is_correct, elapsed, avg_wt, power = result_tuple
                # Ensure elapsed is treated as NaN if it's not a positive float
                valid_elapsed = elapsed if isinstance(elapsed, (int, float)) and not math.isnan(elapsed) and elapsed > 0 else np.nan
                test_times.setdefault(jar_file, []).append(valid_elapsed)
                # Ensure avg_wt and power are NaN if None or NaN
                avg_completion_times.setdefault(jar_file, []).append(avg_wt if avg_wt is not None and not math.isnan(avg_wt) else np.nan)
                power_consumptions.setdefault(jar_file, []).append(power if power is not None and not math.isnan(power) else np.nan)
                if is_correct: passed_tests += 1


    def calculate_rankings(self):
        """Calculates average performance metrics for ranking based on *valid* runs (handles NaN)."""
        with lock: # Use lock to access global data stores safely
            local_test_times = {k: list(v) for k, v in test_times.items()}
            local_avg_completion_times = {k: list(v) for k, v in avg_completion_times.items()}
            local_power_consumptions = {k: list(v) for k, v in power_consumptions.items()}

        time_avgs, completion_avgs, power_avgs = {}, {}, {}
        num_passed_wt = {jar: 0 for jar in TEST_JAR_FILES} # Count passes where WT is valid
        num_passed_power = {jar: 0 for jar in TEST_JAR_FILES} # Count passes where Power is valid
        num_run = {jar: 0 for jar in TEST_JAR_FILES}

        for jar in TEST_JAR_FILES:
            times_list = local_test_times.get(jar, [])
            # Filter only valid positive times for average calculation
            valid_times = [t for t in times_list if isinstance(t, (int, float)) and not math.isnan(t) and t > 0]
            num_run[jar] = len(times_list) # Total attempts recorded (includes failed/timeout)
            time_avgs[jar] = np.mean(valid_times) if valid_times else float('inf')

            wts_list = local_avg_completion_times.get(jar, [])
            powers_list = local_power_consumptions.get(jar, [])
            # Filter only valid non-NaN values for calculation
            valid_wts = [wt for wt in wts_list if wt is not None and not math.isnan(wt)]
            valid_powers = [p for p in powers_list if p is not None and not math.isnan(p)]
            num_passed_wt[jar] = len(valid_wts) # Count valid WT results
            num_passed_power[jar] = len(valid_powers) # Count valid Power results
            completion_avgs[jar] = np.mean(valid_wts) if valid_wts else float('inf')
            power_avgs[jar] = np.mean(valid_powers) if valid_powers else float('inf')

            # Ensure Inf representation if calculation failed or resulted in NaN
            if math.isnan(time_avgs[jar]): time_avgs[jar] = float('inf')
            if math.isnan(completion_avgs[jar]): completion_avgs[jar] = float('inf')
            if math.isnan(power_avgs[jar]): power_avgs[jar] = float('inf')

        # Sort time by average time, then name
        time_rank = sorted(time_avgs.items(), key=lambda item: (item[1], os.path.basename(item[0])))
        # Sort completion time by average WT, then number of valid WT points (higher is better), then name
        completion_rank = sorted(completion_avgs.items(), key=lambda item: (item[1], -num_passed_wt.get(item[0], 0), os.path.basename(item[0])))
        # Sort power by average power, then number of valid Power points (higher is better), then name
        power_rank = sorted(power_avgs.items(), key=lambda item: (item[1], -num_passed_power.get(item[0], 0), os.path.basename(item[0])))

        # Pass count for WT is used for completion ranking display
        # Pass count for Power is used for power ranking display
        return time_rank, completion_rank, power_rank, num_passed_wt, num_passed_power, num_run


    def print_rankings(self):
        """Prints the ranked average performance metrics."""
        time_rank, completion_rank, power_rank, num_passed_wt, num_passed_power, num_run = self.calculate_rankings()
        max_len = max(len(os.path.basename(j)) for j in TEST_JAR_FILES) if TEST_JAR_FILES else 20

        print("\n--- 平均运行时间排名 (所有测试运行, 越低越好) ---")
        print(f"{'排名':<4} {'JAR 文件':<{max_len}} {'平均时间 (秒)':<15} {'运行次数'}"); print("-" * (max_len + 35))
        for rank, (jar, time_avg) in enumerate(time_rank, 1):
             jar_name = os.path.basename(jar); run_count = num_run.get(jar, 0)
             value = f"{time_avg:.3f}" if not math.isinf(time_avg) else "N/A"
             print(f"{rank:<4} {jar_name:<{max_len}} {value:<15} ({run_count} 次)")
        print("-" * (max_len + 35))

        print("\n--- 平均加权完成时间(WT)排名 (仅基于通过测试点, 越低越好) ---")
        print(f"{'排名':<4} {'JAR 文件':<{max_len}} {'平均 WT':<15} {'有效WT/运行次数'}"); print("-" * (max_len + 45)) # Adjusted label
        for rank, (jar, completion_avg) in enumerate(completion_rank, 1):
             jar_name = os.path.basename(jar); passed_count = num_passed_wt.get(jar, 0); run_count = num_run.get(jar, 0)
             value = f"{completion_avg:.4f}" if not math.isinf(completion_avg) else "N/A"
             pass_info = f"({passed_count}/{run_count})" if run_count > 0 else "(0/0)"
             print(f"{rank:<4} {jar_name:<{max_len}} {value:<15} {pass_info}")
        print("-" * (max_len + 45))

        print("\n--- 平均系统耗电量(W)排名 (仅基于通过测试点, 越低越好) ---")
        print(f"{'排名':<4} {'JAR 文件':<{max_len}} {'平均耗电量 (W)':<18} {'有效功耗/运行次数'}"); print("-" * (max_len + 50)) # Adjusted label
        for rank, (jar, power_avg) in enumerate(power_rank, 1):
             jar_name = os.path.basename(jar); passed_count = num_passed_power.get(jar, 0); run_count = num_run.get(jar, 0)
             value = f"{power_avg:.1f}" if not math.isinf(power_avg) else "N/A"
             pass_info = f"({passed_count}/{run_count})" if run_count > 0 else "(0/0)"
             print(f"{rank:<4} {jar_name:<{max_len}} {value:<18} {pass_info}")
        print("-" * (max_len + 50))


    def _generate_plot(self, data_dict: Dict[str, List[float]], title: str, ylabel: str, filename: str, show_only_valid: bool):
        """Helper function to generate plots, handling NaNs and labeling."""
        with lock: local_data_dict = {k: list(v) for k, v in data_dict.items()}
        if not local_data_dict or not any(local_data_dict.values()): print(f"信息: 无数据可用于绘制 '{title}'"); return

        plt.style.use('seaborn-v0_8-whitegrid'); plt.figure(figsize=(12, 7))
        num_tests = max((len(v) for v in local_data_dict.values() if v), default=0)
        if num_tests == 0: print(f"信息: '{title}' 数据列表为空，跳过绘图。"); plt.close(); return

        test_numbers = list(range(1, num_tests + 1)); plot_handles = []
        for jar, values in local_data_dict.items():
            jar_name = os.path.basename(jar)
            if not values: continue
            # Pad with NaN if this JAR has fewer results than the max
            padded_values = values[:num_tests] + [np.nan] * max(0, num_tests - len(values))
            # Convert all to float, ensure None becomes NaN
            numeric_values = [float(v) if isinstance(v, (int, float)) and v is not None else np.nan for v in padded_values]
            np_values = np.array(numeric_values, dtype=float)
            # Use masked array to prevent plotting NaNs as zero or connecting across them if show_only_valid
            masked_values = np.ma.masked_invalid(np_values)
            if show_only_valid:
                line, = plt.plot(test_numbers, masked_values, marker='.', ms=5, linestyle='-', label=jar_name)
            else: # For runtime, plot everything including NaNs (which will appear as gaps)
                line, = plt.plot(test_numbers, np_values, marker='.', ms=5, linestyle='-', label=jar_name) # Plot raw including NaN
            plot_handles.append(line)

        plt.xlabel('测试编号'); plt.ylabel(ylabel); plt.title(f"{title} (HW6+UPDATE)") # Updated title
        if num_tests > 0:
             step = max(1, math.ceil(num_tests / 15))
             plt.xticks(np.arange(1, num_tests + 1, step=step))
        # Set y-axis lower limit to 0 if it's not runtime, otherwise auto
        if ylabel != '时间/秒': plt.ylim(bottom=0)
        plt.legend(handles=plot_handles, bbox_to_anchor=(1.04, 1), loc="upper left", borderaxespad=0.)
        plt.grid(True, which='major', axis='y', linestyle='--', alpha=0.7)
        plt.grid(True, which='major', axis='x', linestyle=':', alpha=0.5)
        plt.tight_layout()

        save_filename = filename.replace(' ', '_').replace('.png', '_hw6update.png') # Updated filename suffix
        try: plt.savefig(save_filename, dpi=100, bbox_inches='tight'); print(f"图表 '{title}' 已保存为 {save_filename}")
        except Exception as e: print(f"保存图表 {save_filename} 时出错: {e}", file=sys.stderr)
        plt.close()

    def plot_runtime(self): self._generate_plot(test_times, '总运行时间', '时间/秒', 'total running time.png', show_only_valid=False)
    def plot_completion_time(self): self._generate_plot(avg_completion_times, '平均加权完成时间', '平均加权完成时间', 'weighted avg time.png', show_only_valid=True)
    def plot_power_consumption(self): self._generate_plot(power_consumptions, '系统耗电量', '耗电量/W', 'elec cons.png', show_only_valid=True)

    def plot_scores(self, ranked_scores):
        """Plots the final calculated composite scores as a bar chart."""
        if not ranked_scores: print("信息: 无评分数据可绘制。"); return
        jars = [os.path.basename(jar) for jar, _ in ranked_scores]; scores = [score for _, score in ranked_scores]
        plt.style.use('seaborn-v0_8-whitegrid'); fig_width = max(8, len(jars) * 0.9 + 2); plt.figure(figsize=(fig_width, 6))
        colors = plt.cm.viridis(np.linspace(0.4, 0.9, len(jars))); bars = plt.bar(jars, scores, color=colors, edgecolor='black', linewidth=0.8)
        plt.ylabel('综合性能得分 (满分 15)'); plt.title('电梯调度程序综合性能得分排名 (HW6+UPDATE)') # Updated title
        plt.xticks(rotation=40, ha='right', fontsize=9); plt.ylim(0, 15.5); plt.grid(True, axis='y', linestyle='--', alpha=0.7)
        plt.axhline(15, color='red', linestyle=':', linewidth=1, alpha=0.5, label='满分线 (15)')
        for bar in bars:
             yval = bar.get_height()
             if yval > 0.01: plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.15, f'{yval:.2f}', va='bottom', ha='center', fontsize=8, color='black')
        plt.legend(); plt.tight_layout()
        save_filename = 'overall ranking_HW6update.png' # Updated filename
        try: plt.savefig(save_filename, dpi=100, bbox_inches='tight'); print(f"综合性能得分排名图已保存为 {save_filename}")
        except Exception as e: print(f"保存评分图表 {save_filename} 时出错: {e}", file=sys.stderr)
        plt.close()


# --- Main Execution Logic ---
def main():
    global TEST_JAR_FILES, DEFAULT_PASSENGER_COUNT, DEFAULT_SCHE_COMMAND_COUNT, DEFAULT_UPDATE_COMMAND_COUNT
    global DEFAULT_TEST_COUNT, TIMEOUT_SECONDS, SINGLE_INSTANCE_TEST, DATA_GENERATOR_SCRIPT

    print("\n=== BUAA OO HW6+UPDATE 自动评测机 ===")
    script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()

    # Auto-detect JARs (same logic)
    if not TEST_JAR_FILES:
        print("配置 TEST_JAR_FILES 为空, 尝试在当前目录自动检测 JAR 文件...")
        try:
            found_jars = [os.path.join(script_dir, f) for f in os.listdir(script_dir) if f.lower().endswith('.jar')]
            if found_jars: TEST_JAR_FILES = found_jars; print(f"自动检测到以下 JAR 文件: {', '.join(map(os.path.basename, TEST_JAR_FILES))}")
            else: print("错误：未在配置中指定 JAR 文件，且当前目录未找到 .jar 文件。", file=sys.stderr); sys.exit(1)
        except Exception as e: print(f"自动检测 JAR 文件时出错: {e}", file=sys.stderr); sys.exit(1)
    else: # Validate configured JARs
         valid_jars = []
         for jar_path_config in TEST_JAR_FILES:
             potential_path_rel = os.path.join(script_dir, jar_path_config)
             if os.path.isfile(potential_path_rel): valid_jars.append(potential_path_rel)
             elif os.path.isfile(jar_path_config): valid_jars.append(os.path.abspath(jar_path_config))
             else: print(f"警告: 配置的 JAR 文件 '{jar_path_config}' 未找到，将忽略。", file=sys.stderr)
         TEST_JAR_FILES = valid_jars
         if not TEST_JAR_FILES: print("错误：所有在 TEST_JAR_FILES 中配置的 JAR 文件都无法找到。", file=sys.stderr); sys.exit(1)
         print(f"使用验证后存在的 JAR 文件: {', '.join(map(os.path.basename, TEST_JAR_FILES))}")

    # Check for Data Generator (same logic)
    potential_gen_path = os.path.join(script_dir, DATA_GENERATOR_SCRIPT)
    if os.path.isfile(potential_gen_path): DATA_GENERATOR_SCRIPT = potential_gen_path; print(f"使用数据生成器: {DATA_GENERATOR_SCRIPT}")
    elif not os.path.isfile(DATA_GENERATOR_SCRIPT) and not SINGLE_INSTANCE_TEST:
        print(f"警告: 未找到数据生成脚本 '{DATA_GENERATOR_SCRIPT}'。除非使用 --single 模式，否则无法运行。", file=sys.stderr)

    # --- Command Line Arguments Parsing (Updated for UPDATE count) ---
    args = sys.argv[1:]
    test_count = DEFAULT_TEST_COUNT
    passenger_count = DEFAULT_PASSENGER_COUNT
    sche_command_count = DEFAULT_SCHE_COMMAND_COUNT
    update_command_count = DEFAULT_UPDATE_COMMAND_COUNT # Added UPDATE count
    timeout_override = None
    run_single_test = SINGLE_INSTANCE_TEST # Initialize from config

    positional_args = []
    # Updated Usage Message
    usage_msg = "用法: python script.py [测试次数] [乘客数] [SCHE数] [UPDATE数] [超时秒数] [--single]"
    for arg in args:
        if arg == '--single':
            run_single_test = True # Set the flag if --single is present
        elif arg.startswith('-'):
            print(f"错误: 未知选项 '{arg}'", file=sys.stderr); print(usage_msg); sys.exit(1)
        else:
            positional_args.append(arg)

    try:
        # Parse positional arguments based on new order
        if len(positional_args) > 0: test_count = int(positional_args[0])
        if len(positional_args) > 1: passenger_count = int(positional_args[1])
        if len(positional_args) > 2: sche_command_count = int(positional_args[2])
        if len(positional_args) > 3: update_command_count = int(positional_args[3]) # UPDATE is 4th arg
        if len(positional_args) > 4: timeout_override = int(positional_args[4])   # Timeout is 5th arg
        if len(positional_args) > 5: print("错误：提供了过多的位置参数。", file=sys.stderr); print(usage_msg); sys.exit(1)
    except ValueError: print("错误：命令行参数（次数、数量、超时）必须是整数。", file=sys.stderr); print(usage_msg); sys.exit(1)

    # Apply overrides
    if timeout_override is not None:
        if timeout_override > 0: TIMEOUT_SECONDS = timeout_override; print(f"使用命令行设置超时: {TIMEOUT_SECONDS} 秒")
        else: print("错误: 超时秒数必须为正整数。", file=sys.stderr); sys.exit(1)

    # --- Handle Single Instance Mode ---
    # Check the flag *after* parsing positional args so test_count can be overridden
    if run_single_test:
        SINGLE_INSTANCE_TEST = True # Set the global flag
        # Keep the test_count determined by default or command line
        print(f"模式: 单例测试 (使用 test.txt 进行 {test_count} 次测试)")
        # These counts are ignored for data generation in single mode, set to placeholder
        passenger_count, sche_command_count, update_command_count = -1, -1, -1
    elif not os.path.isfile(DATA_GENERATOR_SCRIPT):
         print(f"错误: 未找到数据生成脚本 '{DATA_GENERATOR_SCRIPT}' 且未指定 --single 模式。", file=sys.stderr); sys.exit(1)

    # Validate counts (only if not single instance)
    if not SINGLE_INSTANCE_TEST:
        if test_count <= 0 or passenger_count < 0 or sche_command_count < 0 or update_command_count < 0:
            print("错误: 测试次数必须 > 0, 乘客数/SCHE数/UPDATE数必须 >= 0。", file=sys.stderr); sys.exit(1)

    # Print final configuration before running
    if not SINGLE_INSTANCE_TEST:
        print(f"配置 -> 测试次数: {test_count}, PRI/测试: {passenger_count}, SCHE_CMD/测试: {sche_command_count}, UPDATE/测试: {update_command_count}")
    else:
        # Print info for single mode, showing the actual test count used
        print(f"配置 -> 测试模式: 单例 (使用 test.txt), 测试次数: {test_count}, PRI/SCHE/UPDATE 数被忽略")
    print(f"配置 -> 超时: {TIMEOUT_SECONDS}秒")

    # --- Run Evaluation ---
    evaluator = TestEvaluator()
    # Pass all relevant counts to the suite runner
    # In single mode, p_count, sche_count, update_count are -1 but ignored by generate_input_data
    evaluator.run_test_suite(test_count, passenger_count, sche_command_count, update_command_count)


if __name__ == "__main__":
    # Setup Matplotlib Font (same logic)
    try:
        potential_cjk_fonts = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Micro Hei', 'Arial Unicode MS', 'Source Han Sans SC', 'Noto Sans CJK SC', 'PingFang SC', 'Hiragino Sans GB']
        fallback_fonts = ['DejaVu Sans', 'sans-serif']
        available_fonts = set(f.name for f in matplotlib.font_manager.fontManager.ttflist)
        font_to_use = next((font for font in potential_cjk_fonts if font in available_fonts), None)
        if font_to_use:
            print(f"Matplotlib 绘图: 找到并使用字体 '{font_to_use}'。")
            matplotlib.rcParams['font.family'] = 'sans-serif'
            matplotlib.rcParams['font.sans-serif'] = [font_to_use] + fallback_fonts
        else:
            print("警告: 未找到推荐的中文字体。图表中的中文可能无法正确显示。", file=sys.stderr)
            matplotlib.rcParams['font.family'] = 'sans-serif'; matplotlib.rcParams['font.sans-serif'] = fallback_fonts
        matplotlib.rcParams['axes.unicode_minus'] = False
        print(f"Matplotlib 使用的 sans-serif 字体列表: {matplotlib.rcParams['font.sans-serif']}")
    except Exception as e: print(f"设置 Matplotlib 字体时发生错误: {e}", file=sys.stderr)

    # --- Execute Main Logic ---
    main()