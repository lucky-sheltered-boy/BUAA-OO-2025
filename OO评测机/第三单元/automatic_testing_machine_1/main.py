import random
import sys
import string
import math
import os
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import time
import shlex
import datetime
import shutil

# --- Configuration Constants (放在顶部方便修改) ---
TOTAL_TESTS = 200               # 生成输入的组数（即测试用例数）
LINES_PER_TEST = 3000          # 每组输入数据的命令条数 (传递给生成器)
STD_IDENTIFIER = "std"         # 用于识别标准(参考)JAR文件的名称中的子串
RESULTS_DIR = "latest_results" # 结果目录名，设置为固定名称方便查看最新结果
MAX_THREADS = None             # 最大线程数，None表示根据CPU核数自动确定 (建议留None或设置一个合理的值，如CPU核数*2)
GENERATOR_SCRIPT_PATH = "data_generator.py" # 输入生成脚本的路径
GENERATOR_TIMEOUT_SECONDS = 500 # 输入生成脚本的超时时间（秒），针对大量数据生成调大
JAR_TIMEOUT_SECONDS = 10       # 每个JAR执行的超时时间（秒）
TOTAL_TIMEOUT_SECONDS = 100000     # 整个测试过程的总超时时间（秒），包括所有JAR的执行和输入生成

# 指定要测试的JAR文件列表（如果为空，则会自动扫描当前目录非STD_IDENTIFIER的JAR）
# 如果指定了，则只测试列表中的JAR，不进行扫描
TEST_JARS_TO_RUN_EXPLICIT = [
    # 'zcy.jar',
    # 'sqh.jar',
    # 'jyx.jar',
    # 'lty.jar'
    '洞明星.jar',
    '开阳星.jar',
    '天枢星.jar',
    '天璇星.jar',
    '摇光星.jar',
    '玉衡星.jar'
]
# 指定标准JAR文件路径（如果为None，则会扫描当前目录寻找包含STD_IDENTIFIER的JAR）
STD_JAR_EXPLICIT = 'zjy.jar'


# --- Constants ---
# ANSI Color Codes
COLOR_GREEN = '\033[92m'
COLOR_RED = '\033[91m'
COLOR_YELLOW = '\033[93m'
COLOR_RESET = '\033[0m'

# Command aliases/map (kept for completeness, not used for generation here)
# NOTE: The command aliases/map is part of the generator script, not the runner.
# Keeping it here is harmless but unnecessary for this script's logic.
# ALIAS_MAP = { ... }
# INSTRUCTION_MAP = {v: k for k, v in ALIAS_MAP.items()}


# --- JAR Execution and Test Logic ---

def run_jar(jar_path, input_file_path, timeout_seconds=JAR_TIMEOUT_SECONDS):
    """
    Runs a JAR file with input from a file and returns output, errors, return code, and execution time.
    Returns (stdout string, stderr string, return code, time taken).
    Timeout is handled internally. Input is read from input_file_path.
    """
    start_time = time.time()
    stdout, stderr, returncode = "", "", -99

    if not os.path.exists(jar_path):
         stderr = f"Error: JAR file not found at {jar_path}."
         return "", stderr, -1, 0

    try:
        command = ["java", "-jar", jar_path]

        with open(input_file_path, 'r', encoding='utf-8', errors='ignore') as infile:
            process = subprocess.Popen(
                command,
                stdin=infile,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'
            )

            try:
                 stdout, stderr = process.communicate(timeout=timeout_seconds)
                 returncode = process.returncode
            except subprocess.TimeoutExpired:
                 process.kill()
                 stdout, stderr = process.communicate()
                 stderr = f"Error: Process timed out after {timeout_seconds} seconds.\n" + stderr
                 returncode = -2
            except Exception as e:
                stderr = f"An unexpected error occurred during process communication: {e}\n" + stderr
                returncode = -3
                if process.poll() is None:
                     process.kill()

    except FileNotFoundError:
        stderr = f"Error: java command not found or JAR path was invalid initially."
        returncode = -1
    except Exception as e:
        stderr = f"An unexpected error occurred while starting JAR process: {e}"
        returncode = -3

    end_time = time.time()
    duration = end_time - start_time

    return stdout, stderr, returncode, duration

def generate_input(generator_script_path, lines_per_test, output_file_path, timeout_seconds=GENERATOR_TIMEOUT_SECONDS):
    """
    Runs the data_generator.py script to generate input directly into output_file_path.
    Returns True on success, False on failure, and an error message (or None).
    """
    try:
        command = [sys.executable, generator_script_path, str(lines_per_test)]

        with open(output_file_path, 'w', encoding='utf-8', errors='replace') as outfile:
            process = subprocess.run(
                command,
                stdout=outfile,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=timeout_seconds
            )
            stderr = process.stderr
            returncode = process.returncode

        if returncode != 0:
            return False, f"Data generator script '{generator_script_path}' failed with return code {returncode}.\nStderr:\n{stderr}"
        if stderr:
             print(f"{COLOR_YELLOW}Warning: Data generator script '{generator_script_path}' produced stderr:\n{stderr}{COLOR_RESET}", file=sys.stderr)

        return True, None

    except FileNotFoundError:
        return False, f"Error: Data generator script not found at '{generator_script_path}'."
    except subprocess.TimeoutExpired:
        return False, f"Error: Data generator script timed out after {timeout_seconds} seconds."
    except Exception as e:
        return False, f"An unexpected error occurred while running data generator: {e}"

def run_jar_test_case(std_jar, test_jar, input_file_path, test_number, case_dir, jar_timeout):
    """
    Runs a single test JAR against the standard JAR using a pre-generated input file.
    Saves results to case_dir.
    Returns (test_jar_path, test_number, result_type).
    Result type is 'pass', 'fail', or 'timeout'.
    """
    thread_name = threading.current_thread().name
    jar_short_name = os.path.basename(test_jar)
    std_jar_short_name = os.path.basename(std_jar)

    # Run standard JAR first
    std_stdout, std_stderr, std_returncode, std_duration = run_jar(std_jar, input_file_path, jar_timeout)

    # Save standard JAR outputs
    with open(os.path.join(case_dir, f"{std_jar_short_name}_output.txt"), "w", encoding='utf-8', errors='replace') as f:
        f.write(f"# Execution Time: {std_duration:.4f} seconds\n")
        f.write(f"# Return Code: {std_returncode}\n")
        f.write(std_stdout)
    with open(os.path.join(case_dir, f"{std_jar_short_name}_stderr.txt"), "w", encoding='utf-8', errors='replace') as f:
         f.write(f"# Execution Time: {std_duration:.4f} seconds\n")
         f.write(f"# Return Code: {std_returncode}\n")
         f.write(std_stderr)

    # Check if standard JAR run was successful (as a reference)
    if std_returncode != 0 or std_stderr.strip():
        std_ok = False
        print(f"[{thread_name}] Std JAR error on Test {test_number}. Running test JAR for comparison anyway.", file=sys.stderr)
    else:
        std_ok = True

    # Run test JAR
    test_stdout, test_stderr, test_returncode, test_duration = run_jar(test_jar, input_file_path, jar_timeout)

    # Save test JAR outputs
    with open(os.path.join(case_dir, f"{jar_short_name}_output.txt"), "w", encoding='utf-8', errors='replace') as f:
        f.write(f"# Execution Time: {test_duration:.4f} seconds\n")
        f.write(f"# Return Code: {test_returncode}\n")
        f.write(test_stdout)
    with open(os.path.join(case_dir, f"{jar_short_name}_stderr.txt"), "w", encoding='utf-8', errors='replace') as f:
        f.write(f"# Execution Time: {test_duration:.4f} seconds\n")
        f.write(f"# Return Code: {test_returncode}\n")
        f.write(test_stderr)

    # Determine result for this test JAR on this test case
    result_type = 'fail' # Assume fail by default

    if test_returncode == -2:
         result_type = 'timeout'
         print(f"[{thread_name}] Test {test_number} {COLOR_YELLOW}TIMED OUT!{COLOR_RESET} for {jar_short_name}", file=sys.stderr)
    elif test_returncode != 0 or test_stderr.strip():
        print(f"[{thread_name}] Test {test_number} {COLOR_RED}FAILED (Runtime Error/Stderr)!{COLOR_RESET} for {jar_short_name}", file=sys.stderr)
    elif not std_ok:
         print(f"[{thread_name}] Test {test_number} {COLOR_RED}FAILED (Std Error)!{COLOR_RESET} for {jar_short_name}", file=sys.stderr)
    elif std_stdout.strip() != test_stdout.strip():
        reason = f"Outputs differ (Std Time: {std_duration:.4f}s, Test Time: {test_duration:.4f}s)."
        print(f"[{thread_name}] Test {test_number} {COLOR_RED}FAILED (Output Diff)!{COLOR_RESET} for {jar_short_name}", file=sys.stderr)
        diff_file_path = os.path.join(case_dir, f"{jar_short_name}_output_diff.txt")
        try:
             import difflib
             with open(diff_file_path, "w", encoding='utf-8', errors='replace') as f:
                  std_lines = std_stdout.strip().splitlines(keepends=True)
                  test_lines = test_stdout.strip().splitlines(keepends=True)
                  f.writelines(difflib.unified_diff(
                      std_lines,
                      test_lines,
                      fromfile=std_jar_short_name,
                      tofile=jar_short_name,
                      lineterm=''
                  ))
        except ImportError:
             pass
        except Exception as e:
             print(f"[{thread_name}] Warning: Failed to save diff file for {jar_short_name} test {test_number}: {e}", file=sys.stderr)
    else:
        result_type = 'pass'
        print(f"[{thread_name}] Test {test_number} {COLOR_GREEN}PASSED!{COLOR_RESET} for {jar_short_name} (Std Time: {std_duration:.4f}s, Test Time: {test_duration:.4f}s)")

    return (test_jar, test_number, result_type)

# --- Main Program ---

def main():
    total_tests = TOTAL_TESTS
    lines_per_test = LINES_PER_TEST
    std_identifier = STD_IDENTIFIER
    results_dir = RESULTS_DIR
    max_threads = MAX_THREADS
    generator_script_path = GENERATOR_SCRIPT_PATH
    jar_timeout = JAR_TIMEOUT_SECONDS
    total_timeout = TOTAL_TIMEOUT_SECONDS
    explicit_test_jars = TEST_JARS_TO_RUN_EXPLICIT
    explicit_std_jar = STD_JAR_EXPLICIT

    print(f"{COLOR_YELLOW}--- Test Harness Configuration ---{COLOR_RESET}", file=sys.stderr)
    print(f"Total test cases (input sets): {total_tests}", file=sys.stderr)
    print(f"Lines per test case input: {lines_per_test}", file=sys.stderr)
    print(f"Generator script: '{generator_script_path}'", file=sys.stderr)
    print(f"Generator timeout: {GENERATOR_TIMEOUT_SECONDS} seconds", file=sys.stderr)
    print(f"JAR execution timeout per test case: {jar_timeout} seconds", file=sys.stderr)
    print(f"Total test run timeout: {total_timeout} seconds", file=sys.stderr)

    if total_tests < 0:
        print(f"{COLOR_RED}Error: Total test cases cannot be negative.{COLOR_RESET}", file=sys.stderr)
        sys.exit(1)
    if lines_per_test < 0:
         print(f"{COLOR_RED}Error: Lines per test cannot be negative.{COLOR_RESET}", file=sys.stderr)
         sys.exit(1)
    if jar_timeout <= 0:
         print(f"{COLOR_RED}Error: JAR timeout must be positive.{COLOR_RESET}", file=sys.stderr)
         sys.exit(1)
    if GENERATOR_TIMEOUT_SECONDS <= 0:
         print(f"{COLOR_RED}Error: Generator timeout must be positive.{COLOR_RESET}", file=sys.stderr)
         sys.exit(1)
    if total_timeout <= 0:
        print(f"{COLOR_RED}Error: Total timeout must be positive.{COLOR_RESET}", file=sys.stderr)
        sys.exit(1)
    if total_tests == 0:
         print(f"{COLOR_YELLOW}Warning: TOTAL_TESTS is set to 0. No tests will be run.{COLOR_RESET}", file=sys.stderr)


    if not os.path.exists(generator_script_path):
        print(f"{COLOR_RED}Error: Generator script not found at '{generator_script_path}'.{COLOR_RESET}", file=sys.stderr)
        sys.exit(1)
    if explicit_std_jar is not None and not os.path.exists(explicit_std_jar):
         print(f"{COLOR_RED}Error: Explicit standard JAR not found at '{explicit_std_jar}'.{COLOR_RESET}", file=sys.stderr)
         sys.exit(1)


    # Determine results directory name and clean up previous runs
    print(f"Results will be saved in '{results_dir}'", file=sys.stderr)
    if os.path.exists(results_dir):
        print(f"{COLOR_YELLOW}Clearing previous results directory: '{results_dir}'...{COLOR_RESET}", file=sys.stderr)
        try:
            shutil.rmtree(results_dir)
            print(f"{COLOR_GREEN}Previous results cleared.{COLOR_RESET}", file=sys.stderr)
        except Exception as e:
            print(f"{COLOR_RED}Error clearing results directory '{results_dir}': {e}{COLOR_RESET}", file=sys.stderr)
            sys.exit(1)
    os.makedirs(results_dir, exist_ok=True)


    # --- Discover JAR files ---
    std_jar = explicit_std_jar
    test_jars_to_run = []

    if explicit_std_jar is None or not explicit_test_jars:
        print(f"\nScanning for JAR files in '{os.getcwd()}'...", file=sys.stderr)
        jar_files = [f for f in os.listdir(".") if os.path.isfile(f) and f.endswith(".jar")]

        if explicit_std_jar is None:
            std_jars_found = [jar for jar in jar_files if std_identifier.lower() in jar.lower()]
            if not std_jars_found:
                 print(f"{COLOR_RED}Error: No standard JAR file found containing '{std_identifier}' in its name.{COLOR_RESET}", file=sys.stderr)
                 sys.exit(1)
            if len(std_jars_found) > 1:
                 print(f"{COLOR_YELLOW}Warning: Multiple standard JARs found containing '{std_identifier}': {', '.join(std_jars_found)}. Using the first one: {std_jars_found[0]}{COLOR_RESET}", file=sys.stderr)
            std_jar = std_jars_found[0]

        if not explicit_test_jars:
             test_jars_to_run = [jar for jar in jar_files if jar != std_jar]

    else:
        std_jar = explicit_std_jar
        test_jars_to_run = []
        missing_jars = []
        for jar in explicit_test_jars:
             if os.path.exists(jar) and jar != std_jar:
                  test_jars_to_run.append(jar)
             elif not os.path.exists(jar):
                  missing_jars.append(jar)

        if missing_jars:
             print(f"{COLOR_YELLOW}Warning: Some explicit test JARs not found and will be skipped: {', '.join(missing_jars)}{COLOR_RESET}", file=sys.stderr)


    if std_jar is None or not os.path.exists(std_jar):
         print(f"{COLOR_RED}Error: Standard JAR '{std_jar}' not found or could not be determined.{COLOR_RESET}", file=sys.stderr)
         sys.exit(1)

    if not test_jars_to_run and total_tests > 0:
        print(f"{COLOR_RED}Error: No test JAR files found to run.{COLOR_RESET}", file=sys.stderr)
        sys.exit(1)

    print(f"\nStandard JAR: {COLOR_GREEN}{std_jar}{COLOR_RESET}", file=sys.stderr)
    print(f"Test JARs ({len(test_jars_to_run)} found): {COLOR_GREEN}{', '.join(test_jars_to_run)}{COLOR_RESET}", file=sys.stderr)
    print("-" * 40, file=sys.stderr)

    actual_max_threads_for_jars = max_threads if max_threads is not None else len(test_jars_to_run)

    try:
         cpu_count = os.cpu_count() or 1
         actual_max_threads_for_jars = min(actual_max_threads_for_jars, cpu_count * 2 + 1)
         if actual_max_threads_for_jars <= 0: actual_max_threads_for_jars = 1
    except NotImplementedError:
         if actual_max_threads_for_jars <= 0: actual_max_threads_for_jars = 1

    if not test_jars_to_run:
        actual_max_threads_for_jars = 1

    print(f"Running JARs for each test case concurrently using up to {actual_max_threads_for_jars} threads.", file=sys.stderr)
    print(f"Starting tests...", file=sys.stderr)
    start_time = time.time()

    results_summary = {jar: {'passed': 0, 'failed': 0, 'timeouts': 0} for jar in test_jars_to_run}
    generation_failed_cases = []
    timed_out = False

    for test_number in range(1, total_tests + 1):
        elapsed_time = time.time() - start_time
        if elapsed_time >= total_timeout:
             print(f"\n{COLOR_RED}Total test run timed out after {total_timeout:.2f} seconds before starting test case {test_number}. Stopping.{COLOR_RESET}", file=sys.stderr)
             timed_out = True
             break

        case_dir = os.path.join(results_dir, f"case_{test_number:04d}")
        os.makedirs(case_dir, exist_ok=True)

        input_file_path = os.path.join(case_dir, "input.txt")
        print(f"[{test_number:04d}] Generating input...")
        gen_success, gen_error = generate_input(generator_script_path, lines_per_test, input_file_path)

        if not gen_success:
            generation_failed_cases.append(test_number)
            gen_error_path = os.path.join(case_dir, "generation_error.txt")
            with open(gen_error_path, "w", encoding='utf-8', errors='replace') as f:
                 f.write(f"Failed to generate input:\n{gen_error}\n")
            print(f"[{test_number:04d}] {COLOR_RED}Input Generation FAILED!{COLOR_RESET}. Reason: {gen_error}", file=sys.stderr)
            continue

        if not test_jars_to_run:
             print(f"[{test_number:04d}] No test JARs configured to run. Skipping JAR execution for this input.", file=sys.stderr)
             continue

        print(f"[{test_number:04d}] Running JARs concurrently...")
        futures = []
        with ThreadPoolExecutor(max_workers=actual_max_threads_for_jars) as executor:
             for test_jar in test_jars_to_run:
                  future = executor.submit(run_jar_test_case, std_jar, test_jar, input_file_path, test_number, case_dir, jar_timeout)
                  futures.append((test_jar, test_number, future))

             for test_jar, test_num_future, future in futures:
                 try:
                     result_tuple = future.result()
                     jar_path, test_num, result_type = result_tuple
                     results_summary[jar_path][result_type] += 1

                 except FutureTimeoutError:
                     jar_path_from_future = test_jar
                     test_num_from_future = test_num_future
                     results_summary[jar_path_from_future]['timeouts'] += 1
                     print(f"[{test_num_from_future:04d}] {COLOR_YELLOW}TIMED OUT (Future Wait)!{COLOR_RESET} for {os.path.basename(jar_path_from_future)}", file=sys.stderr)

                 except Exception as exc:
                     jar_path_from_future = test_jar
                     test_num_from_future = test_num_future
                     results_summary[jar_path_from_future]['failed'] += 1

    end_time = time.time()

    if not timed_out and (end_time - start_time) >= total_timeout:
         print(f"\n{COLOR_RED}Total test run completed just over the {total_timeout:.2f} second limit ({end_time - start_time:.2f}s).{COLOR_RESET}", file=sys.stderr)
         timed_out = True

    print(f"{COLOR_YELLOW}--- Testing Complete ---{COLOR_RESET}", file=sys.stderr)
    if timed_out:
         print(f"{COLOR_RED}Overall: Test run stopped due to total timeout.{COLOR_RESET}", file=sys.stderr)
    else:
        print(f"Total testing time: {end_time - start_time:.2f} seconds", file=sys.stderr)
    print("-" * 40, file=sys.stderr)

    print(f"{COLOR_YELLOW}--- Test Results Summary Per JAR ---{COLOR_RESET}", file=sys.stderr)
    all_passed_overall = True # Flag for the overall "All Passed" status
    for jar_path in test_jars_to_run:
        jar_short_name = os.path.basename(jar_path)
        counts = results_summary.get(jar_path, {'passed': 0, 'failed': 0, 'timeouts': 0})

        passed_count = counts['passed']
        failed_count = counts['failed']
        timeout_count = counts['timeouts']
        total_attempts_for_jar = total_tests

        status_color = COLOR_GREEN
        status_text = "ALL PASSED!"

        if failed_count > 0 or timeout_count > 0:
            status_color = COLOR_RED
            status_text = "FAILED or TIMEOUTS!"
            all_passed_overall = False
        elif passed_count + failed_count + timeout_count < total_tests:
             # If not red, check if any tests were skipped due to generation failures
             status_color = COLOR_YELLOW
             status_text = "INCOMPLETE!"
             all_passed_overall = False # Cannot be overall passed if incomplete tests exist
        # If none of the above, it's green (all_passed_overall remains True if no other JAR fails)


        print(f"  {jar_short_name}: {status_color}{status_text}{COLOR_RESET}", file=sys.stderr)
        print(f"    Passed: {passed_count}/{total_attempts_for_jar}", file=sys.stderr)
        print(f"    Failed: {failed_count}/{total_attempts_for_jar}", file=sys.stderr)
        print(f"    Timeouts: {timeout_count}/{total_attempts_for_jar}", file=sys.stderr)
        print("-" * 20, file=sys.stderr)


    print(f"\n{COLOR_YELLOW}--- Overall Summary ---{COLOR_RESET}", file=sys.stderr)
    if timed_out:
         print(f"{COLOR_RED}Overall: Test run stopped due to total timeout.{COLOR_RESET}", file=sys.stderr)
    elif not test_jars_to_run:
         print(f"{COLOR_YELLOW}Overall: No test JARs were run.{COLOR_RESET}", file=sys.stderr)
    elif all_passed_overall: # Use the new flag
         print(f"{COLOR_GREEN}Overall: All test JARs passed all test cases against the standard JAR.{COLOR_RESET}", file=sys.stderr)
    else:
         print(f"{COLOR_RED}Overall: Some test JARs failed, timed out, or were incomplete. Check details above.{COLOR_RESET}", file=sys.stderr)

    if generation_failed_cases:
         print(f"{COLOR_YELLOW}Warning: Input generation failed for {len(generation_failed_cases)} test case(s): {generation_failed_cases}{COLOR_RESET}", file=sys.stderr)

    print(f"Detailed results saved in '{results_dir}'", file=sys.stderr)
    print("-" * 40, file=sys.stderr)

    # Exit with non-zero code if any test failed, timed out, or generation failed
    if not all_passed_overall or timed_out or generation_failed_cases:
        sys.exit(1)


if __name__ == "__main__":
    main()