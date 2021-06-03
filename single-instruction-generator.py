import multiprocessing
from FL.tinyrv2_semantics import zext
from pymtl3 import *
from FL.ProcFL import ProcFL
from RTL.ProcRTL import ProcRTL
from harness import *
import struct
import numpy as np
import random
import time
instruction_list = [
    "ADD", "ADDI", "SUB", "MUL",
    "AND", "ANDI", "OR", "ORI", "XOR", "XORI",
    "SLT", "SLTI", "SLTU", "SLTIU",
    "SRA", "SRAI", "SRL", "SRLI", "SLL", "SLLI",
    "LUI", "AUIPC",
    "LW", "SW",
    "JAL", "JALR",
    "BEQ", "BNE", "BLT", "BGE", "BLTU", "BGEU",
    #"CSRR", "CSRW"  # (proc2mngr, mngr2proc, stats_en, core_id, num_cores)
]
reg_list = [
    "x0", "x1", "x2", "x3", "x4", "x5", "x6", "x7", "x8", "x9",
    "x10", "x11", "x12", "x13", "x14", "x15", "x16", "x17", "x18", "x19",
    "x20", "x21", "x22", "x23", "x24", "x25", "x26", "x27", "x28", "x29",
    "x30", "x31"
]


def gen_rs1_rs2_val(r1, r2):
    rs1, rs2 = 0, 0
    if r1 != "x0":
        rs1 = struct.unpack("<i", np.random.bytes(4))[0]
    if r2 != "x0":
        rs2 = struct.unpack("<i", np.random.bytes(4))[0]
    if r1 == r2:
        rs1 = rs2
    return (rs1, rs2)


def gen_rr_code(opcode, dest, r1, r2, val1, val2, expect):
    tmp = []
    tmp.extend([f"csrr {r1}, mngr2proc < {val1}",
               f"csrr {r2}, mngr2proc < {val2}"])  # Init RS1 and RS2
    tmp.append(f"{opcode} {dest},{r1},{r2}")
    if dest == "x0":  # Destination x0 Test
        tmp.append("csrw proc2mngr, x0 > 0")
    else:
        tmp.append(f"csrw proc2mngr, {dest} > {expect}")
    return tmp


def gen_rs1_imme_val(rs1):
    v1, v2 = Bits32(0), Bits12(0)
    if rs1 != "x0":
        v1 = Bits32(struct.unpack("<i", np.random.bytes(4))[0])
    v2 = trunc(Bits32(struct.unpack("<i", np.random.bytes(4))[0]), 12)
    return (v1, v2)


def gen_ri_code(opcode, dest, r1, val1, val2, expect):
    tmp = []
    tmp.append(f"csrr {r1}, mngr2proc < {val1.int()}")
    tmp.append(f"{opcode} {dest},{r1},{val2.int()}")
    if dest == "x0":  # Destination x0 Test
        tmp.append("csrw proc2mngr, x0 > 0")
    else:
        tmp.append(f"csrw proc2mngr, {dest} > {expect.int()}")
    return tmp


def exhOneInst():
    def rshift(val, n): return val>>n if val >= 0 else (val+0x100000000)>>n
    tests = []
    for inst in instruction_list:
        tmp = []
        if inst == "ADD":
            #continue
            for dest in reg_list:
                for rs1 in reg_list:
                    for rs2 in reg_list:
                        v1, v2 = gen_rs1_rs2_val(rs1, rs2)
                        result = 0xFFFFFFFF & (v1+v2)
                        tmp.extend(gen_rr_code(
                            "add", dest, rs1, rs2, v1, v2, result))

        elif inst == "ADDI":
            #continue
            for dest in reg_list:
                for rs1 in reg_list:
                    v1, v2 = gen_rs1_imme_val(rs1)
                    result = v1+sext(v2, 32)
                    tmp.extend(gen_ri_code("addi", dest, rs1, v1, v2, result))

        elif inst == "SUB":
            #continue
            for dest in reg_list:
                for rs1 in reg_list:
                    for rs2 in reg_list:
                        v1, v2 = gen_rs1_rs2_val(rs1, rs2)
                        result = 0xFFFFFFFF & (v1-v2)
                        tmp.extend(gen_rr_code(
                            "sub", dest, rs1, rs2, v1, v2, result))

        elif inst == "MUL":
            #continue
            for dest in reg_list:
                for rs1 in reg_list:
                    for rs2 in reg_list:
                        v1, v2 = gen_rs1_rs2_val(rs1, rs2)
                        result = 0xFFFFFFFF & (v1*v2)
                        tmp.extend(gen_rr_code(
                            "mul", dest, rs1, rs2, v1, v2, result))
        elif inst == "AND":
            #continue
            for dest in reg_list:
                for rs1 in reg_list:
                    for rs2 in reg_list:
                        v1, v2 = gen_rs1_rs2_val(rs1, rs2)
                        result = 0xFFFFFFFF & (v1 & v2)
                        tmp.extend(gen_rr_code(
                            "and", dest, rs1, rs2, v1, v2, result))
        elif inst == "ANDI":
            #continue
            for dest in reg_list:
                for rs1 in reg_list:
                    v1, v2 = gen_rs1_imme_val(rs1)
                    result = v1 & sext(v2, 32)
                    tmp.extend(gen_ri_code("andi", dest, rs1, v1, v2, result))
        elif inst=="OR":
            #continue
            for dest in reg_list:
                for rs1 in reg_list:
                    for rs2 in reg_list:
                        v1, v2 = gen_rs1_rs2_val(rs1, rs2)
                        result = 0xFFFFFFFF & (v1|v2)
                        tmp.extend(gen_rr_code(
                            "or", dest, rs1, rs2, v1, v2, result))
        elif inst=="ORI":
            #continue
            for dest in reg_list:
                for rs1 in reg_list:
                    v1, v2 = gen_rs1_imme_val(rs1)
                    result = v1 | sext(v2, 32)
                    tmp.extend(gen_ri_code("ori", dest, rs1, v1, v2, result))
        elif inst=="XOR":
            #continue
            for dest in reg_list:
                for rs1 in reg_list:
                    for rs2 in reg_list:
                        v1, v2 = gen_rs1_rs2_val(rs1, rs2)
                        result = 0xFFFFFFFF & (v1^v2)
                        tmp.extend(gen_rr_code(
                            "xor", dest, rs1, rs2, v1, v2, result))
        elif inst=="XORI":
            #continue
            for dest in reg_list:
                for rs1 in reg_list:
                    v1, v2 = gen_rs1_imme_val(rs1)
                    result = v1 ^ sext(v2, 32)
                    tmp.extend(gen_ri_code("xori", dest, rs1, v1, v2, result))
        elif inst=="SLT":
            #continue
            for dest in reg_list:
                for rs1 in reg_list:
                    for rs2 in reg_list:
                        v1, v2 = gen_rs1_rs2_val(rs1, rs2)
                        result = int(v1 < v2)
                        tmp.extend(gen_rr_code("slt", dest, rs1, rs2, v1, v2, result))
        elif inst=="SLTI":
            #continue
            for dest in reg_list:
                for rs1 in reg_list:
                    v1, v2 = gen_rs1_imme_val(rs1)
                    result = Bits32(int(v1.int() < sext(v2, 32).int()))
                    tmp.extend(gen_ri_code("slti", dest, rs1, v1, v2, result))
        elif inst=="SLTU":
            #continue
            for dest in reg_list:
                for rs1 in reg_list:
                    for rs2 in reg_list:
                        v1, v2 = gen_rs1_rs2_val(rs1, rs2)
                        v1 = np.uint32(np.int32(v1))
                        v2 = np.uint32(np.int32(v2))
                        result = int(v1 < v2)
                        tmp.extend(gen_rr_code("sltu", dest, rs1, rs2, v1, v2, result))
        elif inst=="SLTIU":
            #continue
            for dest in reg_list:
                for rs1 in reg_list:
                    v1, v2 = gen_rs1_imme_val(rs1)
                    result = Bits32(int(v1.uint() < sext(v2, 32).uint()))
                    tmp.extend(gen_ri_code("sltiu", dest, rs1, v1, v2, result))
        elif inst=="SRA":
            #continue
            for dest in reg_list:
                for rs1 in reg_list:
                    for rs2 in reg_list:
                        #tmp = []
                        v1, v2 = gen_rs1_rs2_val(rs1, rs2)
                        v2 &= 0x1F
                        if rs1 == rs2: v1 = v2
                        result = v1>>v2
                        tmp.extend(gen_rr_code("sra", dest, rs1, rs2, v1, v2, result))
                        #yield "\n".join(tmp)
        elif inst=="SRAI":
            #continue
            for dest in reg_list:
                for rs1 in reg_list:
                    v1, v2 = gen_rs1_imme_val(rs1)
                    result = Bits32(int(v1.int() >> (sext(v2, 32).uint()& 0x1F)))
                    tmp.extend(gen_ri_code("srai", dest, rs1, v1, v2& Bits12(0x1F), result))
        elif inst=="SRL":
            #continue
            for dest in reg_list:
                for rs1 in reg_list:
                    for rs2 in reg_list:
                        #tmp = []
                        v1, v2 = gen_rs1_rs2_val(rs1, rs2)
                        v2 &= 0x1F
                        if rs1 == rs2: v1 = v2
                        result = rshift(v1, v2)
                        tmp.extend(gen_rr_code("srl", dest, rs1, rs2, v1, v2, result))
                        #yield "\n".join(tmp)
        elif inst=="SRLI":
            #continue
            for dest in reg_list:
                for rs1 in reg_list:
                    #tmp = []
                    v1, v2 = gen_rs1_imme_val(rs1)
                    result = Bits32(rshift(v1.int(), (v2.uint()& 0x1F)))
                    tmp.extend(gen_ri_code("srli", dest, rs1, v1, v2& Bits12(0x1F), result))
                    #yield "\n".join(tmp)
        elif inst=="SLL":
            #continue
            for dest in reg_list:
                for rs1 in reg_list:
                    for rs2 in reg_list:
                        #tmp = []
                        v1, v2 = gen_rs1_rs2_val(rs1, rs2)
                        v2 &= 0x1F
                        if rs1 == rs2: v1 = v2
                        result = (v1<<v2)&0xFFFFFFFF
                        tmp.extend(gen_rr_code("sll", dest, rs1, rs2, v1, v2, result))
                        #yield "\n".join(tmp)
        elif inst=="SLLI":
            #continue
            for dest in reg_list:
                for rs1 in reg_list:
                    #tmp = []
                    v1, v2 = gen_rs1_imme_val(rs1)
                    result = v1<< zext(v2&Bits12(0x1F), 32)
                    tmp.extend(gen_ri_code("slli", dest, rs1, v1, v2& Bits12(0x1F), result))
                    #yield "\n".join(tmp)
        elif inst=="LUI":
            #continue
            for dest in reg_list:
                imme = struct.unpack("<i", np.random.bytes(4))[0]&0b1111_1111_1111_1111_1111
                result = int(hex(imme)+"000", 16)
                tmp.append(f"lui {dest}, {imme}")
                if dest == "x0":  # Destination x0 Test
                    tmp.append("csrw proc2mngr, x0 > 0")
                else: tmp.append(f"csrw proc2mngr, {dest} > {result}")
        elif inst=="AUIPC":
            #continue
            pc = 0x200
            for dest in reg_list:
                imme = struct.unpack("<i", np.random.bytes(4))[0]&0b1111_1111_1111_1111_1111
                result = int(hex(imme)+"000", 16)
                tmp.append(f"auipc {dest}, {imme}")
                pc+=4
                if dest == "x0":  # Destination x0 Test
                    tmp.append("csrw proc2mngr, x0 > 0")
                else: tmp.append(f"csrw proc2mngr, {dest} > {pc-4+result}")
                pc+=4
        elif inst=="LW":
            #continue
            for dest in reg_list:
                for r1 in reg_list:
                    singleTest = []
                    randOffset = struct.unpack("<i", np.random.bytes(4))[0]&0b1111
                    randWord = "0x"+np.random.bytes(4).hex()
                    singleTest.append(f"csrr {r1}, mngr2proc < 0x00002000")
                    singleTest.append(f"lw   {dest}, {randOffset}({r1})")
                    if dest=="x0":singleTest.append("csrw proc2mngr, x0 > 0")
                    elif r1=="x0":singleTest.append(f"csrw proc2mngr, {dest} > 0")
                    else :singleTest.append(f"csrw proc2mngr, {dest} > {randWord}")
                    singleTest.append(".data")
                    for i in range(randOffset):
                        singleTest.append(".byte 0xFF")
                    singleTest.append(f".word {randWord}")
                    tmp.append("\n".join(singleTest))
        elif inst=="SW":
            #continue
            for dest in reg_list:
                if dest=="x0" or dest=="x1":continue
                for r1 in reg_list:
                    if r1=="x0" or r1=="x1":continue
                    singleTest = []
                    randOffset = struct.unpack("<i", np.random.bytes(4))[0]&0b1111
                    randWord = "0x"+np.random.bytes(4).hex()
                    singleTest.append(f"csrr x1, mngr2proc < 0x00002000")
                    singleTest.append(f"csrr {r1}, mngr2proc < {randWord}")
                    singleTest.append(f"sw   {r1}, {randOffset}(x1)")
                    singleTest.append(f"lw   {dest}, {randOffset}(x1)")
                    singleTest.append(f"csrw proc2mngr, {dest} > {randWord}")
                    singleTest.append(".data")
                    for i in range(randOffset):
                        singleTest.append(".byte 0xFF")
                    singleTest.append(f".word 0xC0FEBABE")
                    tmp.append("\n".join(singleTest))
        elif inst=="JAL":
            #continue
            for dest in reg_list:
                singleTest = []
                r = random.randint(0, 10)
                singleTest.append(f"jal {dest}, label_a")
                for i in range(r):
                    singleTest.append(f"add {dest}, {dest}, {dest}")#Non jmp hit
                singleTest.append(f"label_a:")
                if dest == "x0":singleTest.append(f"csrw  proc2mngr, {dest} > 0")
                else:singleTest.append(f"csrw  proc2mngr, {dest} > 0x204")
                tmp.append("\n".join(singleTest))
        elif inst=="JALR":
            #continue
            for dest in reg_list:
                for base in reg_list:
                    if base == "x0": continue
                    singleTest = []
                    r = random.randint(0, 10)
                    singleTest.append(f"csrr  {base}, mngr2proc < 0x200")#200
                    singleTest.append(f"jalr  {dest}, {base}, {(r+2)*4}")#204
                    for i in range(r):
                        singleTest.append(f"add {dest}, {dest}, {dest}")#Non jmp hit
                    if dest == "x0":singleTest.append(f"csrw  proc2mngr, {dest} > 0")# At least 208
                    else:singleTest.append(f"csrw  proc2mngr, {dest} > 0x208")
                    tmp.append("\n".join(singleTest))
        #"BEQ", "BNE", "BLT", "BGE", "BLTU", "BGEU",
        elif inst == "BEQ":
            #continue
            for r1 in reg_list:
                if r1=="x0":continue
                for r2 in reg_list:
                    if r2=="x0":continue
                    v1, v2 = gen_rs1_rs2_val(r1, r2)
                    #tmp = []
                    tmp.append(f"csrr  {r1}, mngr2proc < {v1}")
                    tmp.append(f"csrr  {r2}, mngr2proc < {v2}")
                    tmp.append(f"beq {r1},{r2}, 8")
                    tmp.append(f"addi {r1},{r2},{-1}")#Hit test
                    if v1==v2:tmp.append(f"csrw  proc2mngr, {r1} > {v1}")
                    else: tmp.append(f"csrw  proc2mngr, {r1} > {v2-1}")
                    #yield "\n".join(tmp)
        elif inst == "BNE":
            #continue
            for r1 in reg_list:
                if r1=="x0":continue
                for r2 in reg_list:
                    if r2=="x0":continue
                    v1, v2 = gen_rs1_rs2_val(r1, r2)
                    #tmp = []
                    tmp.append(f"csrr  {r1}, mngr2proc < {v1}")
                    tmp.append(f"csrr  {r2}, mngr2proc < {v2}")
                    tmp.append(f"bne {r1},{r2}, 8")
                    tmp.append(f"addi {r1},{r2},{-1}")#Hit test
                    if v1!=v2:tmp.append(f"csrw  proc2mngr, {r1} > {v1}")
                    else: tmp.append(f"csrw  proc2mngr, {r1} > {v2-1}")
                    #yield "\n".join(tmp)
        elif inst == "BLT":
            #continue
            for r1 in reg_list:
                if r1=="x0":continue
                for r2 in reg_list:
                    if r2=="x0":continue
                    v1, v2 = gen_rs1_rs2_val(r1, r2)
                    #tmp = []
                    tmp.append(f"csrr  {r1}, mngr2proc < {v1}")
                    tmp.append(f"csrr  {r2}, mngr2proc < {v2}")
                    tmp.append(f"blt {r1},{r2}, 8")
                    tmp.append(f"addi {r1},{r2},{-1}")#Hit test
                    if v1<v2:tmp.append(f"csrw  proc2mngr, {r1} > {v1}")
                    else: tmp.append(f"csrw  proc2mngr, {r1} > {v2-1}")
                    #yield "\n".join(tmp)
        elif inst == "BGE":
            #continue
            for r1 in reg_list:
                if r1=="x0":continue
                for r2 in reg_list:
                    if r2=="x0":continue
                    v1, v2 = gen_rs1_rs2_val(r1, r2)
                    #tmp = []
                    tmp.append(f"csrr  {r1}, mngr2proc < {v1}")
                    tmp.append(f"csrr  {r2}, mngr2proc < {v2}")
                    tmp.append(f"bge {r1},{r2}, 8")
                    tmp.append(f"addi {r1},{r2},{-1}")#Hit test
                    if v1>=v2:tmp.append(f"csrw  proc2mngr, {r1} > {v1}")
                    else: tmp.append(f"csrw  proc2mngr, {r1} > {v2-1}")
                    #yield "\n".join(tmp)
        elif inst == "BLTU":
            #continue
            for r1 in reg_list:
                if r1=="x0":continue
                for r2 in reg_list:
                    if r2=="x0":continue
                    v1, v2 = gen_rs1_rs2_val(r1, r2)
                    v1 = np.uint32(v1)
                    v2 = np.uint32(v2)
                    #tmp = []
                    tmp.append(f"csrr  {r1}, mngr2proc < {v1}")
                    tmp.append(f"csrr  {r2}, mngr2proc < {v2}")
                    tmp.append(f"bltu {r1},{r2}, 8")
                    tmp.append(f"addi {r1},{r2},{-1}")#Hit test
                    if v1<v2:tmp.append(f"csrw  proc2mngr, {r1} > {v1}")
                    else: tmp.append(f"csrw  proc2mngr, {r1} > {np.int32(v2-1)}")
                    #yield "\n".join(tmp)
        elif inst == "BGEU":
            #continue
            for r1 in reg_list:
                if r1=="x0":continue
                for r2 in reg_list:
                    if r2=="x0":continue
                    v1, v2 = gen_rs1_rs2_val(r1, r2)
                    v1 = np.uint32(v1)
                    v2 = np.uint32(v2)
                    #tmp = []
                    tmp.append(f"csrr  {r1}, mngr2proc < {v1}")
                    tmp.append(f"csrr  {r2}, mngr2proc < {v2}")
                    tmp.append(f"bgeu {r1},{r2}, 8")
                    tmp.append(f"addi {r1},{r2},{-1}")#Hit test
                    if v1>=v2:tmp.append(f"csrw  proc2mngr, {r1} > {v1}")
                    else: tmp.append(f"csrw  proc2mngr, {r1} > {np.int32(v2-1)}")
                    #yield "\n".join(tmp)
        if inst!="LW" and inst!="SW" and inst!="JAL" and inst!="JALR":
            tests.append((ProcRTL, (inst, "\n".join(tmp))))
        else: tests.append((ProcRTL,(inst, tmp)))
    return tuple(tests)

def test(params):
    model, t = params[0], params[1]
    #print(model)
    s = {'dump_vcd': False, 'test_verilog': False,
         'max_cycles': 9999999, 'dump_vtb': ''}
    # p = time.perf_counter()
    # tests = exhOneInst()
    # print(f"Took {time.perf_counter()-p}s to generate all testcases\n")
    
    #for t in tests:
    p = time.perf_counter()
    if isinstance(t[1], str):
        try:
            run_test(s, model, t[1])
        except Exception as e:
            print(e)
            print(t[0])
    elif isinstance(t[1], list):
        for single in t[1]:
            try:
                run_test(s, model, single)
            except Exception as e:
                print(e)
                print(t[0])
    print(f"Took {time.perf_counter()-p}s to run {t[0]} testcases")
    
def singleTest():
    for dest in reg_list:
        for rs1 in reg_list:
            for rs2 in reg_list:
                tmp = []
                v1, v2 = gen_rs1_rs2_val(rs1, rs2)
                v2 &= 0x1F
                if rs1 == rs2: v1 = v2
                result = (v1<<v2)&0xFFFFFFFF
                tmp.extend(gen_rr_code("sll", dest, rs1, rs2, v1, v2, result))
                yield "\n".join(tmp)
def tmp(model):
    a = '''
csrr x1, mngr2proc < 1048576
csrr x31, mngr2proc < 0x84d23094
sw   x31, 9(x1)
lw   x1, 9(x1)
csrr x1, mngr2proc < 1048576
csrr x1, mngr2proc < 0x2474dcf2
sw   x1, 6(x1)
lw   x31, 6(x1)
csrw proc2mngr, x31 > 0x2474dcf2
    '''
    run_test(None, model, a)

from multiprocessing import Pool

def divideWork(works):
    cores = multiprocessing.cpu_count()
    singleWork = int(len(works)/cores)
    remainder = len(works) % cores
    acc = 0
    for i in range(cores):
        work = singleWork
        if remainder != 0:
            work+=1
            remainder-=1
        yield works[acc:acc+work]
        acc+=work

random.seed(0x11223344)
testMode = 99
tmp(ProcFL)
if testMode==2:
    for i in singleTest():
        s = {'dump_vcd': False, 'test_verilog': False,
            'max_cycles': 9999999, 'dump_vtb': ''}
        try:
            run_test(s, ProcFL, i)
        except Exception as e:
            print(e)
            print(i)
            break

if __name__ == "__main__":  # confirms that the code is under main function
    if testMode==1:
        
        p = time.perf_counter()
        tests = exhOneInst()
        print(f"Took {time.perf_counter()-p}s to generate all testcases")
        
        procs = []

        p_total = time.perf_counter()
        # for work in divideWork(tests):
        #     proc = Process(target=test, args=(ProcRTL, work))
        #     procs.append(proc)
        #     proc.start()
        
        
        # for proc in procs:
        #     proc.join()
        p = Pool(multiprocessing.cpu_count())
        p.map(test, tests)
        #p.join()
        print(f"Took total of {time.perf_counter()-p_total}s to run all the testcase")