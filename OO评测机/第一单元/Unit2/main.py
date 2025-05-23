import os
import difflib
import sympy as sp
from sympy import symbols, Eq, simplify
import sys
import multiprocessing
import time

testFileNum = 2
dataRounds = 50
bugFiles = []
bugNums = []
test_mode = 'simple'
stdFile = 'oo_homework_2025_23371524_hw_2.jar'
filenames = ['天枢.jar',
             'oo_homework_2025_23371543_hw_2.jar',
             '天权星.jar',
             '洞明星.jar',
             '天璇星.jar',
             '天玑星.jar',
             '开阳星.jar',
             '摇光星.jar',
             '天枢星.jar',
             'hw_23373276(1).jar',
             'HW2.jar',
             'hw2_lmh.jar',
             'hw2(2).jar',
             'hw2_WZH_2.jar',
             'src(1).jar',
             'hw_2_2.jar',
             'oo_homework_2025_23371537_hw_1.jar',
             'oo_homework_2025_23371343_hw_2.jar',
             'oo_homework_2025_23373434_hw_2.jar',
             'oo_homework_2025_23371359_hw_2.jar',
             'oo_homework_2025_23371138_hw_2.jar',
             'oo_homework_2025_23371301_hw_2.jar',
             'oo_homework_2025_23371414_hw_2.jar',
             'oo_homework_2025_23371281_hw_2.jar',
             'oo_homework_2025_23371405_hw_2.jar',
             'htl.jar',
             'oo_homework_2025_23371057_hw_2.jar',
             'oo_homework_2025_23371214_hw_2.jar',
             'hw_2.jar',
             'kxq_U2_hw2.jar',
             'oo_homework_2025_23371543_hw_2.jar']

def isEqual(expr1,expr2,len1,len2,gap,num):
    if sp.simplify(expr1 - expr2) == 0:
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
    preProcessing()
    print(f'start the {test_mode} test ------------------',end = '\n\n')

    for j in range(testFileNum):
        current_bug = 0
        gap = [0]
        print(f'starting check file {filenames[j]}',end = '\n\n')

        for i in range(dataRounds):
            print(f'enter test{i+1} ')

            data = f'python data_generator_{test_mode}.py > in.txt'
            os.system(data)
            print(f'in.txt net characters: {getFileCharNum('in.txt')}')

            std = 'java -jar ' + stdFile + ' < in.txt > out0.txt'
            os.system(std)

            outName = f'out{j+1}.txt'
            test = 'java -jar ' + filenames[j] + ' < in.txt > ' + outName
            os.system(test)

            with open('out0.txt','r') as f1:
                expr1 = f1.read()
                len1 = len(expr1)
                expr1 = expr1.replace('^','**')
            with open(outName,'r') as f2:
                expr2 = f2.read()
                len2 = len(expr2)
                expr2 = expr2.replace('^', '**')

            print('begin checking -----')
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

            x = symbols('x')

            print(f'expr1 characters: {len1} ', end='')
            # expr1 = sp.simplify(expr1)
            # print('simplified!')
            try:
                expr1 = simplify_with_timeout(expr1, timeout=5)
                print('simplified!')
            except TimeoutError as e:
                print(e)
                print("Continuing with the rest of the program...")
                continue

            print(f'expr2 characters: {len2} ', end='')
            # expr2 = sp.simplify(expr2)
            # print('simplified!')
            try:
                expr2 = simplify_with_timeout(expr2, timeout=5)
                print('simplified!')
            except TimeoutError as e:
                print(e)
                print("Continuing with the rest of the program...")
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
                print(f'Congratulation! {filenames[j]} is AC!!!',end = '\n\n')
            else:
                print(f'{filenames[j]} fail to pass the test, {current_bug} bugs emerged',end = '\n\n',file = sys.stderr)
                bugFiles.append(filenames[j])
                bugNums.append(current_bug)

    else:
        if total_bug == 0:
            print('all files are AC!!!!!!!!!!!!!!!!!!!!!!')
        else:
            print('several files contain bugs:')
            for i in range(len(bugNums)):
                print(f'{bugFiles[i]} contains {bugNums[i]} bugs ',file = sys.stderr)

if __name__ == '__main__':
    main()