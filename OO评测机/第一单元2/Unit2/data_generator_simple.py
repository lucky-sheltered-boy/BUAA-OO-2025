import random

ans = ''
minTermNum = 1
maxTermNum = 2
minFactorNum = 1
maxFactorNum = 1
maxSubExprNum = 1
subExprNum = 0
maxBigInteger = 0
BigInteger = 0
maxSinNum = 2
sinNum = 0
fpattern = random.randint(0,3)
gpattern = random.randint(0,3)
hpattern = random.randint(0,3)

def createSelfFunc():
    global ans
    global gpattern
    global hpattern
    ans += '2' + '\n'
    ans += 'g'
    if gpattern == 0:
        ans += '(x)'
    elif gpattern == 1:
        ans += '(y)'
    elif gpattern == 2:
        ans += '(x,y)'
    else :
        ans += '(y,x)'
    ans += '='
    createSelfFuncTerms(gpattern)
    numOfTerms = random.randint(0,1)
    for i in range(numOfTerms):
        ans += '*'
        createSelfFuncTerms(gpattern)
    ans += '\n'
    ans += 'h'
    if hpattern == 0:
        ans += '(x)'
    elif hpattern == 1:
        ans += '(y)'
    elif hpattern == 2:
        ans += '(x,y)'
    else:
        ans += '(y,x)'
    ans += '='
    createFuncTerm(hpattern,0)
    numOfTerms = random.randint(0, 1)
    for i in range(numOfTerms):
        ans += '*'
        createFuncTerm(hpattern,0)
    ans += '\n'


def createFunc():
    global ans
    global fpattern
    ans += '1' + '\n'
    op = random.randint(0,2)
    if op == 0:
        createFunc0(fpattern)
        createFunc1(fpattern)
        createFuncn(fpattern)
    elif op == 1:
        createFunc1(fpattern)
        createFuncn(fpattern)
        createFunc0(fpattern)
    else:
        createFuncn(fpattern)
        createFunc0(fpattern)
        createFunc1(fpattern)

def createFunc0(pattern):
    global ans
    ans += 'f{0}'
    if pattern == 0:
        ans += '(x)'
    elif pattern == 1:
        ans += '(y)'
    elif pattern == 2:
        ans += '(x,y)'
    else :
        ans += '(y,x)'
    ans += ' = '
    numOfTerm = random.randint(1,2)
    for i in range(numOfTerm):
        addSign()
        createFuncTerm(pattern,1)
    ans += '\n'


def createFunc1(pattern):
    global ans
    ans += 'f{1}'
    if pattern == 0:
        ans += '(x)'
    elif pattern == 1:
        ans += '(y)'
    elif pattern == 2:
        ans += '(x,y)'
    else:
        ans += '(y,x)'
    ans += ' = '
    numOfTerm = random.randint(1, 2)
    for i in range(numOfTerm):
        addSign()
        createFuncTerm(pattern,1)
    ans += '\n'

def createFuncn(pattern):
    global ans
    ans += 'f{n}'
    if pattern == 0:
        ans += '(x)'
    elif pattern == 1:
        ans += '(y)'
    elif pattern == 2:
        ans += '(x,y)'
    else:
        ans += '(y,x)'
    ans += ' = '
    addSign()
    ans += str(random.randint(0,9))
    ans += '*'
    if pattern <= 1:
        ans += 'f{n-1}'
        ans += '('
        createFuncFactor(pattern,1)
        ans += ')'
        addSign()
        ans += str(random.randint(0, 9))
        ans += '*'
        ans += 'f{n-2}'
        ans += '('
        createFuncFactor(pattern,1)
        ans += ')'
        ans += '+'
        createFuncFactor(pattern,1)
    else :
        ans += 'f{n-1}'
        ans += '('
        createFuncFactor(pattern,1)
        ans += ','
        createFuncFactor(pattern,1)
        ans += ')'
        addSign()
        ans += str(random.randint(0, 9))
        ans += '*'
        ans += 'f{n-2}'
        ans += '('
        createFuncFactor(pattern,1)
        ans += ','
        createFuncFactor(pattern,1)
        ans += ')'
        ans += '+'
        createFuncFactor(pattern,1)
    ans += '\n'

def createExpr():
    global ans
    numOfTerms = random.randint(minTermNum, maxTermNum)
    for i in range(numOfTerms):
        addSign()
        addSpace()
        createTerm()
        addSpace()

def createTerm():
    global ans
    numOfFactors = random.randint(minFactorNum, maxFactorNum)
    if getRand():
        ans += '+'
    else:
        ans += '-'
    addSpace()
    createFactor()
    addSpace()
    for i in range(numOfFactors):
        ans += '*'
        addSpace()
        createFactor()
        addSpace()

def createFactor():
    global ans
    global subExprNum
    global maxSubExprNum
    global sinNum
    global maxSinNum
    if subExprNum < maxSubExprNum:
        op = random.randint(91,100)
        if 91 <= op <= 100:
            subExprNum += 1
    else:
        if sinNum < maxSinNum:
            op = random.randint(1, 90)
            if op >= 66:
                sinNum += 1
        else:
            op = random.randint(1,65)
    if 1 <= op <= 20:
        addNum()
    elif 21 <= op <= 40:
        if getRand():
            ans += 'x'
        else:
            ans += 'x'
            addSpace()
            ans += '^'
            addSpace()
            if getRand():
                ans += '+'
            numbit = random.randint(0,1)
            for i in range(numbit):
                ans += str(0)
            ans += str(random.randint(0, 8))
    elif 41 <= op <= 65:
        createFunction(0,2)
    elif 66 <= op <=90:
        if getRand():
            addSin()
        else:
            addCos()
    elif 91 <= op <= 100:
        ans += '('
        createExpr()
        ans += ')'
        addSpace()
        ans += '^'
        addSpace()
        if getRand():
            ans += '+'
        numbit = random.randint(0, 1)
        for i in range(numbit):
            ans += str(0)
        ans += str(random.randint(0, 4))

def getRand():
    return random.randint(0, 1)

def addSign():
    global ans
    if getRand():
        sign = '+'
    else:
        sign = '-'
    ans += sign

def addSpace():
    global ans
    numOfSpace = random.randint(0, 1)
    for i in range(numOfSpace):
        if getRand():
            sign = ' '
        else:
            sign = '\t'
        ans += sign

def addNum():
    global ans
    global BigInteger
    global maxBigInteger
    addSign()
    if BigInteger < maxBigInteger and getRand():
        numbit = 21
        BigInteger += 1
    else:
        numbit = random.randint(1,2)
    for i in range(numbit):
        ans += str(random.randint(0,9))

def addSin():
    global ans
    ans += 'sin('
    createFactor()
    ans += ')'
    if getRand():
        ans += '^'
        if getRand():
            ans += '+'
        numbit = random.randint(0, 1)
        for i in range(numbit):
            ans += str(0)
        ans += str(random.randint(0, 8))

def addSin2(pattern,op):
    global ans
    ans += 'sin('
    createFuncFactor(pattern,op)
    ans += ')'
    if getRand():
        ans += '^'
        if getRand():
            ans += '+'
        numbit = random.randint(0, 1)
        for i in range(numbit):
            ans += str(0)
        ans += str(random.randint(0, 8))

def addSin3(pattern):
    global ans
    ans += 'sin('
    createSelfFuncFactor(pattern)
    ans += ')'
    if getRand():
        ans += '^'
        if getRand():
            ans += '+'
        numbit = random.randint(0, 1)
        for i in range(numbit):
            ans += str(0)
        ans += str(random.randint(0, 8))

def addCos():
    global ans
    ans += 'cos('
    createFactor()
    ans += ')'
    if getRand():
        ans += '^'
        if getRand():
            ans += '+'
        numbit = random.randint(0, 1)
        for i in range(numbit):
            ans += str(0)
        ans += str(random.randint(0, 8))

def addCos2(pattern,op):
    global ans
    ans += 'cos('
    createFuncFactor(pattern,op)
    ans += ')'
    if getRand():
        ans += '^'
        if getRand():
            ans += '+'
        numbit = random.randint(0, 1)
        for i in range(numbit):
            ans += str(0)
        ans += str(random.randint(0, 8))

def addCos3(pattern):
    global ans
    ans += 'cos('
    createSelfFuncFactor(pattern)
    ans += ')'
    if getRand():
        ans += '^'
        if getRand():
            ans += '+'
        numbit = random.randint(0, 1)
        for i in range(numbit):
            ans += str(0)
        ans += str(random.randint(0, 8))

def createFunction(pattern,op1):
    global ans
    op = random.randint(0,op1)
    if op == 2:
        num = random.randint(0,5)
        ans += 'f{'
        ans += str(num)
        ans += '}'
        ans += '('
        if fpattern <= 1:
            createFuncFactor(pattern,op1)
        else:
            createFuncFactor(pattern,op1)
            addSpace()
            ans += ','
            addSpace()
            createFuncFactor(pattern,op1)
        ans += ')'
    elif op == 1:
        ans += 'h'
        ans += '('
        if hpattern <= 1:
            createFuncFactor(pattern,op1)
        else:
            createFuncFactor(pattern,op1)
            addSpace()
            ans += ','
            addSpace()
            createFuncFactor(pattern,op1)
        ans += ')'
    else:
        ans += 'g'
        ans += '('
        if gpattern <= 1:
            createFuncFactor(pattern,op1)
        else:
            createFuncFactor(pattern,op1)
            addSpace()
            ans += ','
            addSpace()
            createFuncFactor(pattern,op1)
        ans += ')'

def createFuncTerm(pattern,op):
    global ans
    addSign()
    numOfFactor = random.randint(0, 1)
    createFuncFactor(pattern,op)
    for j in range(numOfFactor):
        ans += ' * '
        createFuncFactor(pattern,op)

def createFuncFactor(pattern,op1):
    global ans
    op = random.randint(1, 90)
    if pattern == 0:
        signal = 'x'
    elif pattern == 1:
        signal = 'y'
    else :
        if getRand():
            signal = 'x'
        else :
            signal = 'y'
    if 1 <= op <= 20:
        addNum()
    elif 21 <= op <= 40:
        if getRand():
            ans += signal
        else:
            ans += signal
            addSpace()
            ans += '^'
            addSpace()
            if getRand():
                ans += '+'
            numbit = random.randint(0, 1)
            for i in range(numbit):
                ans += str(0)
            ans += str(random.randint(0, 8))
    elif 41 <= op <= 65:
        if getRand():
            addSin2(pattern,op1)
        else:
            addCos2(pattern,op1)
    elif 66 <= op <= 90:
        createFunction(pattern,op1)

def createSelfFuncTerms(pattern):
    global ans
    addSign()
    numOfFactor = random.randint(0, 1)
    createSelfFuncFactor(pattern)
    for j in range(numOfFactor):
        ans += ' * '
        createSelfFuncFactor(pattern)

def createSelfFuncFactor(pattern):
    global ans
    op = random.randint(1, 65)
    signal = ''
    if pattern == 0:
        signal = 'x'
    elif pattern == 1:
        signal = 'y'
    else:
        if getRand():
            signal = 'x'
        else:
            signal = 'y'
    if 1 <= op <= 20:
        addNum()
    elif 21 <= op <= 40:
        if getRand():
            ans += signal
        else:
            ans += signal
            addSpace()
            ans += '^'
            addSpace()
            if getRand():
                ans += '+'
            numbit = random.randint(0, 1)
            for i in range(numbit):
                ans += str(0)
            ans += str(random.randint(0, 8))
    elif 41 <= op <= 65:
        if getRand():
            addSin3(pattern)
        else:
            addCos3(pattern)

createSelfFunc()
createFunc()
createExpr()
print(ans, end = '')