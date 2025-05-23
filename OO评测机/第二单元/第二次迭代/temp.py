import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

log_data = """
C:\\Users\\keshi\\.version-fox\\cache\\python\\current\\python.exe D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\Main.py 
Matplotlib 绘图: 找到并使用字体 'SimHei'。
Matplotlib 使用的 sans-serif 字体列表: ['SimHei', 'DejaVu Sans', 'sans-serif']

=== BUAA OO HW6+UPDATE 自动评测机 ===
使用验证后存在的 JAR 文件: zjy.jar, zjy_100.jar, zjy_50.jar, zjy_30.jar, zjy_20.jar, jyx.jar, zcy.jar
使用数据生成器: D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\data_generator.py
配置 -> 测试次数: 200, PRI/测试: 100, SCHE_CMD/测试: 20, UPDATE/测试: 3
配置 -> 超时: 200秒
清理旧的输出和错误文件...

============================================================
=== BUAA OO HW6+UPDATE 自动评测启动 ===
测试JAR包: zjy.jar, zjy_100.jar, zjy_50.jar, zjy_30.jar, zjy_20.jar, jyx.jar, zcy.jar
总测试次数 (n): 200
每次测试请求数 -> PRI: 100, SCHE_CMD: 20, UPDATE: 3
开始时间: 2025-04-12 02:45:52
输入/输出目录: 'test_inputs_hw6_update/'
错误用例目录: 'error_cases_hw6_update/'
超时设置: 200秒
最大并发线程数: 6
============================================================


[TestWorker_0] ===> 开始测试 1 (PRI:100, SCHE_CMD:20, UPDATE:3) <===
执行数据生成脚本: C:\\Users\\keshi\\.version-fox\\cache\\python\\current\\python.exe D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\data_generator.py 100 20 3

[TestWorker_1] ===> 开始测试 2 (PRI:100, SCHE_CMD:20, UPDATE:3) <===
执行数据生成脚本: C:\\Users\\keshi\\.version-fox\\cache\\python\\current\\python.exe D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\data_generator.py 100 20 3

[TestWorker_2] ===> 开始测试 3 (PRI:100, SCHE_CMD:20, UPDATE:3) <===
执行数据生成脚本: C:\\Users\\keshi\\.version-fox\\cache\\python\\current\\python.exe D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\data_generator.py 100 20 3

[TestWorker_3] ===> 开始测试 4 (PRI:100, SCHE_CMD:20, UPDATE:3) <===
执行数据生成脚本: C:\\Users\\keshi\\.version-fox\\cache\\python\\current\\python.exe D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\data_generator.py 100 20 3

[TestWorker_4] ===> 开始测试 5 (PRI:100, SCHE_CMD:20, UPDATE:3) <===
执行数据生成脚本: C:\\Users\\keshi\\.version-fox\\cache\\python\\current\\python.exe D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\data_generator.py 100 20 3

[TestWorker_5] ===> 开始测试 6 (PRI:100, SCHE_CMD:20, UPDATE:3) <===
执行数据生成脚本: C:\\Users\\keshi\\.version-fox\\cache\\python\\current\\python.exe D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\data_generator.py 100 20 3
[TestWorker_2] 测试 3 - 运行 JAR: zjy.jar ...
[TestWorker_0] 测试 1 - 运行 JAR: zjy.jar ...
[TestWorker_2] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy.jar" < "test_inputs_hw6_update\\test_3_zjy_input.txt" > "test_inputs_hw6_update\\test_3_zjy_output.txt" (Timeout: 200s)
[TestWorker_4] 测试 5 - 运行 JAR: zjy.jar ...
[TestWorker_0] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy.jar" < "test_inputs_hw6_update\\test_1_zjy_input.txt" > "test_inputs_hw6_update\\test_1_zjy_output.txt" (Timeout: 200s)
[TestWorker_4] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy.jar" < "test_inputs_hw6_update\\test_5_zjy_input.txt" > "test_inputs_hw6_update\\test_5_zjy_output.txt" (Timeout: 200s)
[TestWorker_3] 测试 4 - 运行 JAR: zjy.jar ...
[TestWorker_3] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy.jar" < "test_inputs_hw6_update\\test_4_zjy_input.txt" > "test_inputs_hw6_update\\test_4_zjy_output.txt" (Timeout: 200s)
[TestWorker_1] 测试 2 - 运行 JAR: zjy.jar ...
[TestWorker_1] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy.jar" < "test_inputs_hw6_update\\test_2_zjy_input.txt" > "test_inputs_hw6_update\\test_2_zjy_output.txt" (Timeout: 200s)
[TestWorker_5] 测试 6 - 运行 JAR: zjy.jar ...
[TestWorker_5] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy.jar" < "test_inputs_hw6_update\\test_6_zjy_input.txt" > "test_inputs_hw6_update\\test_6_zjy_output.txt" (Timeout: 200s)
[TestWorker_4] === 程序 zjy.jar 正常结束 (耗时 52.65s) ===
[TestWorker_4] 测试 5 - 验证 zjy.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_4] 测试 5 对于 zjy.jar 通过! :)
    性能指标 -> 耗时: 52.654s, 平均加权完成时间(WT): 4.7742, 系统耗电量(W): 203.4
[TestWorker_4] 测试 5 - 运行 JAR: zjy_100.jar ...
[TestWorker_4] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy_100.jar" < "test_inputs_hw6_update\\test_5_zjy_100_input.txt" > "test_inputs_hw6_update\\test_5_zjy_100_output.txt" (Timeout: 200s)
[TestWorker_1] === 程序 zjy.jar 正常结束 (耗时 54.12s) ===
[TestWorker_1] 测试 2 - 验证 zjy.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_1] 测试 2 对于 zjy.jar 通过! :)
    性能指标 -> 耗时: 54.118s, 平均加权完成时间(WT): 3.7996, 系统耗电量(W): 218.0
[TestWorker_1] 测试 2 - 运行 JAR: zjy_100.jar ...
[TestWorker_1] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy_100.jar" < "test_inputs_hw6_update\\test_2_zjy_100_input.txt" > "test_inputs_hw6_update\\test_2_zjy_100_output.txt" (Timeout: 200s)
[TestWorker_5] === 程序 zjy.jar 正常结束 (耗时 55.28s) ===
[TestWorker_5] 测试 6 - 验证 zjy.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_5] 测试 6 对于 zjy.jar 通过! :)
    性能指标 -> 耗时: 55.277s, 平均加权完成时间(WT): 4.8434, 系统耗电量(W): 210.8
[TestWorker_5] 测试 6 - 运行 JAR: zjy_100.jar ...
[TestWorker_5] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy_100.jar" < "test_inputs_hw6_update\\test_6_zjy_100_input.txt" > "test_inputs_hw6_update\\test_6_zjy_100_output.txt" (Timeout: 200s)
[TestWorker_3] === 程序 zjy.jar 正常结束 (耗时 57.64s) ===
[TestWorker_3] 测试 4 - 验证 zjy.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_3] 测试 4 对于 zjy.jar 通过! :)
    性能指标 -> 耗时: 57.645s, 平均加权完成时间(WT): 4.5394, 系统耗电量(W): 198.4
[TestWorker_3] 测试 4 - 运行 JAR: zjy_100.jar ...
[TestWorker_3] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy_100.jar" < "test_inputs_hw6_update\\test_4_zjy_100_input.txt" > "test_inputs_hw6_update\\test_4_zjy_100_output.txt" (Timeout: 200s)
[TestWorker_0] === 程序 zjy.jar 正常结束 (耗时 58.73s) ===
[TestWorker_0] 测试 1 - 验证 zjy.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_0] 测试 1 对于 zjy.jar 通过! :)
    性能指标 -> 耗时: 58.734s, 平均加权完成时间(WT): 5.3782, 系统耗电量(W): 182.6
[TestWorker_0] 测试 1 - 运行 JAR: zjy_100.jar ...
[TestWorker_0] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy_100.jar" < "test_inputs_hw6_update\\test_1_zjy_100_input.txt" > "test_inputs_hw6_update\\test_1_zjy_100_output.txt" (Timeout: 200s)
[TestWorker_2] === 程序 zjy.jar 正常结束 (耗时 59.39s) ===
[TestWorker_2] 测试 3 - 验证 zjy.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_2] 测试 3 对于 zjy.jar 通过! :)
    性能指标 -> 耗时: 59.387s, 平均加权完成时间(WT): 6.1382, 系统耗电量(W): 198.6
[TestWorker_2] 测试 3 - 运行 JAR: zjy_100.jar ...
[TestWorker_2] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy_100.jar" < "test_inputs_hw6_update\\test_3_zjy_100_input.txt" > "test_inputs_hw6_update\\test_3_zjy_100_output.txt" (Timeout: 200s)
[TestWorker_4] === 程序 zjy_100.jar 正常结束 (耗时 52.93s) ===
[TestWorker_4] 测试 5 - 验证 zjy_100.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_4] 测试 5 对于 zjy_100.jar 通过! :)
    性能指标 -> 耗时: 52.927s, 平均加权完成时间(WT): 4.5622, 系统耗电量(W): 209.0
[TestWorker_4] 测试 5 - 运行 JAR: zjy_50.jar ...
[TestWorker_4] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy_50.jar" < "test_inputs_hw6_update\\test_5_zjy_50_input.txt" > "test_inputs_hw6_update\\test_5_zjy_50_output.txt" (Timeout: 200s)
[TestWorker_1] === 程序 zjy_100.jar 正常结束 (耗时 56.15s) ===
[TestWorker_1] 测试 2 - 验证 zjy_100.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_1] 测试 2 对于 zjy_100.jar 通过! :)
    性能指标 -> 耗时: 56.152s, 平均加权完成时间(WT): 3.8038, 系统耗电量(W): 238.0
[TestWorker_1] 测试 2 - 运行 JAR: zjy_50.jar ...
[TestWorker_1] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy_50.jar" < "test_inputs_hw6_update\\test_2_zjy_50_input.txt" > "test_inputs_hw6_update\\test_2_zjy_50_output.txt" (Timeout: 200s)
[TestWorker_3] === 程序 zjy_100.jar 正常结束 (耗时 56.66s) ===
[TestWorker_3] 测试 4 - 验证 zjy_100.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_3] 测试 4 对于 zjy_100.jar 通过! :)
    性能指标 -> 耗时: 56.664s, 平均加权完成时间(WT): 4.4846, 系统耗电量(W): 187.6
[TestWorker_3] 测试 4 - 运行 JAR: zjy_50.jar ...
[TestWorker_3] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy_50.jar" < "test_inputs_hw6_update\\test_4_zjy_50_input.txt" > "test_inputs_hw6_update\\test_4_zjy_50_output.txt" (Timeout: 200s)
[TestWorker_0] === 程序 zjy_100.jar 正常结束 (耗时 55.78s) ===
[TestWorker_0] 测试 1 - 验证 zjy_100.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_0] 测试 1 对于 zjy_100.jar 通过! :)
    性能指标 -> 耗时: 55.778s, 平均加权完成时间(WT): 5.0909, 系统耗电量(W): 191.6
[TestWorker_0] 测试 1 - 运行 JAR: zjy_50.jar ...
[TestWorker_0] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy_50.jar" < "test_inputs_hw6_update\\test_1_zjy_50_input.txt" > "test_inputs_hw6_update\\test_1_zjy_50_output.txt" (Timeout: 200s)
[TestWorker_5] === 程序 zjy_100.jar 正常结束 (耗时 60.44s) ===
[TestWorker_5] 测试 6 - 验证 zjy_100.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_5] 测试 6 对于 zjy_100.jar 通过! :)
    性能指标 -> 耗时: 60.440s, 平均加权完成时间(WT): 5.0897, 系统耗电量(W): 202.2
[TestWorker_5] 测试 6 - 运行 JAR: zjy_50.jar ...
[TestWorker_5] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy_50.jar" < "test_inputs_hw6_update\\test_6_zjy_50_input.txt" > "test_inputs_hw6_update\\test_6_zjy_50_output.txt" (Timeout: 200s)
[TestWorker_2] === 程序 zjy_100.jar 正常结束 (耗时 58.08s) ===
[TestWorker_2] 测试 3 - 验证 zjy_100.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_2] 测试 3 对于 zjy_100.jar 通过! :)
    性能指标 -> 耗时: 58.077s, 平均加权完成时间(WT): 5.7447, 系统耗电量(W): 197.8
[TestWorker_2] 测试 3 - 运行 JAR: zjy_50.jar ...
[TestWorker_2] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy_50.jar" < "test_inputs_hw6_update\\test_3_zjy_50_input.txt" > "test_inputs_hw6_update\\test_3_zjy_50_output.txt" (Timeout: 200s)
[TestWorker_4] === 程序 zjy_50.jar 正常结束 (耗时 51.18s) ===
[TestWorker_4] 测试 5 - 验证 zjy_50.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_4] 测试 5 对于 zjy_50.jar 通过! :)
    性能指标 -> 耗时: 51.185s, 平均加权完成时间(WT): 4.2979, 系统耗电量(W): 215.4
[TestWorker_4] 测试 5 - 运行 JAR: zjy_30.jar ...
[TestWorker_4] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy_30.jar" < "test_inputs_hw6_update\\test_5_zjy_30_input.txt" > "test_inputs_hw6_update\\test_5_zjy_30_output.txt" (Timeout: 200s)
[TestWorker_1] === 程序 zjy_50.jar 正常结束 (耗时 56.21s) ===
[TestWorker_1] 测试 2 - 验证 zjy_50.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_1] 测试 2 对于 zjy_50.jar 通过! :)
    性能指标 -> 耗时: 56.213s, 平均加权完成时间(WT): 3.7837, 系统耗电量(W): 240.2
[TestWorker_1] 测试 2 - 运行 JAR: zjy_30.jar ...
[TestWorker_1] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy_30.jar" < "test_inputs_hw6_update\\test_2_zjy_30_input.txt" > "test_inputs_hw6_update\\test_2_zjy_30_output.txt" (Timeout: 200s)
[TestWorker_3] === 程序 zjy_50.jar 正常结束 (耗时 54.22s) ===
[TestWorker_3] 测试 4 - 验证 zjy_50.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_3] 测试 4 对于 zjy_50.jar 通过! :)
    性能指标 -> 耗时: 54.223s, 平均加权完成时间(WT): 4.3971, 系统耗电量(W): 189.0
[TestWorker_3] 测试 4 - 运行 JAR: zjy_30.jar ...
[TestWorker_3] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy_30.jar" < "test_inputs_hw6_update\\test_4_zjy_30_input.txt" > "test_inputs_hw6_update\\test_4_zjy_30_output.txt" (Timeout: 200s)
[TestWorker_0] === 程序 zjy_50.jar 正常结束 (耗时 55.32s) ===
[TestWorker_0] 测试 1 - 验证 zjy_50.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_0] 测试 1 对于 zjy_50.jar 通过! :)
    性能指标 -> 耗时: 55.322s, 平均加权完成时间(WT): 4.9668, 系统耗电量(W): 184.2
[TestWorker_0] 测试 1 - 运行 JAR: zjy_30.jar ...
[TestWorker_0] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy_30.jar" < "test_inputs_hw6_update\\test_1_zjy_30_input.txt" > "test_inputs_hw6_update\\test_1_zjy_30_output.txt" (Timeout: 200s)
[TestWorker_5] === 程序 zjy_50.jar 正常结束 (耗时 55.54s) ===
[TestWorker_5] 测试 6 - 验证 zjy_50.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_5] 测试 6 对于 zjy_50.jar 通过! :)
    性能指标 -> 耗时: 55.536s, 平均加权完成时间(WT): 4.5824, 系统耗电量(W): 202.8
[TestWorker_5] 测试 6 - 运行 JAR: zjy_30.jar ...
[TestWorker_5] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy_30.jar" < "test_inputs_hw6_update\\test_6_zjy_30_input.txt" > "test_inputs_hw6_update\\test_6_zjy_30_output.txt" (Timeout: 200s)
[TestWorker_2] === 程序 zjy_50.jar 正常结束 (耗时 57.51s) ===
[TestWorker_2] 测试 3 - 验证 zjy_50.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_2] 测试 3 对于 zjy_50.jar 通过! :)
    性能指标 -> 耗时: 57.511s, 平均加权完成时间(WT): 6.0115, 系统耗电量(W): 201.4
[TestWorker_2] 测试 3 - 运行 JAR: zjy_30.jar ...
[TestWorker_2] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy_30.jar" < "test_inputs_hw6_update\\test_3_zjy_30_input.txt" > "test_inputs_hw6_update\\test_3_zjy_30_output.txt" (Timeout: 200s)
[TestWorker_4] === 程序 zjy_30.jar 正常结束 (耗时 51.99s) ===
[TestWorker_4] 测试 5 - 验证 zjy_30.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_4] 测试 5 对于 zjy_30.jar 通过! :)
    性能指标 -> 耗时: 51.994s, 平均加权完成时间(WT): 4.1691, 系统耗电量(W): 196.4
[TestWorker_4] 测试 5 - 运行 JAR: zjy_20.jar ...
[TestWorker_4] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy_20.jar" < "test_inputs_hw6_update\\test_5_zjy_20_input.txt" > "test_inputs_hw6_update\\test_5_zjy_20_output.txt" (Timeout: 200s)
[TestWorker_5] === 程序 zjy_30.jar 正常结束 (耗时 49.47s) ===
[TestWorker_5] 测试 6 - 验证 zjy_30.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_5] 测试 6 对于 zjy_30.jar 通过! :)
    性能指标 -> 耗时: 49.468s, 平均加权完成时间(WT): 4.7212, 系统耗电量(W): 212.8
[TestWorker_5] 测试 6 - 运行 JAR: zjy_20.jar ...
[TestWorker_5] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy_20.jar" < "test_inputs_hw6_update\\test_6_zjy_20_input.txt" > "test_inputs_hw6_update\\test_6_zjy_20_output.txt" (Timeout: 200s)
[TestWorker_3] === 程序 zjy_30.jar 正常结束 (耗时 54.42s) ===
[TestWorker_3] 测试 4 - 验证 zjy_30.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_3] 测试 4 对于 zjy_30.jar 通过! :)
    性能指标 -> 耗时: 54.418s, 平均加权完成时间(WT): 4.4280, 系统耗电量(W): 188.2
[TestWorker_3] 测试 4 - 运行 JAR: zjy_20.jar ...
[TestWorker_3] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy_20.jar" < "test_inputs_hw6_update\\test_4_zjy_20_input.txt" > "test_inputs_hw6_update\\test_4_zjy_20_output.txt" (Timeout: 200s)
[TestWorker_1] === 程序 zjy_30.jar 正常结束 (耗时 57.79s) ===
[TestWorker_1] 测试 2 - 验证 zjy_30.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_1] 测试 2 对于 zjy_30.jar 通过! :)
    性能指标 -> 耗时: 57.791s, 平均加权完成时间(WT): 3.9475, 系统耗电量(W): 224.6
[TestWorker_1] 测试 2 - 运行 JAR: zjy_20.jar ...
[TestWorker_1] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy_20.jar" < "test_inputs_hw6_update\\test_2_zjy_20_input.txt" > "test_inputs_hw6_update\\test_2_zjy_20_output.txt" (Timeout: 200s)
[TestWorker_0] === 程序 zjy_30.jar 正常结束 (耗时 55.85s) ===
[TestWorker_0] 测试 1 - 验证 zjy_30.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_0] 测试 1 对于 zjy_30.jar 通过! :)
    性能指标 -> 耗时: 55.846s, 平均加权完成时间(WT): 5.2177, 系统耗电量(W): 185.8
[TestWorker_0] 测试 1 - 运行 JAR: zjy_20.jar ...
[TestWorker_0] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy_20.jar" < "test_inputs_hw6_update\\test_1_zjy_20_input.txt" > "test_inputs_hw6_update\\test_1_zjy_20_output.txt" (Timeout: 200s)
[TestWorker_2] === 程序 zjy_30.jar 正常结束 (耗时 57.81s) ===
[TestWorker_2] 测试 3 - 验证 zjy_30.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_2] 测试 3 对于 zjy_30.jar 通过! :)
    性能指标 -> 耗时: 57.813s, 平均加权完成时间(WT): 5.8922, 系统耗电量(W): 194.6
[TestWorker_2] 测试 3 - 运行 JAR: zjy_20.jar ...
[TestWorker_2] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy_20.jar" < "test_inputs_hw6_update\\test_3_zjy_20_input.txt" > "test_inputs_hw6_update\\test_3_zjy_20_output.txt" (Timeout: 200s)
[TestWorker_4] === 程序 zjy_20.jar 正常结束 (耗时 52.24s) ===
[TestWorker_4] 测试 5 - 验证 zjy_20.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_4] 测试 5 对于 zjy_20.jar 通过! :)
    性能指标 -> 耗时: 52.239s, 平均加权完成时间(WT): 4.2285, 系统耗电量(W): 217.4
[TestWorker_4] 测试 5 - 运行 JAR: jyx.jar ...
[TestWorker_4] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\jyx.jar" < "test_inputs_hw6_update\\test_5_jyx_input.txt" > "test_inputs_hw6_update\\test_5_jyx_output.txt" (Timeout: 200s)
[TestWorker_4] === 程序 jyx.jar 正常结束 (耗时 0.24s) ===
[TestWorker_4] 测试 5 - 程序 jyx.jar 输出结果不正确!
    错误 1: 验证错误: 程序未产生任何有效输出，但输入包含请求。
错误用例已保存到: error_cases_hw6_update\\error_5_jyx_20250412_025014_663907.txt
[TestWorker_4] 测试 5 - 验证 jyx.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_4] 测试 5 - 运行 JAR: zcy.jar ...
[TestWorker_4] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zcy.jar" < "test_inputs_hw6_update\\test_5_zcy_input.txt" > "test_inputs_hw6_update\\test_5_zcy_output.txt" (Timeout: 200s)
[TestWorker_5] === 程序 zjy_20.jar 正常结束 (耗时 50.87s) ===
[TestWorker_5] 测试 6 - 验证 zjy_20.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_5] 测试 6 对于 zjy_20.jar 通过! :)
    性能指标 -> 耗时: 50.866s, 平均加权完成时间(WT): 4.5402, 系统耗电量(W): 211.8
[TestWorker_5] 测试 6 - 运行 JAR: jyx.jar ...
[TestWorker_5] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\jyx.jar" < "test_inputs_hw6_update\\test_6_jyx_input.txt" > "test_inputs_hw6_update\\test_6_jyx_output.txt" (Timeout: 200s)
[TestWorker_5] === 程序 jyx.jar 正常结束 (耗时 0.44s) ===
[TestWorker_5] 测试 6 - 验证 jyx.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_5] 测试 6 - 运行 JAR: zcy.jar ...
[TestWorker_5] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zcy.jar" < "test_inputs_hw6_update\\test_6_zcy_input.txt" > "test_inputs_hw6_update\\test_6_zcy_output.txt" (Timeout: 200s)
[TestWorker_5] 测试 6 - 程序 jyx.jar 输出结果不正确!
    错误 1: 验证错误: 程序未产生任何有效输出，但输入包含请求。
错误用例已保存到: error_cases_hw6_update\\error_6_jyx_20250412_025025_618347.txt
[TestWorker_3] === 程序 zjy_20.jar 正常结束 (耗时 54.38s) ===
[TestWorker_3] 测试 4 - 验证 zjy_20.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_3] 测试 4 对于 zjy_20.jar 通过! :)
    性能指标 -> 耗时: 54.377s, 平均加权完成时间(WT): 4.4105, 系统耗电量(W): 188.2
[TestWorker_3] 测试 4 - 运行 JAR: jyx.jar ...
[TestWorker_3] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\jyx.jar" < "test_inputs_hw6_update\\test_4_jyx_input.txt" > "test_inputs_hw6_update\\test_4_jyx_output.txt" (Timeout: 200s)
[TestWorker_3] === 程序 jyx.jar 正常结束 (耗时 0.24s) ===
[TestWorker_3] 测试 4 - 程序 jyx.jar 输出结果不正确!
    错误 1: 验证错误: 程序未产生任何有效输出，但输入包含请求。
错误用例已保存到: error_cases_hw6_update\\error_4_jyx_20250412_025030_996768.txt
[TestWorker_3] 测试 4 - 验证 jyx.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_3] 测试 4 - 运行 JAR: zcy.jar ...
[TestWorker_3] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zcy.jar" < "test_inputs_hw6_update\\test_4_zcy_input.txt" > "test_inputs_hw6_update\\test_4_zcy_output.txt" (Timeout: 200s)
[TestWorker_1] === 程序 zjy_20.jar 正常结束 (耗时 57.19s) ===
[TestWorker_1] 测试 2 - 验证 zjy_20.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_1] 测试 2 对于 zjy_20.jar 通过! :)
    性能指标 -> 耗时: 57.186s, 平均加权完成时间(WT): 3.9752, 系统耗电量(W): 237.4
[TestWorker_1] 测试 2 - 运行 JAR: jyx.jar ...
[TestWorker_1] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\jyx.jar" < "test_inputs_hw6_update\\test_2_jyx_input.txt" > "test_inputs_hw6_update\\test_2_jyx_output.txt" (Timeout: 200s)
[TestWorker_1] === 程序 jyx.jar 正常结束 (耗时 0.39s) ===
[TestWorker_1] 测试 2 - 验证 jyx.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_1] 测试 2 - 运行 JAR: zcy.jar ...
[TestWorker_1] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zcy.jar" < "test_inputs_hw6_update\\test_2_zcy_input.txt" > "test_inputs_hw6_update\\test_2_zcy_output.txt" (Timeout: 200s)
[TestWorker_1] 测试 2 - 程序 jyx.jar 输出结果不正确!
    错误 1: 验证错误: 程序未产生任何有效输出，但输入包含请求。
错误用例已保存到: error_cases_hw6_update\\error_2_jyx_20250412_025035_350986.txt
[TestWorker_0] === 程序 zjy_20.jar 正常结束 (耗时 56.88s) ===
[TestWorker_0] 测试 1 - 验证 zjy_20.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_0] 测试 1 对于 zjy_20.jar 通过! :)
    性能指标 -> 耗时: 56.882s, 平均加权完成时间(WT): 5.2656, 系统耗电量(W): 202.6
[TestWorker_0] 测试 1 - 运行 JAR: jyx.jar ...
[TestWorker_0] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\jyx.jar" < "test_inputs_hw6_update\\test_1_jyx_input.txt" > "test_inputs_hw6_update\\test_1_jyx_output.txt" (Timeout: 200s)
[TestWorker_0] === 程序 jyx.jar 正常结束 (耗时 0.49s) ===
[TestWorker_0] 测试 1 - 验证 jyx.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_0] 测试 1 - 运行 JAR: zcy.jar ...
[TestWorker_0] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zcy.jar" < "test_inputs_hw6_update\\test_1_zcy_input.txt" > "test_inputs_hw6_update\\test_1_zcy_output.txt" (Timeout: 200s)
[TestWorker_0] 测试 1 - 程序 jyx.jar 输出结果不正确!
    错误 1: 验证错误: 程序未产生任何有效输出，但输入包含请求。
错误用例已保存到: error_cases_hw6_update\\error_1_jyx_20250412_025036_623550.txt
[TestWorker_2] === 程序 zjy_20.jar 正常结束 (耗时 57.44s) ===
[TestWorker_2] 测试 3 - 验证 zjy_20.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_2] 测试 3 对于 zjy_20.jar 通过! :)
    性能指标 -> 耗时: 57.439s, 平均加权完成时间(WT): 5.6887, 系统耗电量(W): 200.8
[TestWorker_2] 测试 3 - 运行 JAR: jyx.jar ...
[TestWorker_2] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\jyx.jar" < "test_inputs_hw6_update\\test_3_jyx_input.txt" > "test_inputs_hw6_update\\test_3_jyx_output.txt" (Timeout: 200s)
[TestWorker_2] === 程序 jyx.jar 正常结束 (耗时 0.34s) ===
[TestWorker_2] 测试 3 - 验证 jyx.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_2] 测试 3 - 运行 JAR: zcy.jar ...
[TestWorker_2] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zcy.jar" < "test_inputs_hw6_update\\test_3_zcy_input.txt" > "test_inputs_hw6_update\\test_3_zcy_output.txt" (Timeout: 200s)
[TestWorker_2] 测试 3 - 程序 jyx.jar 输出结果不正确!
    错误 1: 验证错误: 程序未产生任何有效输出，但输入包含请求。
错误用例已保存到: error_cases_hw6_update\\error_3_jyx_20250412_025044_047320.txt
[TestWorker_4] === 程序 zcy.jar 正常结束 (耗时 51.99s) ===
[TestWorker_4] 测试 5 - 验证 zcy.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_4] 测试 5 对于 zcy.jar 通过! :)
    性能指标 -> 耗时: 51.992s, 平均加权完成时间(WT): 3.6177, 系统耗电量(W): 205.0
[TestWorker_4] ===> 完成测试 5 <===

[TestWorker_4] ===> 开始测试 7 (PRI:100, SCHE_CMD:20, UPDATE:3) <===
--- 测试 5/200 处理完成 (1/200) ---
执行数据生成脚本: C:\\Users\\keshi\\.version-fox\\cache\\python\\current\\python.exe D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\data_generator.py 100 20 3
[TestWorker_4] 测试 7 - 运行 JAR: zjy.jar ...
[TestWorker_4] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy.jar" < "test_inputs_hw6_update\\test_7_zjy_input.txt" > "test_inputs_hw6_update\\test_7_zjy_output.txt" (Timeout: 200s)
[TestWorker_5] === 程序 zcy.jar 正常结束 (耗时 52.18s) ===
[TestWorker_5] 测试 6 - 验证 zcy.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_5] 测试 6 对于 zcy.jar 通过! :)
    性能指标 -> 耗时: 52.176s, 平均加权完成时间(WT): 3.6687, 系统耗电量(W): 203.0
[TestWorker_5] ===> 完成测试 6 <===

[TestWorker_5] ===> 开始测试 8 (PRI:100, SCHE_CMD:20, UPDATE:3) <===
执行数据生成脚本: C:\\Users\\keshi\\.version-fox\\cache\\python\\current\\python.exe D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\data_generator.py 100 20 3
--- 测试 6/200 处理完成 (2/200) ---
[TestWorker_5] 测试 8 - 运行 JAR: zjy.jar ...
[TestWorker_5] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy.jar" < "test_inputs_hw6_update\\test_8_zjy_input.txt" > "test_inputs_hw6_update\\test_8_zjy_output.txt" (Timeout: 200s)
[TestWorker_3] === 程序 zcy.jar 正常结束 (耗时 54.65s) ===
[TestWorker_3] 测试 4 - 验证 zcy.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_3] 测试 4 对于 zcy.jar 通过! :)
    性能指标 -> 耗时: 54.652s, 平均加权完成时间(WT): 3.6059, 系统耗电量(W): 193.2
[TestWorker_3] ===> 完成测试 4 <===

[TestWorker_3] ===> 开始测试 9 (PRI:100, SCHE_CMD:20, UPDATE:3) <===
--- 测试 4/200 处理完成 (3/200) ---
执行数据生成脚本: C:\\Users\\keshi\\.version-fox\\cache\\python\\current\\python.exe D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\data_generator.py 100 20 3
[TestWorker_3] 测试 9 - 运行 JAR: zjy.jar ...
[TestWorker_3] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy.jar" < "test_inputs_hw6_update\\test_9_zjy_input.txt" > "test_inputs_hw6_update\\test_9_zjy_output.txt" (Timeout: 200s)
[TestWorker_1] === 程序 zcy.jar 正常结束 (耗时 55.32s) ===
[TestWorker_1] 测试 2 - 验证 zcy.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_1] 测试 2 对于 zcy.jar 通过! :)
    性能指标 -> 耗时: 55.322s, 平均加权完成时间(WT): 3.4817, 系统耗电量(W): 240.0
[TestWorker_1] ===> 完成测试 2 <===

[TestWorker_1] ===> 开始测试 10 (PRI:100, SCHE_CMD:20, UPDATE:3) <===
执行数据生成脚本: C:\\Users\\keshi\\.version-fox\\cache\\python\\current\\python.exe D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\data_generator.py 100 20 3
--- 测试 2/200 处理完成 (4/200) ---
[TestWorker_1] 测试 10 - 运行 JAR: zjy.jar ...
[TestWorker_1] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy.jar" < "test_inputs_hw6_update\\test_10_zjy_input.txt" > "test_inputs_hw6_update\\test_10_zjy_output.txt" (Timeout: 200s)
[TestWorker_0] === 程序 zcy.jar 正常结束 (耗时 56.60s) ===
[TestWorker_0] 测试 1 - 验证 zcy.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_0] 测试 1 对于 zcy.jar 通过! :)
    性能指标 -> 耗时: 56.603s, 平均加权完成时间(WT): 4.8803, 系统耗电量(W): 197.0
[TestWorker_0] ===> 完成测试 1 <===

[TestWorker_0] ===> 开始测试 11 (PRI:100, SCHE_CMD:20, UPDATE:3) <===
执行数据生成脚本: C:\\Users\\keshi\\.version-fox\\cache\\python\\current\\python.exe D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\data_generator.py 100 20 3
--- 测试 1/200 处理完成 (5/200) ---
[TestWorker_0] 测试 11 - 运行 JAR: zjy.jar ...
[TestWorker_0] 执行命令: java -jar "D:\\Desktop\\python\\评测机\\第二单元\\第二次迭代\\zjy.jar" < "test_inputs_hw6_update\\test_11_zjy_input.txt" > "test_inputs_hw6_update\\test_11_zjy_output.txt" (Timeout: 200s)
[TestWorker_2] === 程序 zcy.jar 正常结束 (耗时 58.75s) ===
[TestWorker_2] 测试 3 - 验证 zcy.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_2] 测试 3 对于 zcy.jar 通过! :)
    性能指标 -> 耗时: 58.749s, 平均加权完成时间(WT): 5.0174, 系统耗电量(W): 191.0
[TestWorker_2] ===> 完成测试 3 <===

# ... (rest of the log data omitted for brevity) ...

[TestWorker_5] === 程序 zcy.jar 正常结束 (耗时 56.34s) ===
[TestWorker_5] 测试 199 - 验证 zcy.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_5] 测试 199 对于 zcy.jar 通过! :)
    性能指标 -> 耗时: 56.341s, 平均加权完成时间(WT): 6.2095, 系统耗电量(W): 174.8
[TestWorker_5] ===> 完成测试 199 <===
[TestWorker_2] === 程序 zcy.jar 正常结束 (耗时 54.77s) ===
[TestWorker_2] 测试 200 - 验证 zcy.jar 的输出 (HW6+UPDATE规则)...
[TestWorker_2] 测试 200 对于 zcy.jar 通过! :)
    性能指标 -> 耗时: 54.769s, 平均加权完成时间(WT): 4.1822, 系统耗电量(W): 256.4
[TestWorker_2] ===> 完成测试 200 <===

进程已结束，退出代码为 1
"""

# Regex patterns
pass_pattern = re.compile(r"测试 \d+ 对于 (.*?) 通过! :\)")
metric_pattern = re.compile(r"性能指标 -> 耗时: (.*?)s, 平均加权完成时间\(WT\): (.*?), 系统耗电量\(W\): (.*?)$")

results = {}
lines = log_data.strip().split('\n')

current_jar = None
for i, line in enumerate(lines):
    pass_match = pass_pattern.search(line)
    if pass_match:
        current_jar = pass_match.group(1).strip()
        # Look at the next line for metrics
        if i + 1 < len(lines):
            metric_match = metric_pattern.search(lines[i + 1])
            if metric_match:
                try:
                    time_val = float(metric_match.group(1))
                    wt_val = float(metric_match.group(2))
                    w_val = float(metric_match.group(3))

                    if current_jar not in results:
                        results[current_jar] = {'time': [], 'wt': [], 'w': []}

                    results[current_jar]['time'].append(time_val)
                    results[current_jar]['wt'].append(wt_val)
                    results[current_jar]['w'].append(w_val)
                    current_jar = None  # Reset after successful metric capture
                except ValueError:
                    print(
                        f"Warning: Could not convert metrics to float for {current_jar} following line: {lines[i + 1]}")
                    current_jar = None  # Reset even on error
            else:
                current_jar = None  # Reset if next line isn't metrics
        else:
            current_jar = None  # Reset if it's the last line

# Calculate averages
averages = []
jars_to_process = ['zjy.jar', 'zjy_100.jar', 'zjy_50.jar', 'zjy_30.jar', 'zjy_20.jar', 'zcy.jar']
# Explicitly excluding jyx.jar as it had no successful runs in the log

for jar in jars_to_process:
    if jar in results and len(results[jar]['time']) > 0:
        count = len(results[jar]['time'])
        avg_time = sum(results[jar]['time']) / count
        avg_wt = sum(results[jar]['wt']) / count
        avg_w = sum(results[jar]['w']) / count
        averages.append({
            'jar': jar,
            'avg_time': avg_time,
            'avg_wt': avg_wt,
            'avg_w': avg_w,
            'count': count
        })
    else:
        averages.append({
            'jar': jar,
            'avg_time': float('inf'),  # Use infinity for sorting non-passing jars last
            'avg_wt': float('inf'),
            'avg_w': float('inf'),
            'count': 0
        })

# Create DataFrame for easier sorting and plotting
df_avg = pd.DataFrame(averages)

# **2. Calculate Averages and Rank**

# Sort for ranking (lower is better for all metrics)
df_avg_sorted_time = df_avg.sort_values(by='avg_time').reset_index(drop=True)
df_avg_sorted_wt = df_avg.sort_values(by='avg_wt').reset_index(drop=True)
df_avg_sorted_w = df_avg.sort_values(by='avg_w').reset_index(drop=True)

print("=== Performance Averages (Lower is Better) ===")
print(df_avg.to_string(index=False, float_format="%.4f"))
print("\n=== Rankings ===")
print("\n--- By Average Time (耗时) ---")
print(df_avg_sorted_time[['jar', 'avg_time', 'count']].to_string(index=False, float_format="%.4f"))
print("\n--- By Average Weighted Completion Time (WT) ---")
print(df_avg_sorted_wt[['jar', 'avg_wt', 'count']].to_string(index=False, float_format="%.4f"))
print("\n--- By Average Power Consumption (W) ---")
print(df_avg_sorted_w[['jar', 'avg_w', 'count']].to_string(index=False, float_format="%.4f"))

# **3. Plotting**

plt.rcParams['font.sans-serif'] = ['SimHei']  # Use SimHei font for Chinese characters
plt.rcParams['axes.unicode_minus'] = False  # Fix for negative signs not showing


# Plotting function
def plot_metric(df_sorted, metric_col, title):
    plt.figure(figsize=(10, 6))
    bars = plt.bar(df_sorted['jar'], df_sorted[metric_col])
    plt.ylabel('Average Value')
    plt.title(title)
    plt.xticks(rotation=45, ha='right')
    # Add value labels on top of bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2.0, yval, f'{yval:.2f}', va='bottom', ha='center')
    plt.tight_layout()
    plt.show()


# Generate plots
plot_metric(df_avg_sorted_time, 'avg_time', 'Average Execution Time (耗时) - Lower is Better')
plot_metric(df_avg_sorted_wt, 'avg_wt', 'Average Weighted Completion Time (WT) - Lower is Better')
plot_metric(df_avg_sorted_w, 'avg_w', 'Average Power Consumption (W) - Lower is Better')