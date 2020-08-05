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

REG        = "r1[0-5]|r[0-9]"
NAT        = "0x[0-9a-f]+|\d+"
R_AND_N    = "({})[+-]({})".format(REG, NAT)
LABEL      = "\w+"
WS         = ["r7", "r8", "r9", "r10"]
STACK_BASE = 0x00000400
STACK_PTR  = "r1"
SECT_LEN   = 18
FUNC_LEN   =  8
HALFW_LEN  = 16
WORD_LEN   =  4
HEXDEC     = 16

labels      = []
label_count = 0

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

def new_label():
        global label_count

        label_count += 1
        label        = "_unique_{}".format(label_count)
        while label in labels:
                label_count += 1
                label        = "_unique_{}".format(label_count)
        labels.append(label)

        return label

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
        result = asm
        orig   = ""
        while result != orig:
                orig   = result
                result = replace_(orig)

        return result

def NOTH():
        return line("and", "r1", "r1", "r1")

def arith_log_macro(func):
        def func_(arg_1, arg_2, arg_3):
                result  = COPY(arg_1, arg_3)
                result += COPY(arg_2, WS[2])
                result += line(func,  arg_3, WS[2], arg_3)

                return result

        return func_

for e in ["ADD", "SUB", "MULT", "DIV", "AND", "OR"]:
        globals()[e] = arith_log_macro(e.lower())

def NOT(arg_1, arg_2):
        result  = COPY(arg_1, arg_2)
        result += MULT(arg_2, 0xffffffff, arg_2)
        result += SUB(arg_2,  0x1,        arg_2)

        return result

def JUMP(arg_1):
        result  = COPY(arg_1,   WS[2])
        result += COPY(0,       WS[0])
        result += line("zjump", WS[0], WS[2])

        return result

def GJUMP(arg_1, arg_2, arg_3):
        result  = SUB(arg_2,    arg_1,                    WS[3])
        result += DIV(WS[3],    1 << (2 * HALFW_LEN - 1), WS[3])
        result += SUB(WS[3],    0x1,                      WS[3])
        result += COPY(arg_3,   WS[2])
        result += line("zjump", WS[3],                    WS[2])

        return result

def GEJUMP(arg_1, arg_2, arg_3):
        result  = SUB(arg_1,    arg_2,                    WS[3])
        result += DIV(WS[3],    1 << (2 * HALFW_LEN - 1), WS[3])
        result += COPY(arg_3,   WS[2])
        result += line("zjump", WS[3],                    WS[2])

        return result

LJUMP  = lambda arg_1, arg_2, arg_3 : GJUMP(arg_2,  arg_1, arg_3)

LEJUMP = lambda arg_1, arg_2, arg_3 : GEJUMP(arg_2, arg_1, arg_3)

def ZJUMP(arg_1, arg_2):
        result  = COPY(arg_1,   WS[2])
        result += COPY(arg_2,   WS[3])
        result += line("zjump", WS[2], WS[3])

        return result

def NZJUMP(arg_1, arg_2):
        result  = COPY(arg_1,         WS[2])
        result += COPY([new_label()], WS[3])
        result += line("zjump",       WS[2], WS[3])
        result += COPY(arg_2,         WS[2])
        result += JUMP(WS[2])
        result += (labels[-1] + ":").ljust(SECT_LEN) + NOTH()[SECT_LEN:]

        return result

def EJUMP(arg_1, arg_2, arg_3):
        result  = SUB(arg_1,    arg_2, WS[3])
        result += COPY(arg_3,   WS[2])
        result += line("zjump", WS[3], WS[2])

        return result

def NEJUMP(arg_1, arg_2, arg_3):
        result  = SUB(arg_1,          arg_2, WS[3])
        result += COPY([new_label()], WS[2])
        result += line("zjump",       WS[3], WS[2])
        result += COPY(arg_3,         WS[3])
        result += JUMP(WS[3])
        result += (labels[-1] + ":").ljust(SECT_LEN) + NOTH()[SECT_LEN:]

        return result

def COPY(arg_1, arg_2):
        if   isinstance(arg_1, str):
                result  = line("and",   arg_1,          arg_1, arg_2)
        elif isinstance(arg_1, int):
                lsb     = arg_1  & (2 ** HALFW_LEN - 1)
                msb     = arg_1 >> HALFW_LEN
                result  = line("copy",  lsb,            arg_2)
                result += line("copy",  msb,            WS[0])
                result += line("copy",  2 ** HALFW_LEN, WS[1])
                result += line("mult",  WS[0],          WS[1], WS[0])
                result += line("add",   arg_2,          WS[0], arg_2)
        elif isinstance(arg_1, tuple):
                result  = COPY(abs(arg_1[1]), arg_2)
                if arg_1[1] >= 0:
                        result += line("add", arg_1[0], arg_2, arg_2)
                else:
                        result += line("sub", arg_1[0], arg_2, arg_2)
        elif isinstance(arg_1, list):
                result  = line("and",   "r0",           "r0",  arg_2)
                result += line("copy",  "0x20",         WS[0])
                result += line("copy",  "0x4",          WS[1])
                result += line("add",   arg_2,          WS[0], WS[0])
                result += line("add",   WS[0],          WS[1], WS[1])
                result += line("load",  WS[0],          arg_2)
                result += line("copy",  "0x0",          WS[0])
                result += line("zjump", WS[0],          WS[1])
                result += line(arg_1[0])

        return result

def LOAD(arg_1, arg_2):
        result  = COPY(arg_1,  arg_2)
        result += line("load", arg_2, arg_2)

        return result

def STORE(arg_1, arg_2):
        result  = COPY(arg_1,   WS[2])
        result += COPY(arg_2,   WS[3])
        result += line("store", WS[2], WS[3])

        return result

def PUSH(arg_1):
        result  = SUB(STACK_PTR, WORD_LEN, STACK_PTR)
        result += STORE(arg_1,   STACK_PTR)

        return result

def POP(arg_1):
        result  = LOAD(STACK_PTR, arg_1)
        result += ADD(STACK_PTR,  WORD_LEN, STACK_PTR)

        return result
