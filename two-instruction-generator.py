from io import IncrementalNewlineDecoder
import multiprocessing
from pymtl3 import *
from typing_extensions import final
from FL.ProcFL import ProcFL
from RTL.ProcRTL import ProcRTL
from harness import *
import struct
import numpy as np
import random
import time
import os
from shutil import rmtree
codeAddrCounter = 0x200
dataAddrCounter = 0x0100000
instruction_list = [
    "ADD", "ADDI", "SUB", "MUL",
    "AND", "ANDI", "OR", "ORI", "XOR", "XORI",
    "SLT", "SLTI", "SLTU", "SLTIU",
    "SRA", "SRAI", "SRL", "SRLI", "SLL", "SLLI",
    "LUI", "AUIPC",
    "LW", "SW",
    "JAL", "JALR",
    "BEQ", "BNE", "BLT", "BGE", "BLTU", "BGEU",
]
RRR_INST = ['ADD', 'SUB', 'MUL', 'AND', 'OR', 'XOR', 'SLT', 'SLTU', 'SRA', 'SRL', 'SLL']
RR_INST = ['ADDI', 'ANDI', 'ORI', 'XORI', 'SLTI', 'SLTIU', 'SRAI', 'SRLI', 'SLLI', 
'LW', 'SW', 'JALR', 'BEQ', 'BNE', 'BLT', 'BGE', 'BLTU', 'BGEU']
R_INST = ['LUI', 'AUIPC', 'JAL']

reg_list = [
    "x0", "x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9",
    "x10", "x11", "x12", "x13", "x14", "x15", "x16", "x17", "x18", "x19",
    "x20", "x21", "x22", "x23", "x24", "x25", "x26", "x27", "x28", "x29",
    "x30", "x31"
]
def rshift(val, n): return val>>n if val >= 0 else (val+0x100000000)>>n
#param - > type:str, bits:int, 
def genTwoRandNum(bits1, bits2):
    rNum1 = Bits32(struct.unpack("<i", np.random.bytes(4))[0])
    rNum2 = Bits32(struct.unpack("<i", np.random.bytes(4))[0])
    if bits1 != 32: rNum1 = trunc(rNum1, bits1)
    if bits2 != 32: rNum2 = trunc(rNum2, bits2)
    return (rNum1, rNum2)
def genRRRCodeSecond(inst, dest, r1 ,r2, expect):
    tmp = []
    tmp.append(f"{inst} {dest},{r1},{r2}")
    if dest == "x0":  # Destination x0 Test
        tmp.append("csrw proc2mngr, x0 > 0")
    else:
        tmp.append(f"csrw proc2mngr, {dest} > {expect}")
    return tmp
def secondPart(inst, param1, param2=None, param3=None):
    global codeAddrCounter
    global dataAddrCounter
    if inst == "ADD":
        #return []
        if param2!= None and param3!=None:
            result = Bits32(0xFFFFFFFF & (param2['val'].int() + param3['val'].int()))
            return genRRRCodeSecond("add", param1['name'], param2['name'], param3['name'], result.int())
        elif param2 != None and param3==None:
            result = Bits32(0xFFFFFFFF & (param1['val'].int() + param2['val'].int()))
            return genRRRCodeSecond("add", param1['name'], param1['name'], param2['name'], result.int())
        else:
            result = Bits32(0xFFFFFFFF & (param1['val'].int() + param1['val'].int()))
            return genRRRCodeSecond("add", param1['name'], param1['name'], param1['name'], result.int())
    elif inst == "ADDI":
        return []
        imme = genTwoRandNum(12,12)[0]
        if param2!= None and param3!=None:
            result = Bits32(0xFFFFFFFF & (param2['val'].int() + sext(imme,32).int()))
            return genRRRCodeSecond("addi", param1['name'], param2['name'], imme.int(), result.int())
        elif param2 != None and param3==None:
            result = Bits32(0xFFFFFFFF & (param1['val'].int() + sext(imme,32).int()))
            return genRRRCodeSecond("addi", param1['name'], param1['name'], imme.int(), result.int())
        else:
            result = Bits32(0xFFFFFFFF & (param1['val'].int() + sext(imme,32).int()))
            return genRRRCodeSecond("addi", param1['name'], param1['name'], imme.int(), result.int())
    elif inst == "SUB":
        return []
        if param2!= None and param3!=None:
            result = Bits32(0xFFFFFFFF & (param2['val'].int() - param3['val'].int()))
            return genRRRCodeSecond("sub", param1['name'], param2['name'], param3['name'], result.int())
        elif param2 != None and param3==None:
            result = Bits32(0xFFFFFFFF & (param1['val'].int() - param2['val'].int()))
            return genRRRCodeSecond("sub", param1['name'], param1['name'], param2['name'], result.int())
        else:
            result = Bits32(0xFFFFFFFF & (param1['val'].int() - param1['val'].int()))
            return genRRRCodeSecond("sub", param1['name'], param1['name'], param1['name'], result.int())
    elif inst == "MUL":
        return []
        if param2!= None and param3!=None:
            result = Bits32(0xFFFFFFFF & (param2['val'].int() * param3['val'].int()))
            return genRRRCodeSecond("mul", param1['name'], param2['name'], param3['name'], result.int())
        elif param2 != None and param3==None:
            result = Bits32(0xFFFFFFFF & (param1['val'].int() * param2['val'].int()))
            return genRRRCodeSecond("mul", param1['name'], param1['name'], param2['name'], result.int())
        else:
            result = Bits32(0xFFFFFFFF & (param1['val'].int() * param1['val'].int()))
            return genRRRCodeSecond("mul", param1['name'], param1['name'], param1['name'], result.int())
    elif inst == "AND":
        return []
        if param2!= None and param3!=None:
            result = Bits32(0xFFFFFFFF & (param2['val'].int() & param3['val'].int()))
            return genRRRCodeSecond("and", param1['name'], param2['name'], param3['name'], result.int())
        elif param2 != None and param3==None:
            result = Bits32(0xFFFFFFFF & (param1['val'].int() & param2['val'].int()))
            return genRRRCodeSecond("and", param1['name'], param1['name'], param2['name'], result.int())
        else:
            result = Bits32(0xFFFFFFFF & (param1['val'].int() & param1['val'].int()))
            return genRRRCodeSecond("and", param1['name'], param1['name'], param1['name'], result.int())
    elif inst == "ANDI":
        return []
        imme = genTwoRandNum(12,12)[0]
        if param2!= None and param3!=None:
            result = Bits32(0xFFFFFFFF & (param2['val'].int() & sext(imme,32).int()))
            return genRRRCodeSecond("andi", param1['name'], param2['name'], imme.int(), result.int())
        elif param2 != None and param3==None:
            result = Bits32(0xFFFFFFFF & (param1['val'].int() & sext(imme,32).int()))
            return genRRRCodeSecond("andi", param1['name'], param1['name'], imme.int(), result.int())
        else:
            result = Bits32(0xFFFFFFFF & (param1['val'].int() & sext(imme,32).int()))
            return genRRRCodeSecond("andi", param1['name'], param1['name'], imme.int(), result.int())
    elif inst=="OR":
        return []
        if param2!= None and param3!=None:
            result = Bits32(0xFFFFFFFF & (param2['val'].int() | param3['val'].int()))
            return genRRRCodeSecond("or", param1['name'], param2['name'], param3['name'], result.int())
        elif param2 != None and param3==None:
            result = Bits32(0xFFFFFFFF & (param1['val'].int() | param2['val'].int()))
            return genRRRCodeSecond("or", param1['name'], param1['name'], param2['name'], result.int())
        else:
            result = Bits32(0xFFFFFFFF & (param1['val'].int() | param1['val'].int()))
            return genRRRCodeSecond("or", param1['name'], param1['name'], param1['name'], result.int())
    elif inst=="ORI":
        return []
        imme = genTwoRandNum(12,12)[0]
        if param2!= None and param3!=None:
            result = Bits32(0xFFFFFFFF & (param2['val'].int() | sext(imme,32).int()))
            return genRRRCodeSecond("ori", param1['name'], param2['name'], imme.int(), result.int())
        elif param2 != None and param3==None:
            result = Bits32(0xFFFFFFFF & (param1['val'].int() | sext(imme,32).int()))
            return genRRRCodeSecond("ori", param1['name'], param1['name'], imme.int(), result.int())
        else:
            result = Bits32(0xFFFFFFFF & (param1['val'].int() | sext(imme,32).int()))
            return genRRRCodeSecond("ori", param1['name'], param1['name'], imme.int(), result.int())
    elif inst=="XOR":
        return []
        if param2!= None and param3!=None:
            result = Bits32(0xFFFFFFFF & (param2['val'].int() ^ param3['val'].int()))
            return genRRRCodeSecond("xor", param1['name'], param2['name'], param3['name'], result.int())
        elif param2 != None and param3==None:
            result = Bits32(0xFFFFFFFF & (param1['val'].int() ^ param2['val'].int()))
            return genRRRCodeSecond("xor", param1['name'], param1['name'], param2['name'], result.int())
        else:
            result = Bits32(0xFFFFFFFF & (param1['val'].int() ^ param1['val'].int()))
            return genRRRCodeSecond("xor", param1['name'], param1['name'], param1['name'], result.int())
    elif inst=="XORI":
        return []
        imme = genTwoRandNum(12,12)[0]
        if param2!= None and param3!=None:
            result = Bits32(0xFFFFFFFF & (param2['val'].int() ^ sext(imme,32).int()))
            return genRRRCodeSecond("xori", param1['name'], param2['name'], imme.int(), result.int())
        elif param2 != None and param3==None:
            result = Bits32(0xFFFFFFFF & (param1['val'].int() ^ sext(imme,32).int()))
            return genRRRCodeSecond("xori", param1['name'], param1['name'], imme.int(), result.int())
        else:
            result = Bits32(0xFFFFFFFF & (param1['val'].int() ^ sext(imme,32).int()))
            return genRRRCodeSecond("xori", param1['name'], param1['name'], imme.int(), result.int())
    elif inst=="SLT":
        return []
        if param2!= None and param3!=None:
            result = Bits32(0xFFFFFFFF & int(param2['val'].int() < param3['val'].int()))
            return genRRRCodeSecond("slt", param1['name'], param2['name'], param3['name'], result.int())
        elif param2 != None and param3==None:
            result = Bits32(0xFFFFFFFF & int(param1['val'].int() < param2['val'].int()))
            return genRRRCodeSecond("slt", param1['name'], param1['name'], param2['name'], result.int())
        else:
            result = Bits32(0xFFFFFFFF & int(param1['val'].int() < param1['val'].int()))
            return genRRRCodeSecond("slt", param1['name'], param1['name'], param1['name'], result.int())
    elif inst=="SLTI":
        return []
        imme = genTwoRandNum(12,12)[0]
        if param2!= None and param3!=None:
            result = Bits32(0xFFFFFFFF & int(param2['val'].int() < sext(imme,32).int()))
            return genRRRCodeSecond("slti", param1['name'], param2['name'], imme.int(), result.int())
        elif param2 != None and param3==None:
            result = Bits32(0xFFFFFFFF & int(param1['val'].int() < sext(imme,32).int()))
            return genRRRCodeSecond("slti", param1['name'], param1['name'], imme.int(), result.int())
        else:
            result = Bits32(0xFFFFFFFF & int(param1['val'].int() < sext(imme,32).int()))
            return genRRRCodeSecond("slti", param1['name'], param1['name'], imme.int(), result.int())
    elif inst=="SLTU":
        return [] 
        if param2!= None and param3!=None:
            result = Bits32(0xFFFFFFFF & int(param2['val'].uint() < param3['val'].uint()))
            return genRRRCodeSecond("sltu", param1['name'], param2['name'], param3['name'], result.int())
        elif param2 != None and param3==None:
            result = Bits32(0xFFFFFFFF & int(param1['val'].uint() < param2['val'].uint()))
            return genRRRCodeSecond("sltu", param1['name'], param1['name'], param2['name'], result.int())
        else:
            result = Bits32(0xFFFFFFFF & int(param1['val'].uint() < param1['val'].uint()))
            return genRRRCodeSecond("sltu", param1['name'], param1['name'], param1['name'], result.int())
    elif inst=="SLTIU":
        return []
        imme = genTwoRandNum(12,12)[0]
        if param2!= None and param3!=None:
            result = Bits32(0xFFFFFFFF & int(param2['val'].uint() < sext(imme,32).uint()))
            return genRRRCodeSecond("sltiu", param1['name'], param2['name'], imme.int(), result.int())
        elif param2 != None and param3==None:
            result = Bits32(0xFFFFFFFF & int(param1['val'].uint() < sext(imme,32).uint()))
            return genRRRCodeSecond("sltiu", param1['name'], param1['name'], imme.int(), result.int())
        else:
            result = Bits32(0xFFFFFFFF & int(param1['val'].uint() < sext(imme,32).uint()))
            return genRRRCodeSecond("sltiu", param1['name'], param1['name'], imme.uint(), result.uint())
    elif inst=="SRA":
        return []
        if param2!= None and param3!=None:
            result = Bits32(0xFFFFFFFF & (param2['val'].int() >> (param3['val'].int() & 0x1F)))
            return genRRRCodeSecond("sra", param1['name'], param2['name'], param3['name'], result.int())
        elif param2 != None and param3==None:
            result = Bits32(0xFFFFFFFF & (param1['val'].int() >> (param2['val'].int() & 0x1F)))
            return genRRRCodeSecond("sra", param1['name'], param1['name'], param2['name'], result.int())
        else:
            result = Bits32(0xFFFFFFFF & (param1['val'].int() >> (param1['val'].int() & 0x1F)))
            return genRRRCodeSecond("sra", param1['name'], param1['name'], param1['name'], result.int())
    elif inst=="SRAI":
        return []
        imme = genTwoRandNum(12,12)[0]
        if param2!= None and param3!=None:
            result = Bits32(0xFFFFFFFF & (param2['val'].int() >> (imme.int()&0x1F)))
            return genRRRCodeSecond("srai", param1['name'], param2['name'], (imme.int()&0x1F), result.int())
        elif param2 != None and param3==None:
            result = Bits32(0xFFFFFFFF & (param1['val'].int() >> (imme.int()&0x1F)))
            return genRRRCodeSecond("srai", param1['name'], param1['name'], (imme.int()&0x1F), result.int())
        else:
            result = Bits32(0xFFFFFFFF & (param1['val'].int() >> (imme.int()&0x1F)))
            return genRRRCodeSecond("srai", param1['name'], param1['name'], (imme.int()&0x1F), result.int())
    elif inst=="SRL":
        return []
        if param2!= None and param3!=None:
            result = Bits32(0xFFFFFFFF & rshift(param2['val'].int() , param3['val'].int() & 0x1F))
            return genRRRCodeSecond("srl", param1['name'], param2['name'], param3['name'], result.int())
        elif param2 != None and param3==None:
            result = Bits32(0xFFFFFFFF & rshift(param1['val'].int() , param2['val'].int() & 0x1F))
            return genRRRCodeSecond("srl", param1['name'], param1['name'], param2['name'], result.int())
        else:
            result = Bits32(0xFFFFFFFF & rshift(param1['val'].int() , param1['val'].int() & 0x1F))
            return genRRRCodeSecond("srl", param1['name'], param1['name'], param1['name'], result.int())
    elif inst=="SRLI":
        return []
        imme = genTwoRandNum(12,12)[0] & Bits12(0x1F)
        if param2!= None and param3!=None:
            result = Bits32(0xFFFFFFFF & (param2['val'].int() >> imme.int()))
            return genRRRCodeSecond("srli", param1['name'], param2['name'], imme.int(), result.int())
        elif param2 != None and param3==None:
            result = Bits32(0xFFFFFFFF & (param1['val'].int() >> imme.int()))
            return genRRRCodeSecond("srli", param1['name'], param1['name'], imme.int(), result.int())
        else:
            result = Bits32(0xFFFFFFFF & (param1['val'].int() >> imme.int()))
            return genRRRCodeSecond("srli", param1['name'], param1['name'], imme.int(), result.int())
    elif inst=="SLL":
        return []
        if param2!= None and param3!=None:
            result = Bits32(0xFFFFFFFF & (param2['val'].int() << (param3['val'].int() & 0x1F)))
            return genRRRCodeSecond("sll", param1['name'], param2['name'], param3['name'], result.int())
        elif param2 != None and param3==None:
            result = Bits32(0xFFFFFFFF & (param1['val'].int() << (param2['val'].int() & 0x1F)))
            return genRRRCodeSecond("sll", param1['name'], param1['name'], param2['name'], result.int())
        else:
            result = Bits32(0xFFFFFFFF & (param1['val'].int() << (param1['val'].int() & 0x1F)))
            return genRRRCodeSecond("sll", param1['name'], param1['name'], param1['name'], result.int())
    elif inst=="SLLI":
        return []
        imme = genTwoRandNum(12,12)[0] & Bits12(0x1F)
        if param2!= None and param3!=None:
            result = Bits32(0xFFFFFFFF & (param2['val'].int() << imme.int()))
            return genRRRCodeSecond("slli", param1['name'], param2['name'], imme.int(), result.int())
        elif param2 != None and param3==None:
            result = Bits32(0xFFFFFFFF & (param1['val'].int() << imme.int()))
            return genRRRCodeSecond("slli", param1['name'], param1['name'], imme.int(), result.int())
        else:
            result = Bits32(0xFFFFFFFF & (param1['val'].int() << imme.int()))
            return genRRRCodeSecond("slli", param1['name'], param1['name'], imme.int(), result.int())
    elif inst=="LUI":
        return []
        single = []
        imme = struct.unpack("<i", np.random.bytes(4))[0]&0b1111_1111_1111_1111_1111
        result = int(hex(imme)+"000", 16)
        single.append(f"lui {param1['name']}, {imme}")
        if param1['name'] == "x0":  # Destination x0 Test
            single.append("csrw proc2mngr, x0 > 0")
        else: single.append(f"csrw proc2mngr, {param1['name']} > {result}")
        return single
    elif inst=="AUIPC":
        return []
        global codeAddrCounter
        single = []
        imme = struct.unpack("<i", np.random.bytes(4))[0]&0b1111_1111_1111_1111_1111
        result = int(hex(imme)+"000", 16)
        single.append(f"auipc {param1['name']}, {imme}")
        if param1['name'] == "x0":  # Destination x0 Test
            single.append("csrw proc2mngr, x0 > 0")
        else: single.append(f"csrw proc2mngr, {param1['name']} > {(codeAddrCounter+result)&0xFFFFFFFF}")
        codeAddrCounter+=(len(single)*4)
        return single
    elif inst=="LW":
        #return []
        singleTest = []
        randOffset = random.randint(0, 0xFFB)
        randWord = "0x"+np.random.bytes(4).hex()
        singleTest.append(f"csrr x1, mngr2proc < {dataAddrCounter}")
        if param2 ==None:
            singleTest.append(f"csrr {param1['name']}, mngr2proc < {randWord}")
            singleTest.append(f"sw {param1['name']}, {randOffset}(x1)")
            singleTest.append(f"add {param1['name']}, x0,-1")
            singleTest.append(f"lw   {param1['name']}, {randOffset}(x1)")
        else:
            singleTest.append(f"csrr {param2['name']}, mngr2proc < {randWord}")
            singleTest.append(f"sw {param2['name']}, {randOffset}(x1)")
            singleTest.append(f"lw   {param1['name']}, {randOffset}(x1)")
        if param1['name']=="x0":singleTest.append("csrw proc2mngr, x0 > 0")
        elif param2!=None and param2['name']=="x0":singleTest.append(f"csrw proc2mngr, {param1['name']} > 0")
        else :singleTest.append(f"csrw proc2mngr, {param1['name']} > {randWord}")
        return singleTest
    elif inst=="SW":
        #return []
        singleTest = []
        randOffset = random.randint(0, 0xFFB)
        randWord = "0x"+np.random.bytes(4).hex()
        singleTest.append(f"csrr x1, mngr2proc < {dataAddrCounter}")
        singleTest.append(f"csrr {param2['name'] if param2 != None else param1['name']}, mngr2proc < {randWord}")
        singleTest.append(f"sw   {param2['name'] if param2 != None else param1['name']}, {randOffset}(x1)")
        singleTest.append(f"lw   {param1['name']}, {randOffset}(x1)")
        if param1['name']=='x0':singleTest.append(f"csrw proc2mngr, {param1['name']} > 0")
        elif param2 != None and param2['name'] == "x0":singleTest.append(f"csrw proc2mngr, {param1['name']} > 0")
        else:singleTest.append(f"csrw proc2mngr, {param1['name']} > {randWord}")
        return singleTest
    elif inst=="JAL":
        #return []
        singleTest = []
        r = random.randint(0, 10)
        singleTest.append(f"jal {param1['name']}, {(r+1)*4}")
        for i in range(r):
            singleTest.append(f"add {param1['name']}, {param1['name']}, {param1['name']}")#Non jmp hit
        if param1['name'] == "x0":singleTest.append(f"csrw  proc2mngr, {param1['name']} > 0")
        else:singleTest.append(f"csrw  proc2mngr, {param1['name']} > {hex(codeAddrCounter+4)}")
        return singleTest
    elif inst=="JALR":
        #return []
        singleTest = []
        r = random.randint(0, 10)
        if param2!=None:
            singleTest.append(f"csrr  {param2['name']}, mngr2proc < {hex(codeAddrCounter)}")
        else:
            singleTest.append(f"csrr  x1, mngr2proc < {hex(codeAddrCounter)}")
        singleTest.append(f"jalr  {param1['name']}, {param2['name'] if param2 !=None else 'x1'}, {(r+2)*4}")#204
        for i in range(r):
            singleTest.append(f"add {param1['name']},{param1['name']}, {param1['name']}")#Error Test
        if param1['name'] == "x0":singleTest.append(f"csrw  proc2mngr, {param1['name']} > 0")# At least 208
        else:singleTest.append(f"csrw  proc2mngr, {param1['name']} > {hex(codeAddrCounter+8)}")
        #codeAddrCounter+=(len(singleTest)*4)
        return singleTest
    elif inst == "BEQ":
        return []
        tmp = []
        tmp.append(f"beq {param1['name']},x0, 8")
        tmp.append(f"addi {param1['name']},{param1['name']},{-1}")#Hit test
        if param1['val'].int()==0:tmp.append(f"csrw  proc2mngr, {param1['name']} > {param1['val'].int()}")
        else: tmp.append(f"csrw  proc2mngr, {param1['name']} > {param1['val'].int()-1 if param1['name']!='x0' else 0}")
        return tmp
    elif inst == "BNE":
        return []
        tmp = []
        tmp.append(f"bne {param1['name']},x0, 8")
        tmp.append(f"addi {param1['name']},{param1['name']},{-1}")#Hit test
        if param1['val'].int()!=0:tmp.append(f"csrw  proc2mngr, {param1['name']} > {param1['val'].int()}")
        else: tmp.append(f"csrw  proc2mngr, {param1['name']} > {param1['val'].int()-1 if param1['name']!='x0' else 0}")
        return tmp
    elif inst == "BLT":
        return []
        tmp = []
        tmp.append(f"blt {param1['name']},x0, 8")
        tmp.append(f"addi {param1['name']},{param1['name']},{-1}")#Hit test
        if param1['val'].int()<0:tmp.append(f"csrw  proc2mngr, {param1['name']} > {param1['val'].int()}")
        else: tmp.append(f"csrw  proc2mngr, {param1['name']} > {param1['val'].int()-1 if param1['name']!='x0' else 0}")
        return tmp
    elif inst == "BGE":
        #return []
        tmp = []
        tmp.append(f"bge {param1['name']},x0, 8")
        tmp.append(f"addi {param1['name']},{param1['name']},{-1}")#Hit test
        if param1['val'].int()>=0:tmp.append(f"csrw  proc2mngr, {param1['name']} > {param1['val'].int()}")
        else: tmp.append(f"csrw  proc2mngr, {param1['name']} > {param1['val'].int()-1 if param1['name']!='x0' else 0}")
        return tmp
    elif inst == "BLTU":
        return []
        tmp = []
        tmp.append(f"bltu {param1['name']},x0, 8")
        tmp.append(f"addi {param1['name']},{param1['name']},{-1}")#Hit test
        if param1['val'].uint()<0:tmp.append(f"csrw  proc2mngr, {param1['name']} > {param1['val'].uint()}")
        else: tmp.append(f"csrw  proc2mngr, {param1['name']} > {param1['val'].int()-1 if param1['name']!='x0' else 0}")
        return tmp
    elif inst == "BGEU":
        return []
        tmp = []
        tmp.append(f"bgeu {param1['name']},x0, 8")
        tmp.append(f"addi {param1['name']},{param1['name']},{-1}")#Hit test
        if param1['val'].uint()>=0:tmp.append(f"csrw  proc2mngr, {param1['name']} > {param1['val'].uint()}")
        else: tmp.append(f"csrw  proc2mngr, {param1['name']} > {param1['val'].int()-1 if param1['name']!='x0' else 0}")
        return tmp
def genRRRCodeFirst(inst, dest, r1 ,r2, val1, val2):
    tmp = []
    tmp.extend([f"csrr {r1}, mngr2proc < {val1}",
               f"csrr {r2}, mngr2proc < {val2}"])  # Init RS1 and RS2
    tmp.append(f"{inst} {dest},{r1},{r2}")
    return tmp
def genRRCodeFirst(inst, dest, r1 , val1, val2):
    tmp = []
    tmp.append(f"csrr {r1}, mngr2proc < {val1}")  
    tmp.append(f"{inst} {dest},{r1},{val2}")
    return tmp
def getRRRValues(inst, dest, r1 ,r2):
        val1, val2 = genTwoRandNum(32,32)
        if r1== r2:val1 = val2
        code = genRRRCodeFirst(inst, dest, r1, r2, val1.int(), val2.int())
        if r1=="x0":val1 = Bits32(0)
        if r2=="x0":val2 = Bits32(0)
        return (val1, val2, code)
def returnRRRValues(dest, r1 ,r2, val1, val2, result, code):
        if dest == r1:val1 = result
        if dest == r2:val2 = result
        return [
            {"name":dest, "val":result if dest!="x0" else Bits32(0)}, 
            {"name":r1, "val":val1 if r1!="x0" else Bits32(0)}, 
            {"name":r2, "val":val2 if r2!="x0" else Bits32(0)}, 
            code
        ]
def returnRRValues(dest, r1 , val1, result, code):
        if dest == r1:val1 = result
        return [
            {"name":dest, "val":result if dest!="x0" else Bits32(0)}, 
            {"name":r1, "val":val1 if r1!="x0" else Bits32(0)}, 
            None, 
            code
        ]
def getRRValues(inst, dest, r1 ):
        val1, val2 = genTwoRandNum(32,12)
        code = genRRCodeFirst(inst, dest, r1, val1.int(), val2.int())
        if r1=="x0":val1 = Bits32(0)
        return (val1, val2, code)
def getBValues(inst, r1 ,r2):
    val1, val2 = genTwoRandNum(32,32)
    if r2 == r1:val1 = val2
    tmp = []
    tmp.append(f"csrr  {r1}, mngr2proc < {val1.int()}")
    tmp.append(f"csrr  {r2}, mngr2proc < {val2.int()}")
    tmp.append(f"{inst} {r1},{r2}, 8")
    tmp.append(f"addi {r1},{r2},{-1}")#Hit test
    if r1=="x0":val1 = Bits32(0)
    if r2=="x0":val2 = Bits32(0)

    return (val1, val2, tmp)
def returnBValues(r1, r2 , val1, val2, code):
        if r1 == r2:val2 = val1
        return [
            {"name":r1, "val":val1 if r1!="x0" else Bits32(0)}, 
            {"name":r2, "val":val2 if r2!="x0" else Bits32(0)}, 
            None, 
            code
        ]
def firstPart(inst, dest, r1=None, r2=None):
    if inst == "ADD":
        #return []
        val1, val2 = genTwoRandNum(32,32)
        if r1== r2:val1 = val2
        code = genRRRCodeFirst("add", dest, r1, r2, val1.int(), val2.int())
        if r1=="x0":val1 = Bits32(0)
        if r2=="x0":val2 = Bits32(0)
        result = Bits32(0xFFFFFFFF & (val1.int() + val2.int()))
        if dest == r1:val1 = result
        if dest == r2:val2 = result
        return [
            {"name":dest, "val":result if dest!="x0" else Bits32(0)}, 
            {"name":r1, "val":val1 if r1!="x0" else Bits32(0)}, 
            {"name":r2, "val":val2 if r2!="x0" else Bits32(0)}, 
            code
        ]
    elif inst == "ADDI":
        return []
        val1, val2 = genTwoRandNum(32,12)
        code = genRRCodeFirst("addi", dest, r1, val1.int(), val2.int())
        if r1=="x0":val1 = Bits32(0)
        result = Bits32(0xFFFFFFFF & (val1.int() + val2.int()))
        if dest == r1:val1 = result
        return [
            {"name":dest, "val":result if dest!="x0" else Bits32(0)}, 
            {"name":r1, "val":val1 if r1!="x0" else Bits32(0)}, 
            None, 
            code
        ]
    elif inst == "SUB":
        return []
        val1, val2, code = getRRRValues("sub", dest, r1, r2)
        result = Bits32(0xFFFFFFFF & (val1.int() - val2.int()))
        return returnRRRValues(dest, r1,r2, val1,val2,result,code)
    elif inst == "MUL":
        return []
        val1, val2, code = getRRRValues("mul", dest, r1, r2)
        result = Bits32(0xFFFFFFFF & (val1.int() * val2.int()))
        return returnRRRValues(dest, r1,r2, val1,val2,result,code)
    elif inst == "AND":
        return []
        val1, val2, code = getRRRValues("and", dest, r1, r2)
        result = Bits32(0xFFFFFFFF & (val1.int() & val2.int()))
        return returnRRRValues(dest, r1,r2, val1,val2,result,code)
    elif inst == "ANDI":
        return []
        val1, val2, code = getRRValues("andi", dest, r1)
        result = Bits32(0xFFFFFFFF & (val1.int() & val2.int()))
        return returnRRValues(dest, r1, val1,result,code)
    elif inst=="OR":
        return []
        val1, val2, code = getRRRValues("or", dest, r1, r2)
        result = Bits32(0xFFFFFFFF & (val1.int() | val2.int()))
        return returnRRRValues(dest, r1,r2, val1,val2,result,code)
    elif inst=="ORI":
        return []
        val1, val2, code = getRRValues("ori", dest, r1)
        result = Bits32(0xFFFFFFFF & (val1.int() | val2.int()))
        return returnRRValues(dest, r1, val1,result,code)
    elif inst=="XOR":
        return []
        val1, val2, code = getRRRValues("xor", dest, r1, r2)
        result = Bits32(0xFFFFFFFF & (val1.int() ^ val2.int()))
        return returnRRRValues(dest, r1,r2, val1,val2,result,code)
    elif inst=="XORI":
        return []
        val1, val2, code = getRRValues("xori", dest, r1)
        result = Bits32(0xFFFFFFFF & (val1.int() ^ val2.int()))
        return returnRRValues(dest, r1, val1,result,code)
    elif inst=="SLT":
        return []
        val1, val2, code = getRRRValues("slt", dest, r1, r2)
        result = Bits32(0xFFFFFFFF & int(val1.int() < val2.int()))
        return returnRRRValues(dest, r1,r2, val1,val2,result,code)
    elif inst=="SLTI":
        return []
        val1, val2, code = getRRValues("slti", dest, r1)
        result = Bits32(0xFFFFFFFF & int(val1.int() < val2.int()))
        return returnRRValues(dest, r1, val1,result,code)
    elif inst=="SLTU":
        return []
        val1, val2, code = getRRRValues("sltu", dest, r1, r2)
        result = Bits32(0xFFFFFFFF & int(val1.uint() < val2.uint()))
        return returnRRRValues(dest, r1,r2, val1,val2,result,code)
    elif inst=="SLTIU":
        return []
        val1, val2, code = getRRValues("sltiu", dest, r1)
        result = Bits32(0xFFFFFFFF & int(val1.uint() < val2.uint()))
        return returnRRValues(dest, r1, val1,result,code)
    elif inst=="SRA":
        return []
        val1, val2, code = getRRRValues("sra", dest, r1, r2)
        result = Bits32(0xFFFFFFFF & val1.int() >> (val2.int()&0x1F))
        return returnRRRValues(dest, r1,r2, val1,val2,result,code)
    elif inst=="SRAI":
        return []
        val1, val2, code = getRRValues("srai", dest, r1)
        result = Bits32(0xFFFFFFFF & val1.int() >> (val2.int()&0x1F))
        return returnRRValues(dest, r1, val1,result,code)
    elif inst=="SRL":
        return []
        val1, val2, code = getRRRValues("srl", dest, r1, r2)
        result = Bits32(0xFFFFFFFF & rshift(val1.int(), (val2.int()&0x1F)) )
        return returnRRRValues(dest, r1,r2, val1,val2,result,code)
    elif inst=="SRLI":
        return []
        val1, val2, code = getRRValues("srli", dest, r1)
        result = Bits32(0xFFFFFFFF & rshift(val1.int() , (val2.int()&0x1F)))
        return returnRRValues(dest, r1, val1,result,code)
    elif inst=="SLL":
        return []
        val1, val2, code = getRRRValues("sll", dest, r1, r2)
        result = Bits32(0xFFFFFFFF & val1.int() << (val2.int()&0x1F))
        return returnRRRValues(dest, r1,r2, val1,val2,result,code)
    elif inst=="SLLI":
        return []
        val1, val2, code = getRRValues("slli", dest, r1)
        result = Bits32(0xFFFFFFFF & val1.int() << (val2.int()&0x1F))
        return returnRRValues(dest, r1, val1,result,code)
    elif inst=="LUI":
        return []
        tmp = []
        imme = genTwoRandNum(20,32)[0]
        result = Bits32(int(hex(imme)+"000", 16))
        tmp.append(f"lui {dest}, {imme.uint()}")
        return [
            {"name":dest, "val":result if dest!="x0" else Bits32(0)}, 
            None,
            None, 
            tmp
        ]
    elif inst=="AUIPC":
        return []
        tmp = []
        imme = genTwoRandNum(20,32)[0]
        result = Bits32((int(hex(imme.int())+"000", 16) + codeAddrCounter)&0xFFFFFFFF)
        tmp.append(f"auipc {dest}, {imme.int()}")
        return [
            {"name":dest, "val":result if dest!="x0" else Bits32(0)}, 
            None,
            None, 
            tmp
        ]
    elif inst=="LW":
        #return []
        singleTest = []
        randOffset = random.randint(0, 0xFFB)
        randWord = "0x"+np.random.bytes(4).hex()
        singleTest.append(f"csrr x1, mngr2proc < {dataAddrCounter}")
        singleTest.append(f"csrr {dest}, mngr2proc < {randWord}")
        singleTest.append(f"sw   {dest}, {randOffset}(x1)")
        for i in range(random.randint(0,3)):
            singleTest.append("nop")
        singleTest.append(f"lw   {r1}, {randOffset}(x1)")
        return [
            {"name":dest, "val":b32(int(randWord, 16)) if dest!="x0" else Bits32(0)}, 
            {"name":r1, "val":b32(int(randWord, 16)) if r1!="x0" else Bits32(0)}, 
            None, 
            singleTest,
        ]
    elif inst=="SW":
        #return []
        singleTest = []
        randOffset = random.randint(0, 0xFFB)
        randWord = "0x"+np.random.bytes(4).hex()
        singleTest.append(f"csrr x1, mngr2proc < {dataAddrCounter}")
        singleTest.append(f"csrr {dest}, mngr2proc < {randWord}")
        singleTest.append(f"sw   {dest}, {randOffset}(x1)")
        singleTest.append(f"lw   {r1}, {randOffset}(x1)")
        return [
            {"name":dest, "val":b32(int(randWord, 16)) if dest!="x0" else Bits32(0)}, 
            {"name":r1, "val":b32(int(randWord, 16)) if r1!="x0" else Bits32(0)}, 
            None, 
            singleTest,
        ]
    elif inst=="JAL":
        #return []
        singleTest = []
        r = random.randint(0, 10)
        singleTest.append(f"jal {dest}, {(r+1)*4}")
        for i in range(r):
            singleTest.append(f"add {dest}, {dest}, {dest}")#Non jmp hit
        return [
            {"name":dest, "val":b32(codeAddrCounter+4) if dest!="x0" else Bits32(0)}, 
            None,
            None, 
            singleTest
        ]
    elif inst=="JALR":
        return []
        singleTest = []
        r = random.randint(0, 10)
        singleTest.append(f"csrr  {r1}, mngr2proc < {hex(codeAddrCounter)}")
        singleTest.append(f"jalr  {dest}, {r1}, {(r+2)*4}")#204
        for i in range(r):
            singleTest.append(f"add {dest},{dest}, {dest}")#Error Test
        val1 = b32(codeAddrCounter+8)
        val2 = b32(codeAddrCounter)
        if dest == r1: val2 = val1
        return [
            {"name":dest, "val":val1 if dest!="x0" else Bits32(0)}, 
            {"name":r1, "val":val2 if r1!="x0" else Bits32(0)}, 
            None, 
            singleTest
        ]
    elif inst == "BEQ":
        return []
        val1, val2, code = getBValues("beq", dest, r1)
        if val1.int() == val2.int():
            return returnBValues(dest, r1, val1, val2, code)
        else: return returnBValues(dest, r1, val2-1, val2, code)
    elif inst == "BNE":
        return []
        val1, val2, code = getBValues("bne", dest, r1)
        if val1.int() != val2.int():
            return returnBValues(dest, r1, val1, val2, code)
        else: return returnBValues(dest, r1, val2-1, val2, code)
    elif inst == "BLT":
        return []
        val1, val2, code = getBValues("blt", dest, r1)
        if val1.int() < val2.int():
            return returnBValues(dest, r1, val1, val2, code)
        else: return returnBValues(dest, r1, val2-1, val2, code)
    elif inst == "BGE":
        return []
        val1, val2, code = getBValues("bge", dest, r1)
        if val1.int() >= val2.int():
            return returnBValues(dest, r1, val1, val2, code)
        else: return returnBValues(dest, r1, val2-1, val2, code)
    elif inst == "BLTU":
        return []
        val1, val2, code = getBValues("bltu", dest, r1)
        if val1.uint() < val2.uint():
            return returnBValues(dest, r1, val1, val2, code)
        else: return returnBValues(dest, r1, val2-1, val2, code)
    elif inst == "BGEU":
        return []
        val1, val2, code = getBValues("bgeu", dest, r1)
        if val1.uint() >= val2.uint():
            return returnBValues(dest, r1, val1, val2, code)
        else: return returnBValues(dest, r1, val2-1, val2, code)
lastInst2 = None
def genProgram(inst1, inst2, dest, r1=None, r2=None):
    global lastInst2
    prog = []
    global codeAddrCounter
    no = []#"LW", ]#"SW", ]
    if inst2 =="JALR" and (r1=="x0" or dest=="x0"):return
    if inst2 =="JAL" and (r1=="x0" or dest=="x0"):return
    if (inst2=="SW" or inst2=="LW") and (dest=="x1" or r1=="x1"):return
    if inst1 =="JALR" and r1=="x0":return
    if inst2 =="JAL" and r1=="x0":return
    if (inst1=="SW" or inst1=="LW") and (dest=="x1" or r1=="x1"):return
    ret = firstPart(inst1, dest, r1, r2)
    if len(ret) !=0:
        data1, data2 = [], []
        param1, param2, param3, part1 = ret[0], ret[1], ret[2], ret[3]
        if inst1 =="LW":
            data1 = ret[4]

        codeAddrCounter+=(len(part1)*4)
        prog.extend(part1)
        part2 = secondPart(inst2, param1, param2, param3)
        if len(part2) != 0:

            # if inst2 =="LW":
            #     data2 = part2[1]
            #     part2 = part2[0]
            prog.extend(part2)
            # if len(data1) !=0 and len(data2) !=0:
            #     data = []
            #     data.extend(data1)
            #     data2.pop(0)
            #     data.extend(data2)
            #     prog.extend(data)
            # elif len(data1) ==0 and len(data2) !=0:
            #     prog.extend(data2)
            # elif len(data1) !=0 and len(data2) == 0:
            #     prog.extend(data1)

            if inst1 in no or inst2 in no:
                os.makedirs(os.path.dirname(f"./tests/{inst1}-{inst2}/{dest}-{r1}-{r2}.txt"), exist_ok=True)
                f = open(f"./tests/{inst1}-{inst2}/{dest}-{r1}-{r2}.txt","w")
                f.write("\n".join(prog))
                f.close()
            else:
                os.makedirs(os.path.dirname(f"./tests/{inst1}-{inst2}.txt"), exist_ok=True)
                f = open(f"./tests/{inst1}-{inst2}.txt","a")
                f.write("\n".join(prog))
                f.write("\n")
                f.close()
            # if lastInst2 != inst2 and (inst1=="SW" or lastInst2=="SW") and lastInst2 != None and inst1 != "LW" and lastInst2!="LW":
            #     f = open(f"./tests/{inst1}-{lastInst2}.txt", "a")
            #     f.write(".data\n")
            #     for i in range(0x3FF):
            #         f.write(".word 0xFFFFFFFF\n")
            #     f.close()
        codeAddrCounter+=(len(part2)*4)
def exhTwoInst():
    global codeAddrCounter
    global dataAddrCounter
    global lastInst2
    for inst1 in instruction_list:
        if inst1 != "SW" : continue
        for inst2 in instruction_list:
            #if inst2 != "SW":continue
            if inst1 in RRR_INST:
                for dest in reg_list:
                    for r1 in reg_list:
                        for r2 in reg_list:
                            genProgram(inst1, inst2, dest, r1, r2)
            if inst1 in RR_INST:
                for dest in reg_list:
                    #if dest == "x0":continue
                    for r1 in reg_list:
                        #if r1 == "x0":continue
                        genProgram(inst1, inst2, dest, r1)
            if inst1 in R_INST:
                for dest in reg_list:
                    #if dest == "x0":continue
                    genProgram(inst1, inst2, dest)
            codeAddrCounter = 0x200
            dataAddrCounter = 0x0100000
            lastInst2 = inst2
s = {'dump_vcd': False, 'test_verilog': False,
    'max_cycles': 9999999, 'dump_vtb': ''}

def runTask(file):
    print(f"{file} starts")
    f = open(file, "r")
    try:
        p1 = time.perf_counter()
        run_test(s, ProcFL, f.read())
        print(time.perf_counter()-p1)
        print(f"{file} ends")
    except Exception as e:
        print(e)
        print(file)
    finally: f.close()

def getTasks():
    allTasks = []
    for root, dir, files in os.walk("./tests"):
        for fn in files:
            path = os.path.join(root, fn)
            allTasks.append(path)
    return allTasks

# try:
#     rmtree("./tests/")
# except:pass
# print("Gen Tests")
# exhTwoInst()
# print("Gen Done")

# for i in getTasks():
#     runTask(i)
# p1 = time.perf_counter()
# runTask("./tests/ADD-JALR.txt")
# print(time.perf_counter()-p1)

def runTaskNoOpen(test):
    try:
        run_test(s, ProcFL, test)
    except Exception as e:
        print(e)
        print(test)

from multiprocessing import Pool
if __name__ == "__main__":

    try:
        rmtree("./tests/")
    except:pass
    print("Gen Tests")
    exhTwoInst()
    print("Gen Done")

    p1 = time.perf_counter()
    p = Pool(multiprocessing.cpu_count())
    p.map(runTask, getTasks())
    print(time.perf_counter()-p1, "s")
