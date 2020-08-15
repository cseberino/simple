# Copyright 2020 Christian Seberino
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import re

REG       = "r1[0-5]|r[0-9]"
NAT       = "0x[0-9a-f]+|\d+"
R_AND_N   = "({})[+-]({})".format(REG, NAT)
LABEL     = "\w+"
STACK_PTR = "r1"
RET_PTR   = "r2"
RET_VAL   = "r3"
WORK      = ["r4", "r5", "r6", "r7"]
FUNC_LEN  = 8
SECT_LEN  = 18
BYTE_LEN  = 8
WORD_LEN  = 4
SECOND    = (STACK_PTR,     WORD_LEN)
THIRD     = (STACK_PTR, 2 * WORD_LEN)
NIBB_MASK = 2 ** (WORD_LEN * BYTE_LEN // 2) - 1
SIGNED    = 1 << (WORD_LEN * BYTE_LEN - 1)
NEG_ONE   = 0xffffffff
HEXDEC    = 16

labels     = []
if_labs    = []
while_labs = []

def parse_arg(arg):
        result = None
        if   re.fullmatch(REG, arg):
                result = arg
        elif re.fullmatch(NAT, arg):
                if arg.startswith("0x"):
                        result = int(arg, HEXDEC)
                else:
                        result = int(arg)
        elif re.fullmatch(R_AND_N, arg):
                reg = re.match(REG, arg).group(0)
                nat = arg[len(reg) + 1:]
                if nat.startswith("0x"):
                        nat = int(nat, HEXDEC)
                else:
                        nat = int(nat)
                if arg[len(reg)] == "-":
                        nat *= -1
                result = (reg, nat)
        elif re.fullmatch(LABEL, arg):
                result = [arg]

        return result

def parse_args(args):
        result = []
        index  = 0
        while index < len(args):
                if (index <= len(args) - 3) and (args[index + 1] in ["+", "-"]):
                        result.append(parse_arg("".join(args[index:index + 3])))
                        index += 3
                else:
                        result.append(parse_arg(args[index]))
                        index += 1

        return result

def line(func, *args):
        line_ = SECT_LEN * " " + func.ljust(FUNC_LEN)
        for e in args:
                line_ += str(e).ljust(SECT_LEN)
        line_ = line_.rstrip() + "\n"

        return line_

def new_label_gen():
        count = 1
        label = "_unique_{}".format(count)
        while True:
                while label in labels:
                        count += 1
                        label  = "_unique_{}".format(count)
                labels.append(label)
                yield [label]
new_label = lambda : next(new_label_gen())

def replace_(asm):
        result = ""
        for e in [e for e in asm.strip().split("\n") if e]:
                e_    = e.split()
                label = e_[0] if ":" in e_[0] else ""
                if label:
                        e_      = e_[1:]
                if (e_[0] == e_[0].upper()) and (e_[0] in globals()):
                        args    = parse_args(e_[1:])
                        result += label.ljust(SECT_LEN) + NOTH()[SECT_LEN:]
                        result += globals()[e_[0]](*args)
                else:
                        result += label.ljust(SECT_LEN) + line(*e_)[SECT_LEN:]

        return result

def replace(asm):
        labels.extend(re.findall("^{}:".format(LABEL), asm, re.MULTILINE))
        result = asm
        orig   = ""
        while result != orig:
                orig   = result
                result = replace_(orig)

        return result

def NOTH():
        return line("and", "r1", "r1", "r1")

def NEG(arg_1, arg_2):
        result  = NOT(arg_1, arg_2)
        result += ADD(arg_2, 1,    arg_2)

        return result

def arith_log_macro(func):
        def func_(arg_1, arg_2, arg_3):
                result  = COPY(arg_1, WORK[2])
                result += COPY(arg_2, arg_3)
                result += line(func,  WORK[2], arg_3, arg_3)

                return result

        return func_

for e in ["ADD", "SUB", "MULT", "DIV", "AND", "OR"]:
        globals()[e] = arith_log_macro(e.lower())

def MOD(arg_1, arg_2, arg_3):
        result  = PUSH(arg_1)
        result += PUSH(arg_2)
        result += DIV(arg_1,    arg_2, arg_3)
        result += POP(WORK[3])
        result += MULT(WORK[3], arg_3, arg_3)
        result += POP(WORK[3])
        result += SUB(WORK[3],  arg_3, arg_3)

        return result

def EXP(arg_1, arg_2, arg_3):
        result  = PUSH(arg_2)
        result += PUSH(arg_1)
        result += COPY(1,       arg_3)
        result += LOAD(SECOND,  WORK[3])
        result += WHILE(WORK[3])
        result += AND(WORK[3],  1,       WORK[3])
        result += IF(WORK[3])
        result += POP(WORK[3])
        result += MULT(arg_3,   WORK[3], arg_3)
        result += PUSH(WORK[3])
        result += ENDIF()
        result += LOAD(SECOND,  WORK[3])
        result += PUSH(arg_3)
        result += DIV(WORK[3],  2,       arg_3)
        result += STORE(arg_3,  THIRD)
        result += POP(arg_3)
        result += POP(WORK[3])
        result += MULT(WORK[3], WORK[3], WORK[3])
        result += PUSH(WORK[3])
        result += LOAD(SECOND,  WORK[3])
        result += ENDWHILE()
        result += POP(WORK[3])
        result += POP(WORK[3])

        return result

def NOT(arg_1, arg_2):
        result  = COPY(arg_1, arg_2)
        result += MULT(arg_2, NEG_ONE, arg_2)
        result += SUB(arg_2,  1,       arg_2)

        return result

def XOR(arg_1, arg_2, arg_3):
        result  = OR(arg_1,    arg_2,   WORK[3])
        result += PUSH(WORK[3])
        result += NOT(arg_1,   WORK[3])
        result += NOT(arg_2,   arg_3)
        result += OR(WORK[3],  arg_3,   WORK[3])
        result += POP(arg_3)
        result += AND(arg_3,   WORK[3], arg_3)

        return result

def LSHIFT(arg_1, arg_2, arg_3):
        result  = COPY(arg_1,   WORK[3])
        result += COPY(arg_2,   arg_3)
        result += WHILE(arg_3)
        result += MULT(WORK[3], 2,      WORK[3])
        result += SUB(arg_3,    1,      arg_3)
        result += ENDWHILE()
        result += COPY(WORK[3], arg_3)

        return result

def RSHIFT(arg_1, arg_2, arg_3):
        result  = COPY(arg_1,   WORK[3])
        result += COPY(arg_2,   arg_3)
        result += WHILE(arg_3)
        result += DIV(WORK[3],  2,      WORK[3])
        result += SUB(arg_3,    1,      arg_3)
        result += ENDWHILE()
        result += COPY(WORK[3], arg_3)

        return result

def JUMP(arg_1):
        result  = COPY(arg_1,   WORK[2])
        result += COPY(0,       WORK[0])
        result += line("zjump", WORK[0], WORK[2])

        return result

def GJUMP(arg_1, arg_2, arg_3):
        result  = SUB(arg_2,    arg_1,   WORK[3])
        result += DIV(WORK[3],  SIGNED,  WORK[3])
        result += SUB(WORK[3],  1,       WORK[3])
        result += COPY(arg_3,   WORK[2])
        result += line("zjump", WORK[3], WORK[2])

        return result

def GEJUMP(arg_1, arg_2, arg_3):
        result  = SUB(arg_1,    arg_2,   WORK[3])
        result += DIV(WORK[3],  SIGNED,  WORK[3])
        result += COPY(arg_3,   WORK[2])
        result += line("zjump", WORK[3], WORK[2])

        return result

LJUMP  = lambda arg_1, arg_2, arg_3 : GJUMP(arg_2,  arg_1, arg_3)

LEJUMP = lambda arg_1, arg_2, arg_3 : GEJUMP(arg_2, arg_1, arg_3)

def ZJUMP(arg_1, arg_2):
        result  = COPY(arg_1,   WORK[2])
        result += COPY(arg_2,   WORK[3])
        result += line("zjump", WORK[2], WORK[3])

        return result

def NZJUMP(arg_1, arg_2):
        result  = COPY(arg_1,       WORK[2])
        result += COPY(new_label(), WORK[3])
        result += line("zjump",     WORK[2], WORK[3])
        result += COPY(arg_2,       WORK[2])
        result += JUMP(WORK[2])
        result += (labels[-1] + ":").ljust(SECT_LEN) + NOTH()[SECT_LEN:]

        return result

def EJUMP(arg_1, arg_2, arg_3):
        result  = SUB(arg_1,    arg_2,   WORK[3])
        result += COPY(arg_3,   WORK[2])
        result += line("zjump", WORK[3], WORK[2])

        return result

def NEJUMP(arg_1, arg_2, arg_3):
        result  = SUB(arg_1,        arg_2,   WORK[3])
        result += COPY(new_label(), WORK[2])
        result += line("zjump",     WORK[3], WORK[2])
        result += COPY(arg_3,       WORK[3])
        result += JUMP(WORK[3])
        result += (labels[-1] + ":").ljust(SECT_LEN) + NOTH()[SECT_LEN:]

        return result

def COPY(arg_1, arg_2):
        if   isinstance(arg_1, str):
                result  = line("and",   arg_1,         arg_1,   arg_2)
        elif isinstance(arg_1, int):
                lsb     = arg_1  & NIBB_MASK
                msb     = arg_1 >> (WORD_LEN * BYTE_LEN // 2)
                result  = line("copy",  lsb,           arg_2)
                result += line("copy",  msb,           WORK[0])
                result += line("copy",  NIBB_MASK + 1, WORK[1])
                result += line("mult",  WORK[0],       WORK[1], WORK[0])
                result += line("add",   arg_2,         WORK[0], arg_2)
        elif isinstance(arg_1, tuple):
                result  = COPY(abs(arg_1[1]), arg_2)
                if arg_1[1] >= 0:
                        result += line("add", arg_1[0], arg_2, arg_2)
                else:
                        result += line("sub", arg_1[0], arg_2, arg_2)
        elif isinstance(arg_1, list):
                result  = line("and",   "r0",          "r0",    arg_2)
                result += line("copy",  "32",          WORK[0])
                result += line("copy",  "4",           WORK[1])
                result += line("add",   arg_2,         WORK[0], WORK[0])
                result += line("add",   WORK[0],       WORK[1], WORK[1])
                result += line("load",  WORK[0],       arg_2)
                result += line("copy",  "0",           WORK[0])
                result += line("zjump", WORK[0],       WORK[1])
                result += line(arg_1[0])

        return result

def LOAD(arg_1, arg_2):
        result  = COPY(arg_1,  arg_2)
        result += line("load", arg_2, arg_2)

        return result

def STORE(arg_1, arg_2):
        result  = COPY(arg_1,   WORK[2])
        result += COPY(arg_2,   WORK[3])
        result += line("store", WORK[2], WORK[3])

        return result

def PUSH(arg_1):
        result  = SUB(STACK_PTR, WORD_LEN, STACK_PTR)
        result += COPY(arg_1,    WORK[2])
        result += line("store",  WORK[2],  STACK_PTR)

        return result

def POP(arg_1):
        result  = LOAD(STACK_PTR, arg_1)
        result += ADD(STACK_PTR,  WORD_LEN, STACK_PTR)

        return result

def CALL(*args):
        result  = PUSH(new_label())
        for e in reversed(args[1:]):
                result += PUSH(e)
        result += JUMP(args[0])
        result += (labels[-1] + ":").ljust(SECT_LEN) + NOTH()[SECT_LEN:]

        return result

def RETURN(arg_1 = False):
        result  = COPY(arg_1, RET_VAL) if arg_1 else ""
        result += POP(RET_PTR)
        result += JUMP(RET_PTR)

        return result

def IF(*args):
        if isinstance(args[0], list):
                result = CALL(*args)
        else:
                result = COPY(args[0], RET_VAL)
        if_labs.append(new_label())
        result += COPY(if_labs[-1], WORK[2])
        result += line("zjump",     RET_VAL, WORK[2])

        return result

def ENDIF():
        return (if_labs.pop()[0] + ":").ljust(SECT_LEN) + NOTH()[SECT_LEN:]

def WHILE(*args):
        while_labs.append(new_label())
        result  = (while_labs[-1][0] + ":").ljust(SECT_LEN) + NOTH()[SECT_LEN:]
        result += IF(*args)

        return result

def ENDWHILE():
        result  = JUMP(while_labs.pop())
        result += ENDIF()

        return result
