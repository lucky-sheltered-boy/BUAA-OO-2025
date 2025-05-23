import os
import difflib
import sympy as sp
from sympy import symbols, Eq, simplify
import sys
import multiprocessing
import time
import shlex
import subprocess

singleTest = 0
testFileNum = 1
dataRounds = 200
bugFiles = []
bugNums = []
test_mode = 'simple'
stdFile = 'oo_homework_2025_23371524_hw_3.jar'
filenames = ['hw3_others.jar',
             '天璇星.jar',
             '开阳星.jar',
             '摇光星.jar',
             '天璇星.jar',
             'hw_2_2.jar',
             '摇光星.jar',
             '5.jar.',
             '天枢星.jar',
             '摇光星.jar',
             '天璇星.jar',
             '天权星.jar',
             'oo_homework_2025_23371543_hw_3.jar',
             'hw_2_2.jar',
             'oo_homework_2025_22375354_hw_3.jar',
             'hw_2_2.jar',
             'oo_homework_2025_23371414_hw_3.jar',
             'oo_homework_2025_22375354_hw_3.jar',
             'oo_homework_2025_23373375_hw_1.jar',
             'oo_homework_2025_22375354_hw_3.jar',
             'oo_homework_2025_23371414_hw_3.jar',
             'HW3.jar',
             'oo_homework_2025_22375354_hw_3.jar',
             'HW3.jar',
             'oo_homework_2025_22375354_hw_3.jar',
             'oo_homework_2025_23371210_hw_3.jar',
             'oo_homework_2025_22375354_hw_3.jar',
             'HW3.jar',
             'oo_homework_2025_23373375_hw_1.jar',
             'oo_homework_2025_23371414_hw_3.jar',
             'oo_homework_2025_23371405_hw_3.jar',
             'HW3_ZHOU_NestDiff.jar',
             'std.jar',
             'Unit1.jar',
             'oo_homework_2025_23371359_hw_3.jar',
             'hw_2_2.jar',
             'oo_homework_2025_23371543_hw_3.jar',
             'lty2.jar',]

def isEqual(expr1,expr2,len1,len2,gap,num):
    if sp.simplify(expr1) == 0 and sp.simplify(expr2) == 0:
        if abs(len1 - len2) >= 2:
            gap[0] += 1
            os.system(f'cp in.txt 0_{num}_chargap{gap[0]}_{len2-len1}.txt')
            print(f'this test has large char gap {gap[0]} {len2-len1}')
        return True
    else:
        return False

def clear(string):
    string = string.replace(' ','')
    string = string.replace('\t','')
    return string

def getFileCharNum(filename):
    with open(filename, 'r') as f:
        info = f.read()
    info = clear(info)
    return len(info)

def preProcessing():
    os.system('rm -f *.txt')
    os.system('rm -f *.html')
    os.system('rm -f bugfile*')

def worker(result_queue, expr_str):
    try:
        expr = sp.sympify(expr_str)  # 将字符串转换回表达式
        simplified_expr = sp.simplify(expr)
        result_queue.put(simplified_expr)
    except Exception as e:
        result_queue.put(e)

def simplify_with_timeout(expr, timeout=3):
    result_queue = multiprocessing.Queue()
    expr_str = str(expr)  # 将表达式转换为字符串以便序列化
    process = multiprocessing.Process(target=worker, args=(result_queue, expr_str))
    process.start()
    process.join(timeout=timeout)

    if process.is_alive():
        process.terminate()
        process.join()
        raise TimeoutError(f"Simplification exceeded {timeout} seconds")

    result = result_queue.get()
    if isinstance(result, Exception):
        raise result
    return result


def main():
    total_bug = 0
    if singleTest == 0:
        preProcessing()
    print(f'start the {test_mode} test ------------------',end = '\n\n')

    for j in range(testFileNum):
        current_bug = 0
        gap = [0]
        invalid = 0
        print(f'starting check file {filenames[j]}',end = '\n\n')

        for i in range(dataRounds):
            print(f'enter test{i+1} ')
            if singleTest == 0:
                data = f'python data_generator_{test_mode}.py > in.txt'
                os.system(data)
            print(f'in.txt net characters: {getFileCharNum('in.txt')}')

            std = 'java -jar ' + stdFile + ' < in.txt > out0.txt'
            #os.system(std)
            try:
                with open('in.txt', 'r') as infile, open('out0.txt', 'w') as outfile:
                    process = subprocess.run(
                        ['java', '-jar', stdFile],
                        stdin=infile,
                        stdout=outfile,
                        stderr=subprocess.PIPE,  # 捕获标准错误
                        timeout=5,  # 设置超时时间
                        text=True  # 以文本模式捕获输出
                    )
                    if process.returncode != 0:
                        print(f"Java程序运行出错，返回码: {process.returncode}")
                        print("错误信息:")
                        print(process.stderr,file = sys.stderr)  # 打印标准错误
                        total_bug += 1
                        current_bug += 1
                        os.system(f'cp in.txt 0_bugfile{current_bug}.txt')
            except subprocess.TimeoutExpired:
                print("Java0程序运行超时，已终止",end = '\n\n\n')
                invalid += 1
                continue

            outName = f'out{j+1}.txt'
            test = 'java -jar ' + filenames[j] + ' < in.txt > ' + outName
            #os.system(test)
            try:
                with open('in.txt', 'r') as infile, open(outName, 'w') as outfile:
                    process = subprocess.run(
                        ['java', '-jar', filenames[j]],
                        stdin=infile,
                        stdout=outfile,
                        stderr=subprocess.PIPE,  # 捕获标准错误
                        timeout=5,  # 设置超时时间
                        text=True  # 以文本模式捕获输出
                    )
                    if process.returncode != 0:
                        print(f"Java程序运行出错，返回码: {process.returncode}")
                        print("错误信息:")
                        print(process.stderr,file = sys.stderr)  # 打印标准错误
                        total_bug += 1
                        current_bug += 1
                        os.system(f'cp in.txt {j + 1}_bugfile{current_bug}.txt')
            except subprocess.TimeoutExpired:
                print(f"Java{j+1}程序运行超时，已终止",end = '\n\n\n')
                invalid += 1
                continue

            with open('out0.txt','r') as f1:
                expr1 = f1.read()
                len1 = len(expr1)
                expr1 = expr1.replace('^','**')
            with open(outName,'r') as f2:
                expr2 = f2.read()
                len2 = len(expr2)
                expr2 = expr2.replace('^', '**')

            print('begin checking -----')
            if len1 >= 100 and len2 >= 100 and abs(len1 - len2) <= 1:
                print(f'file {j + 1} data{i + 1} AC!!! total bug = {total_bug}, current bug = {current_bug}',end='\n\n\n')
                print(f'expr1 characters: {len1} ', end='\n')
                print(f'expr2 characters: {len2} ', end='\n\n\n')
                continue
            flag = 1
            if expr1 == "" :
                print('error !! expr1 is null string',file = sys.stderr)
                total_bug += 1
                current_bug += 1
                os.system(f'cp in.txt 0_bugfile{current_bug}.txt')
                flag = 0
            if expr2 == "" :
                print('error !! expr2 is null string',file = sys.stderr)
                total_bug += 1
                current_bug += 1
                os.system(f'cp in.txt {j+1}_bugfile{current_bug}.txt')
                flag = 0

            if flag == 0:
                continue

            os.system('cp out0.txt subtract.txt')
            os.system('echo -( >> subtract.txt')
            os.system(f'cat {outName} >> subtract.txt')
            os.system('echo ) >> subtract.txt')
            with open('subtract.txt', 'r') as file:
                content = file.read()
                content = content.replace(" ", "").replace("\t", "").replace("\n", "")
            with open('subtract.txt', 'w') as file:
                contents = '0' + '\n' + '0' + '\n' + content
                file.write(contents)
            std = 'java -jar ' + stdFile + ' < subtract.txt > subtract0.txt'
            os.system(std)
            outName = f'subtract{j + 1}.txt'
            test = 'java -jar ' + filenames[j] + ' < subtract.txt > ' + outName
            os.system(test)

            x = symbols('x')

            print(f'expr1 characters: {len1} ',end = '')
            with open('subtract0.txt','r') as file:
                expr1 = file.read()
                expr1 = expr1.replace('^','**')
            try:
                expr1 = simplify_with_timeout(expr1, timeout=10)
                print('simplified!')
            except TimeoutError as e:
                print(e)
                print("Continuing with the rest of the program...",end = '\n\n\n')
                invalid += 1
                continue

            print(f'expr2 characters: {len2} ',end = '')
            with open(outName,'r') as file:
                expr2 = file.read()
                expr2 = expr2.replace('^','**')
            try:
                expr2 = simplify_with_timeout(expr2, timeout=10)
                print('simplified!')
            except TimeoutError as e:
                print(e)
                print("Continuing with the rest of the program...",end = '\n\n\n')
                invalid += 1
                continue

            if isEqual(expr1,expr2,len1,len2,gap,j+1):
                print(f'file {j+1} data{i+1} AC!!! total bug = {total_bug}, current bug = {current_bug}',end='\n\n\n')
            else:
                total_bug += 1
                current_bug += 1
                print(f'file {j+1} data{i+1} error total bug = {total_bug}, current bug = {current_bug}',end='\n\n\n',file = sys.stderr)
                os.system(f'cat in.txt > {j+1}_bugfile{current_bug}.txt')

        else:
            if current_bug == 0:
                print(f'Congratulation! {filenames[j]} is AC!!!')
            else:
                print(f'{filenames[j]} fail to pass the test, {current_bug} bugs emerged',file = sys.stderr)
                bugFiles.append(filenames[j])
                bugNums.append(current_bug)
            print(f'valid tests : {dataRounds - invalid}',end = '\n\n')

    else:
        if total_bug == 0:
            print('all files are AC!!!!!!!!!!!!!!!!!!!!!!')
        else:
            print('several files contain bugs:')
            for i in range(len(bugNums)):
                print(f'{bugFiles[i]} contains {bugNums[i]} bugs ',file = sys.stderr)

if __name__ == '__main__':
    main()