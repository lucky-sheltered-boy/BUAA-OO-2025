import os
import difflib
import sympy as sp
from sympy import symbols, Eq, simplify
import sys

testFileNum = 2
dataRounds = 50
bugFiles = []
bugNums = []
test_mode = 'simple'
stdFile = 'oo_homework_2025_23371524_hw_1.jar'
filenames = ['oo_homework_2025_23371543_hw_1.jar',
             'oo_homework_2025_23371540_hw_1.jar']

def isEqual(expr1,expr2,len1,len2,gap,num):
    if sp.simplify(expr1 - expr2) == 0:
        if abs(len1 - len2) >= 2:
            gap += 1
            os.system(f'cp in.txt 0_{num}_chargap{gap}.txt')
            print(f'this test has large char gap')
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

def main():
    total_bug = 0
    preProcessing()
    print(f'start the {test_mode} test ------------------',end = '\n\n')

    for j in range(testFileNum):
        current_bug = 0
        gap = 0
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
            expr1 = sp.simplify(expr1)
            print('simplified!')
            print(f'expr2 characters: {len2} ', end='')
            expr2 = sp.simplify(expr2)
            print('simplified!')

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