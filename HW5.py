# Garrett Stahl, 11540475
# Received help from Alex White

import re
def tokenize(s):
    return re.findall("/?[a-zA-Z][a-zA-Z0-9_]*|[\[][a-zA-Z-?0-9_\s\(\)!][a-zA-Z-?0-9_\s\(\)!]*[\]]|[\()][a-zA-Z-?0-9_\s!][a-zA-Z-?0-9_\s!]*[\)]|[-]?[0-9]+|[}{]+|%.*|[^ \t\n]", s)

# search the dictstack for the dictionary "name" is defined in and return the (list) index for that dictionary (start searhing at the top of the stack)
def staticLink(name):
    if not dictstack:
        return 0
    else: # return position number that the name was found
        #dictstack.reverse()
        for i in range(0, len(dictstack)):
            if dictstack[i][1].get('/' + name):
                #dictstack.reverse()
                return i
        #dictstack.reverse()
        return 0

# COMPLETE THIS FUNCTION
# The it argument is an iterator.
# The tokens between '{' and '}' is included as a sub code-array (dictionary). If the
# parentheses in the input iterator is not properly nested, returns False.
def groupMatch(it): # only the nested stuff
    res = []
    for c in it:
        if c == '}':
            return {'codearray':res}
        elif c == '{':
            # Note how we use a recursive call to group the tokens inside the
            # inner matching parenthesis.
            # Once the recursive call returns the code-array for the inner
            # parenthesis, it will be appended to the list we are constructing
            # as a whole.
            res.append(groupMatch(it))
        else:
            if c.isnumeric():
                res.append(int(c))
            elif '-' in c and c.lstrip('-').isnumeric():
                res.append(int(c.lstrip('-')) * -1)
            elif c.isnumeric():
                res.append(int(c))
            elif c[0] == '[':
                x = c[1:len(c) - 1]
                x.lstrip(',')
                x = x.split()
                res.append(groupMatch(x))
            elif c == 'true' or c == 'True':
                res.append(True)
            elif c == 'False' or c == 'false':
                res.append(False)
            else:
                res.append(c)
    if len(res) > 0:
        return res
    return False

parseBool = {'True':True, 'False':False, 'true':True, 'false':False}

# COMPLETE THIS FUNCTION
# Function to parse a list of tokens and arrange the tokens between { and } braces
# as code-arrays.
# Properly nested parentheses are arranged into a list of properly nested dictionaries.
def parse(L): # this and groupmatch make it so we can pass values onto the stack to be evaluated by evaluteArray()
    res = []
    it = iter(L)
    for c in it:
        if  c== '}':  #non matching closing parenthesis; return false since there is
                    # a syntax error in the Postscript code.
            return False
        elif c == '{':
            res.append(groupMatch(it))
        else:
            if c in parseBool:
                res.append(parseBool.get(c))
            elif c.isnumeric():
                res.append(int(c))
            elif c[0] == '[':
                x = c[1:len(c)-1]
                x.lstrip(',')
                x = x.split()
                res.append(groupMatch(x))
            elif c == ' ':
                continue
            elif '-' in c and c.lstrip('-').isnumeric():
                res.append(int(c.lstrip('-')))
            else:
                res.append(c)
    return {'codearray':res}

# COMPLETE THIS FUNCTION
# This will probably be the largest function of the whole project,
# but it will have a very regular and obvious structure if you've followed the plan of the assignment.
# Write additional auxiliary functions if you need them.
def interpretSPS(code, scope): # code is a code array
    for token in code['codearray']:
        if isinstance(token, int) or isinstance(token, bool) or isinstance(token, dict):
            opPush(token)
        elif isinstance(token, list):
            evaluateArray(token, scope)
        elif isinstance(token, str):
            if len(token) >= 2 and token[0] == '(' and token[-1] == ')':  # const string
                opPush(token)
            elif len(token) >= 1 and token[0] == '/':
                opPush(token)
            elif token in internalOps.keys():
                if token == "if" or token == "for" or token == "ifelse":
                    internalOps.get(token)[0](scope)
                else:
                    internalOps.get(token)[0]()
            else:
                searchItem = lookup(token, scope)
                if searchItem is not None:
                    if isinstance(searchItem, dict):
                        dictPush((staticLink(token), {}))
                        interpretSPS(searchItem, scope)
                        dictPop()
                    else:
                        opPush(searchItem)
                else:
                    print("Error: interpretSPS - " + token + " was not found in lookup.")
        else:
            print("Error: interpretSPS -" + token + " is invalid.")

def interpreter(s, scope): # s is a string
    interpretSPS(parse(tokenize(s)), scope)

#clear opstack and dictstack
def clearBoth():
    opstack[:] = []
    dictstack[:] = []

def psIf(scope):
    if len(opstack) < 2:
        print("Error: psIf- opstack does not have enough arguments.")
    else:
        operation = opPop()
        boolVal = opPop()
        if isinstance(boolVal, bool):
            if boolVal == True:
                interpretSPS(operation, scope)
        else:
            print("Error: psIf - popped value was not a bool.")
            replaceHelp([operation, boolVal])

def psIfelse(scope):
    if len(opstack) < 3:
        print("Error: psIfelse - opstack does not have enough arguments.")
    else:
        operation2 = opPop()
        operation1 = opPop()
        boolVal = opPop()
        if isinstance(boolVal, bool):
            if boolVal == True:
                interpretSPS(operation1, scope)
            else:
                interpretSPS(operation2, scope)
        else:
            print("Error: psIfelse - operator was not a boolean value.")
            replaceHelp([boolVal, operation1, operation2])

def psFor(scope):
    if len(opstack) < 4:
        print("Error: psFor - opstack does not have enough operands.")
    else:
        operation = opPop()
        endVar = opPop()
        incVar = opPop()
        startVar = opPop()
        if endVar > startVar:
            while startVar <= endVar:
                opPush(startVar)
                interpretSPS(operation, scope)
                startVar += incVar
        else:
            while startVar >= endVar:
                opPush(startVar)
                interpretSPS(operation, scope)
                startVar += incVar

#------------------------- 10% -------------------------------------
# The operand stack: define the operand stack and its operations
opstack = []  #assuming top of the stack is the end of the list

# Now define the HELPER FUNCTIONS to push and pop values on the opstack
# Remember that there is a Postscript operator called "pop" so we choose
# different names for these functions.
# Recall that `pass` in Python is a no-op: replace it with your code.

def opPop():
    if not opstack:
        print("Error: opPop() - opstack is empty.")
    else:
        returnVal = opstack[-1]
        opstack.pop(-1)
        return returnVal
    # opPop should return the popped value.
    # The pop() function should call opPop to pop the top value from the opstack, but it will ignore the popped value.

def opPush(value):
    opstack.append(value)

#-------------------------- 16% -------------------------------------
# The dictionary stack: define the dictionary stack and its operations
dictstack = []  #assuming top of the stack is the end of the list

# now define functions to push and pop dictionaries on the dictstack, to
# define name, and to lookup a name

def dictPop():
    if not dictstack:
        print("Error: dictPop() - dictstack is empty.")
    else:
        returnVal = dictstack[-1]
        dictstack.pop(-1)
        return returnVal
    # dictPop pops the top dictionary from the dictionary stack.

def dictPush(d):
    dictstack.append(d)
    #dictPush pushes the dictionary ‘d’ to the dictstack.
    #Note that, your interpreter will call dictPush only when Postscript
    #“begin” operator is called. “begin” should pop the empty dictionary from
    #the opstack and push it onto the dictstack by calling dictPush.

def define(name, value):
    if not dictstack:
        dictPush((0,{name:value}))
    else:
        if dictstack[len(dictstack) - 1][1].get(name, None) == None:
            dictstack[len(dictstack) - 1][1][name] = value
        elif dictstack[len(dictstack) - 1][1].get(name, None) is not None:
            dictstack[len(dictstack) - 1][1][name] = value
        else:
            dictPush((0,{name:value}))

#def define(name, value):
#    if dictstack[-1] == {}:
#        dictstack[-1] = {name: value}
#    else:
#        dictstack[-1][name] = value
    #add name:value pair to the top dictionary in the dictionary stack.
    #Keep the '/' in the name constant.
    #Your psDef function should pop the name and value from operand stack and
    #call the “define” function.

def lookup(token, scope):
    if not dictstack:
        print("Error: lookup - dictstack is empty.")
    else:
        if scope == "dynamic":
            i = len(dictstack) - 1
            while i >= 0:
                if dictstack[i][1].get("/" + token) is not None:
                    return dictstack[i][1].get("/" + token)
                i -= 1
            print("Error: lookup - /" + token + " was not found.")
            return None
        else:
            return lookupHelp("/" + token, len(dictstack) - 1)

def lookupHelp(token, i):
    if dictstack[i][1].get(token, None):
        return dictstack[i][1][token]
    elif dictstack[i][0] == i:
        return None
    else:
        return lookupHelp(token, dictstack[i][0])
    # return the value associated with name
    # What is your design decision about what to do when there is no definition for “name”? If “name” is not defined,
    # your program should not break, but should give an appropriate error message.

#--------------------------- 10% -------------------------------------
# Arithmetic and comparison operators: add, sub, mul, eq, lt, gt
# Make sure to check the operand stack has the correct number of parameters
# and types of the parameters are correct.
# Most of the code in this block was copied directly from the homework 4 instructions and edited to fit my needs
def add():
    if len(opstack) > 1:
        op2 = opPop()
        op1 = opPop()
        if (isinstance(op1, int) and isinstance(op2, int)):
            opPush(op1 + op2)
        else:
            print("Error: add - one of the operands is not a numerical value")
            replaceHelp([op1, op2])
    else:
        print("Error: add - expects 2 operands")

def sub():
    if len(opstack) > 1:
        op2 = opPop()
        op1 = opPop()
        if (isinstance(op1, int) and isinstance(op2, int)):
            opPush(op1 - op2)
        else:
            print("Error: sub - one of the operands is not a numerical value")
            replaceHelp([op1, op2])
    else:
        print("Error: sub - expects 2 operands")

def mul():
    if len(opstack) > 1:
        op2 = opPop()
        op1 = opPop()
        if (isinstance(op1, int) and isinstance(op2, int)):
            opPush(op1 * op2)
        else:
            print("Error: mul - one of the operands is not a numerical value")
            replaceHelp([op1, op2])
    else:
        print("Error: mul - expects 2 operands")

def eq():
    if len(opstack) > 1:
        op2 = opPop()
        op1 = opPop()
        if type(op1) == type(op2): # They don't need
            if op1 != op2:
                opPush(False)
            else:
                opPush(True)
        else:
            print("Error: eq - operand types don't match.")
            replaceHelp([op1, op2])
            opPush(False)
    else:
        print("Error: eq expects 2 operands")

def lt():
    if len(opstack) > 1:
        op2 = opPop()
        op1 = opPop()
        if (isinstance(op1, int) and isinstance(op2, int)):
            if op1 < op2:
                opPush(True)
            else:
                opPush(False)
        else:
            print("Error: lt - one of the operands is not a numerical value")
            replaceHelp([op1, op2])
    else:
        print("Error: lt expects 2 operands")

def gt():
    if len(opstack) > 1:
        op2 = opPop()
        op1 = opPop()
        if (isinstance(op1, int) and isinstance(op2, int)):
            if op1 > op2:
                opPush(True)
            else:
                opPush(False)
        else:
            print("Error: gt - one of the operands is not a numerical value")
            replaceHelp([op1, op2])
    else:
        print("Error: gt expects 2 operands")

#--------------------------- 20% -------------------------------------
# String operators: define the string operators length, get, getinterval,  putinterval, search
def length():
    strHope = opPop()
    if isinstance(strHope, str):
        opPush(len(strHope) - 2) # to account for the parenthesis
    else:
        print("Error: length - argument was not a string.")
        replaceHelp([strHope])

def get():
    if len(opstack) < 2:
        print("Error: get - not enough arguments.")
    else: #exec code here
        index = opPop()
        getStr = opPop()
        if isinstance(index, int) and isinstance(getStr, str):
            index += 1 # to account for the paren ( "(" )
            opPush(ord(getStr[index]))
        else:
            print("Error: get - operands were not of correct type.")
            replaceHelp([getStr, index])

def getinterval():
    if len(opstack) < 3:
        print("Error: getinterval - opstack does not have enough arguments.")
    else:  # carry out code
        countIn = opPop()
        indexIn = opPop()
        stringIn = opPop()
        # Each checks to make sure the corresponding
        if isinstance(stringIn, str) and isinstance(indexIn, int) and isinstance(countIn, int):
            opPush("(" + stringIn[indexIn + 1:countIn + indexIn + 1] + ")") # pushes the corresponding string to the stack
        else:
            print("Error: getinterval - some argument was not of the correct type.")
            replaceHelp([stringIn, indexIn, countIn])

def putinterval():
    if len(opstack) < 3:
        print("Error: putinterval - opstack does not have enough arguments.")
    else:
        valueIn = opPop()
        indexIn = opPop()
        stringIn = opPop()
        if isinstance(stringIn, str) and isinstance(indexIn, int) and isinstance(valueIn, str):
            repString = stringIn[0:indexIn + 1] + valueIn[1:len(valueIn) - 1] + stringIn[indexIn + len(valueIn) - 1:]
            opIn = len(opstack) - 1
            while opIn >= 0:
                if opstack[opIn] == stringIn:
                    opstack[opIn] = repString
                opIn -= 1
            dictIn = len(dictstack) - 1
            while dictIn >= 0:  # start at end of list and loop backwards through
                for key in dictstack[dictIn]:
                    if dictstack[dictIn][1] == stringIn:
                        dictstack[dictIn][key] = repString
                dictIn -= 1
        else:
            print("Error: putinterval - some argument was not of correct type.")
            replaceHelp([stringIn, indexIn, valueIn])

def search():
    if len(opstack) < 2:
        print("Error: search - opstack does not have enough arguments.")
    else:
        seekIn = opPop()
        stringIn = opPop()
        searchVal = seekIn[1:-1]
        if isinstance(stringIn, str) and isinstance(searchVal, str):
            if searchVal in stringIn:  # searchVal is in stringIn
                searchValIndex = 0
                for i in range(0, len(stringIn)):
                    if stringIn[i] == searchVal:
                        searchValIndex = i # represents the index where the searchVal was found
                        break
                # Messily pushes all of the strings and appropriate T/F value to the stack
                replaceHelp(["(" + stringIn[searchValIndex + len(searchVal):], "(" + searchVal + ")",
                             stringIn[0:searchValIndex] + ")", True])
            else:
                print("Search - seek string was not in original string.")
                replaceHelp([stringIn, False])
        else:
            print("Error: search - some operand was not of the right type.")
            replaceHelp([stringIn, seekIn])

#--------------------------- 18% -------------------------------------
# Array functions and operators:
#      define the helper function evaluateArray
#      define the array operators aload, astore

def evaluateArray(aInput, scope):
    count = len(aInput)
    for i in range(0, len(aInput)):
        if aInput[i] in internalOps: # is an operation
            internalOps[aInput[i]][0]()
            count -= internalOps[aInput[i]][1]
        else:
            if isinstance(aInput[i], str):
                if lookup(aInput[i],scope) is not None: # sees if we have a value associated with the string
                    opPush(lookup(aInput[i], scope)) # if so, we push the value to the stack
                else: # if no value is associated with the string, push the string to the stack
                    opPush(aInput[i])
            elif isinstance(aInput[i], int):
                opPush(aInput[i])
    retArr = [None] * count
    opPush(retArr)
    astore()
    return retArr

def aload():
    if not opstack:
        print("Error: aload - opstack is empty.")
    else:
        aloadArr = opPop()
        if isinstance(aloadArr, list):
            for i in aloadArr:
                opPush(i)
            opPush(aloadArr)
        else:
            print("Error: aload - argument was not of correct type.")
            replaceHelp([aloadArr])

def astore():
    if not opstack:
        print("Error: astore - opstack is empty.")
    else:
        astoreArr = opPop()
        if isinstance(astoreArr, list):
            for i in range(0, len(astoreArr)):
                astoreArr[i] = opPop()
            astoreArr.reverse()
            opPush(astoreArr)
        else:
            print("Error: astore - argument was not of correct type.")
            replaceHelp([astoreArr])

#--------------------------- 6% -------------------------------------
# Define the stack manipulation and print operators: dup, copy, count, pop, clear, exch, stack
def dup():
    if not opstack:
        print("Error: dup - opstack is empty.")
    else:
        dupVal = opPop()
        for i in range(0, 2):
            opPush(dupVal)

def copy():
    if not opstack:
        print("Error: copy - opstack is empty.")
    else:
        copyNum = opPop()
        if isinstance(copyNum, int):
            copyList = []
            for i in range(0, copyNum):
                copyList.append(opPop())
            copyList.reverse()
            for j in range(0, 2): # twice because we need push the list we popped the first time
                for i in range(0, len(copyList)):
                    opPush(copyList[i])
        else:
            print("Error: copy - argument was not of correct type.")
            replaceHelp([copyNum])

def count():
    opPush(len(opstack))

def pop():
    opstack.pop()

def clear():
    opstack.clear()
    dictstack.clear()

def exch():
    if len(opstack) < 2:
        print("Error: exch - not enough operands on opstack.")
    else:
        tempVar = opPop()
        tempVar2 = opPop()
        opPush(tempVar)
        opPush(tempVar2)

def stack():
    print("==============")
    opstack.reverse()
    for i in range(0, len(opstack)):
        print(opstack[i])
    opstack.reverse()
    print("==============")

    dictstack.reverse()
    for i in range(0, len(dictstack)):
        print("---- " + str(len(dictstack) - i - 1) + " ---- " + str(dictstack[len(dictstack) - 1][0]) + " ---- ")
        for j in dictstack[i][1]:
            print(j + "    " + str(dictstack[i][1].get(j)))
    dictstack.reverse()
    print("==============")

#--------------------------- 20% -------------------------------------
# Define the dictionary manipulation operators: psDict, begin, end, psDef
# name the function for the def operator psDef because def is reserved in Python. Similarly, call the function for dict operator as psDict.
# Note: The psDef operator will pop the value and name from the opstack and call your own "define" operator (pass those values as parameters).
# Note that psDef()won't have any parameters.
def psDict():
    if not opstack:
        print("Error: psDict - opstack is empty.")
    else:
        pop()
        opPush({})

def begin():
    if not opstack:
        print("Error: begin - opstack is empty.")
    else:
        if type(opstack[-1]) == dict:
            dictPush(opPop())
        else:
            print("Error: begin - last item in opstack is not a dictionary.")

def end():
    dictPop()

def psDef():
    if len(opstack) < 2:
        print("Error: psdef - opstack does not contain enough arguments.")
    else:
        varValue = opPop()
        varName = opPop()
        if type(varName) == str:
            define(varName, varValue)
        else:
            replaceHelp([varName, varValue])

# Replaces the variables in the case the function that called them doesn't work with them.
# This function assumes that everything is in the correct order already.
def replaceHelp(listInput):
    for i in listInput:
        opPush(i)

# Contains dictionary of operators as well as the amount of inputs that particular operator takes
# "key":[function, num of values used by stack]
internalOps = { "opPop":[opPop, 1],"pop":[opPop, 1], "add":[add, 2], "sub":[sub, 2], "mul":[mul, 2], "eq":[eq, 2],
                "lt":[lt, 2], "gt":[gt, 2], "length":[length, 1], "get":[get, 2], "getinterval":[getinterval, 3],
                "putinterval":[putinterval, 3], "search":[search, 2], "aload":[aload, 1], "astore":[astore, 1],
                "dup":[dup,0], "copy":[copy, 1], "def":[psDef, 2], "exch":[exch, 2], "clear":[clear, 0], "stack":[stack, 0],
                "for":[psFor, 4], "if":[psIf, 2], "ifelse":[psIfelse, 3], "count":[count, 0]}

# "end":[end, 0], "begin":[begin, 1], "dict":[psDict, 0],

def sspsTests():

    testinput1 = """
    /x 4 def
    /g { x stack } def
    /f { /x 7 def g } def
    f
    """

    testinput2 = """
    /x 4 def
    (static_?) dup 7 (x) putinterval /x exch def
    /g { x stack } def
    /f { /x (dynamic_x) def g } def
    f
    """

    testinput3 = """
    /m 50 def
    /n 100 def
    /egg1 {/m 25 def n} def
    /chic
    	{ /n 1 def
	      /egg2 { n stack} def
	      m  n
	      egg1
	      egg2
	    } def
    n
    chic
        """

    testinput4 = """
    /x 10 def
    /A { x } def
    /C { /x 40 def A stack } def
    /B { /x 30 def /A { x } def C } def
    B
    """

    testinput5 = """
    /x 2 def
    /n 5  def
    /A { 1  n -1 1 {pop x mul} for} def
    /C { /n 3 def /x 40 def A stack } def
    /B { /x 30 def /A { x } def C } def
    B
    """

    testinput6 = """
    /out true def 
    /xand { true eq {pop false} {true eq { false } { true } ifelse} ifelse dup /x exch def stack} def 
    /myput { out dup /x exch def xand } def 
    /f { /out false def myput } def 
    false f
    """

    testinput7 = """
    /x [1 2 3 4] def
    /A { x aload pop add add add } def
    /C { /x [10 20 30 40 50] def A stack } def
    /B { /x [6 7 8 9] def /A { x } def C } def
    B
    """

    testinput8 = """
    /x [2 3 4 5] def
    /a 10 def  
    /A { x } def
    /C { /x [a 2 mul a 3 mul dup a 4 mul] def A  a x stack } def
    /B { /x [6 7 8 9] def /A { x } def /a 5 def C } def
    B
    """

    # I wrote these following tests myself
    testinput9 = """
    /garrett 12 def 
    /alex 589 def
    add
    """

    testinput10 = """
    /LOLKEKWHAHA 4 def
    (static_?) dup 90 (x) putinterval /x exch def
    /g { LOLKEKWHAHA stack } def
    /o { /LOLKEKWHAHA (dynamic_x) def g } def
    o
    """

    testinput11 = """
    /q 420 def
    /w 69  def
    /T { 1  n -1 1 {pop x mul} for} def
    /P { /n 3 def /x 59 def T stack } def
    /B { /x 30 def /T { x } def P } def
    B
    """

    ssps_testinputs = [testinput1, testinput2, testinput3, testinput4, testinput5, testinput6, testinput7, testinput8, testinput9, testinput10, testinput11]
    i = 1
    for input in ssps_testinputs:
        print('TEST CASE -',i)
        i += 1
        print("Static")
        interpreter(input, "static")
        clearBoth()
        print("Dynamic")
        interpreter(input, "dynamic")
        clearBoth()
        print('\n-----------------------------')

if __name__ == "__main__":
    sspsTests()