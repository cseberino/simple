#!/usr/bin/env python3
#
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

import sys
sys.path.append("..")

import macros
import unittest
import subprocess
import importlib
import warnings

def get_code(program):
        open("__program__", "w").write(program)
        subprocess.call(["../assembler", "__program__"])
        code = open("__program__.mem", "rb").read()
        subprocess.call(["rm", "__program__", "__program__.mem"])

        return code

def get_output(program):
        open("__program__", "w").write(program)
        subprocess.call(["../assembler", "__program__"])
        output = subprocess.check_output(["../emulator", "__program__.mem"])
        subprocess.call(["rm", "__program__", "__program__.mem"])

        return output

def create_emu_mod():
        subprocess.call(["cp", "../emulator", "__emulator__.py"])
        contents = open("__emulator__.py").readlines()
        open("__emulator__.py", "w").write("".join(contents[:-13]))

class Tester(unittest.TestCase):
        def setUp(self):
                warnings.simplefilter("ignore", ResourceWarning)

        def test_add_assem(self):
                program = \
"""
add r2 r3 r4
add r6 r1 r2
"""
                output  = get_code(program)
                answer  = "02340000"
                answer += "06120000"
                answer  = bytes.fromhex(answer)
                self.assertEqual(output, answer)

        def test_sub_assem(self):
                program = \
"""
sub r2 r3 r4
sub r6 r1 r2
"""
                output  = get_code(program)
                answer  = "12340000"
                answer += "16120000"
                answer  = bytes.fromhex(answer)
                self.assertEqual(output, answer)

        def test_mult_assem(self):
                program = \
"""
mult r2 r3 r4
mult r6 r1 r2
"""
                output  = get_code(program)
                answer  = "22340000"
                answer += "26120000"
                answer  = bytes.fromhex(answer)
                self.assertEqual(output, answer)

        def test_div_assem(self):
                program = \
"""
div r2 r3 r4
div r6 r1 r2
"""
                output  = get_code(program)
                answer  = "32340000"
                answer += "36120000"
                answer  = bytes.fromhex(answer)
                self.assertEqual(output, answer)

        def test_and_assem(self):
                program = \
"""
and r2 r3 r4
and r6 r1 r2
"""
                output  = get_code(program)
                answer  = "42340000"
                answer += "46120000"
                answer  = bytes.fromhex(answer)
                self.assertEqual(output, answer)

        def test_or_assem(self):
                program = \
"""
or r2 r3 r4
or r6 r1 r2
"""
                output  = get_code(program)
                answer  = "52340000"
                answer += "56120000"
                answer  = bytes.fromhex(answer)
                self.assertEqual(output, answer)

        def test_zjump_assem(self):
                program = \
"""
zjump r1 r4
zjump r8 r7
"""
                output  = get_code(program)
                answer  = "61400000"
                answer += "68700000"
                answer  = bytes.fromhex(answer)
                self.assertEqual(output, answer)

        def test_gjump_assem(self):
                program = \
"""
gjump r1 r4 r11
gjump r8 r7 r3
"""
                output  = get_code(program)
                answer  = "714b0000"
                answer += "78730000"
                answer  = bytes.fromhex(answer)
                self.assertEqual(output, answer)

        def test_copy_assem(self):
                program = \
"""
copy 15       r6
copy 0x3f     r4
copy 16724940 r2
copy 0xaabbcc r4
"""
                output  = get_code(program)
                answer  = "800000f6"
                answer += "800003f4"
                answer += "8ff33cc2"
                answer += "8aabbcc4"
                answer  = bytes.fromhex(answer)
                self.assertEqual(output, answer)

        def test_load_assem(self):
                program = \
"""
load r2 r3
load r6 r1
"""
                output  = get_code(program)
                answer  = "92300000"
                answer += "96100000"
                answer  = bytes.fromhex(answer)
                self.assertEqual(output, answer)

        def test_store_assem(self):
                program = \
"""
store r2 r3
store r6 r1
"""
                output  = get_code(program)
                answer  = "a2300000"
                answer += "a6100000"
                answer  = bytes.fromhex(answer)
                self.assertEqual(output, answer)

        def test_stop_assem(self):
                program = \
"""
stop
stop
"""
                output  = get_code(program)
                answer  = "b0000000"
                answer += "b0000000"
                answer  = bytes.fromhex(answer)
                self.assertEqual(output, answer)

        def test_comments_assem(self):
                program = \
"""
# This is comment #1.
add r2 r3 r4
# This is comment #2.
# This is comment #3.
copy 16724940 r2
# This is comment #4.

"""
                output  = get_code(program)
                answer  = "02340000"
                answer += "8ff33cc2"
                answer  = bytes.fromhex(answer)
                self.assertEqual(output, answer)

        def test_labels_assem(self):
                program = \
"""
# This comment and blank lines should not affect labels.

         add r2 r3 r4
         add r6 r1 r2

label_1: sub r2 r3 r4
         add r2 r3 r4


         add r6 r1 r2
         copy label_1 r6
label_2: zjump r1 r2
         label_2
         stop
"""
                output  = get_code(program)
                answer  = "02340000"
                answer += "06120000"
                answer += "12340000"
                answer += "02340000"
                answer += "06120000"
                answer += "80000086"
                answer += "61200000"
                answer += "00000018"
                answer += "b0000000"
                answer  = bytes.fromhex(answer)
                self.assertEqual(output, answer)

        def test_data_assem(self):
                program = \
"""
         # This is a comment.
         add r2 r3 r4
         add r6 r1 r2
label_1: sub r2 r3 r4
         add r2 r3 r4
         add r6 r1 r2
         copy label_1 r6
label_2: zjump r1 r2
         label_2
         stop
         # This is another comment.
         14
         0xabcd
         # This is yet another comment.
         0xdeadbeef
         4294902051
"""
                output  = get_code(program)
                answer  = "02340000"
                answer += "06120000"
                answer += "12340000"
                answer += "02340000"
                answer += "06120000"
                answer += "80000086"
                answer += "61200000"
                answer += "00000018"
                answer += "b0000000"
                answer += "0000000e"
                answer += "0000abcd"
                answer += "deadbeef"
                answer += "ffff0123"
                answer  = bytes.fromhex(answer)
                self.assertEqual(output, answer)

        def test_get_word_emul(self):
                create_emu_mod()
                import __emulator__ as e ; importlib.reload(e)
                subprocess.call(["rm", "__emulator__.py"])

                e.memory = bytearray.fromhex("aabbccddeeff")
                output   = e.get_word(1, e.memory), e.memory
                answer   = (bytes.fromhex("bbccddee"),
                            bytes.fromhex("aabbccddeeff"))
                self.assertEqual(output, answer)

                e.memory = bytearray.fromhex("aabbccddeeff")
                output   = e.get_word(4, e.memory), e.memory
                answer   = (bytes.fromhex("eeff0000"),
                            bytes.fromhex("aabbccddeeff0000"))
                self.assertEqual(output, answer)

                e.memory = bytearray.fromhex("aabbccddeeff")
                output   = e.get_word(7, e.memory), e.memory
                answer   = (bytes.fromhex("00000000"),
                            bytes.fromhex("aabbccddeeff0000000000"))
                self.assertEqual(output, answer)

        def test_set_word_emul(self):
                create_emu_mod()
                import __emulator__ as e ; importlib.reload(e)
                subprocess.call(["rm", "__emulator__.py"])

                e.memory = bytearray.fromhex("aabbccddeeff")
                e.set_word(bytes.fromhex("deadbeef"), 1, e.memory)
                output   = e.memory
                answer   = bytes.fromhex("aadeadbeefff")
                self.assertEqual(output, answer)

                e.memory = bytearray.fromhex("aabbccddeeff")
                e.set_word(bytes.fromhex("deadbeef"), 4, e.memory)
                output   = e.memory
                answer   = bytes.fromhex("aabbccdddeadbeef")
                self.assertEqual(output, answer)

                e.memory = bytearray.fromhex("aabbccddeeff")
                e.set_word(bytes.fromhex("deadbeef"), 7, e.memory)
                output   = e.memory
                answer   = bytes.fromhex("aabbccddeeff00deadbeef")
                self.assertEqual(output, answer)

        def test_get_reg_args_emul(self):
                create_emu_mod()
                import __emulator__ as e ; importlib.reload(e)
                subprocess.call(["rm", "__emulator__.py"])

                output = e.get_reg_args(bytes.fromhex("abcdef78"))
                answer = (11, 12, 13)
                self.assertEqual(output, answer)

                output = e.get_reg_args(bytes.fromhex("a83fef78"))
                answer = (8, 3, 15)
                self.assertEqual(output, answer)

        def test_add_emul(self):
                create_emu_mod()
                import __emulator__ as e ; importlib.reload(e)
                subprocess.call(["rm", "__emulator__.py"])

                e.regs     = list(range(10, 26))
                e.add(bytes.fromhex("095f0000"), e.regs, None)
                output     = e.regs
                answer     = list(range(10, 26))
                answer[15] = 19 + 15
                self.assertEqual(output, answer)

        def test_sub_emul(self):
                create_emu_mod()
                import __emulator__ as e ; importlib.reload(e)
                subprocess.call(["rm", "__emulator__.py"])

                e.regs     = list(range(10, 26))
                e.sub(bytes.fromhex("095f0000"), e.regs, None)
                output     = e.regs
                answer     = list(range(10, 26))
                answer[15] = 19 - 15
                self.assertEqual(output, answer)

        def test_mult_emul(self):
                create_emu_mod()
                import __emulator__ as e ; importlib.reload(e)
                subprocess.call(["rm", "__emulator__.py"])

                e.regs     = list(range(10, 26))
                e.mult(bytes.fromhex("095f0000"), e.regs, None)
                output     = e.regs
                answer     = list(range(10, 26))
                answer[15] = 19 * 15
                self.assertEqual(output, answer)

        def test_div_emul(self):
                create_emu_mod()
                import __emulator__ as e ; importlib.reload(e)
                subprocess.call(["rm", "__emulator__.py"])

                e.regs     = list(range(10, 26))
                e.div(bytes.fromhex("095f0000"), e.regs, None)
                output     = e.regs
                answer     = list(range(10, 26))
                answer[15] = int(19 / 15)
                self.assertEqual(output, answer)

        def test_and_emul(self):
                create_emu_mod()
                import __emulator__ as e ; importlib.reload(e)
                subprocess.call(["rm", "__emulator__.py"])

                e.regs     = list(range(10, 26))
                e.and_(bytes.fromhex("095f0000"), e.regs, None)
                output     = e.regs
                answer     = list(range(10, 26))
                answer[15] = 19 & 15
                self.assertEqual(output, answer)

        def test_or_emul(self):
                create_emu_mod()
                import __emulator__ as e ; importlib.reload(e)
                subprocess.call(["rm", "__emulator__.py"])

                e.regs     = list(range(10, 26))
                e.or_(bytes.fromhex("095f0000"), e.regs, None)
                output     = e.regs
                answer     = list(range(10, 26))
                answer[15] = 19 | 15
                self.assertEqual(output, answer)

        def test_copy_emul(self):
                create_emu_mod()
                import __emulator__ as e ; importlib.reload(e)
                subprocess.call(["rm", "__emulator__.py"])

                e.regs     = list(range(10, 26))
                e.copy(bytes.fromhex("deadbeef"), e.regs, None)
                output     = e.regs
                answer     = list(range(10, 26))
                answer[15] = 0xeadbee
                self.assertEqual(output, answer)

        def test_load_emul(self):
                create_emu_mod()
                import __emulator__ as e ; importlib.reload(e)
                subprocess.call(["rm", "__emulator__.py"])

                e.memory  = bytearray.fromhex("aabbccddeeff")
                e.regs    = list(range(1, 17))
                e.load(bytes.fromhex("01300000"), e.regs, e.memory)
                output    = e.regs, e.memory
                answer    = list(range(1, 17))
                answer[3] = 0xccddeeff
                answer    = answer, bytes.fromhex("aabbccddeeff")
                self.assertEqual(output, answer)

                e.memory  = bytearray.fromhex("aabbccddeeff")
                e.regs    = list(range(1, 17))
                e.load(bytes.fromhex("03900000"), e.regs, e.memory)
                output    = e.regs, e.memory
                answer    = list(range(1, 17))
                answer[9] = 0xeeff0000
                answer    = answer, bytes.fromhex("aabbccddeeff0000")
                self.assertEqual(output, answer)

                e.memory  = bytearray.fromhex("aabbccddeeff")
                e.regs    = list(range(1, 17))
                e.load(bytes.fromhex("06900000"), e.regs, e.memory)
                output    = e.regs, e.memory
                answer    = list(range(1, 17))
                answer[9] = 0x00000000
                answer    = answer, bytes.fromhex("aabbccddeeff0000000000")
                self.assertEqual(output, answer)

        def test_store_emul(self):
                create_emu_mod()
                import __emulator__ as e ; importlib.reload(e)
                subprocess.call(["rm", "__emulator__.py"])

                e.memory   = bytearray.fromhex("aabbccddeeff")
                e.regs     = list(range(1, 17))
                e.regs[11] = 0xdeadbeef
                e.store(bytes.fromhex("0b100000"), e.regs, e.memory)
                output     = e.regs, e.memory
                answer     = list(range(1, 17))
                answer[11] = 0xdeadbeef
                answer     = (answer, bytes.fromhex("aabbdeadbeef"))
                self.assertEqual(output, answer)

                e.memory   = bytearray.fromhex("aabbccddeeff")
                e.regs     = list(range(1, 17))
                e.regs[11] = 0xdeadbeef
                e.store(bytes.fromhex("0b300000"), e.regs, e.memory)
                output     = e.regs, e.memory
                answer     = list(range(1, 17))
                answer[11] = 0xdeadbeef
                answer     = (answer, bytes.fromhex("aabbccdddeadbeef"))
                self.assertEqual(output, answer)

                e.memory   = bytearray.fromhex("aabbccddeeff")
                e.regs     = list(range(1, 17))
                e.regs[11] = 0xdeadbeef
                e.store(bytes.fromhex("0b600000"), e.regs, e.memory)
                output     = e.regs, e.memory
                answer     = list(range(1, 17))
                answer[11] = 0xdeadbeef
                answer     = (answer, bytes.fromhex("aabbccddeeff00deadbeef"))
                self.assertEqual(output, answer)

        def test_zjump_emul(self):
                create_emu_mod()
                import __emulator__ as e ; importlib.reload(e)
                subprocess.call(["rm", "__emulator__.py"])

                e.regs    = list(range(11, 27))
                e.regs[4] = 9999
                e.zjump(bytes.fromhex("04300000"), e.regs, None)
                output    = e.regs
                answer    = list(range(11, 27))
                answer[4] = 9999
                self.assertEqual(output, answer)

                e.regs    = list(range(11, 27))
                e.regs[4] = 0
                e.zjump(bytes.fromhex("04300000"), e.regs, None)
                output    = e.regs
                answer    = list(range(11, 27))
                answer[4] = 0
                answer[0] = 10
                self.assertEqual(output, answer)

        def test_gjump_emul(self):
                create_emu_mod()
                import __emulator__ as e ; importlib.reload(e)
                subprocess.call(["rm", "__emulator__.py"])

                e.regs    = list(range(11, 27))
                e.regs[4] = 9999
                e.gjump(bytes.fromhex("03450000"), e.regs, None)
                output    = e.regs
                answer    = list(range(11, 27))
                answer[4] = 9999
                self.assertEqual(output, answer)

                e.regs    = list(range(11, 27))
                e.regs[4] = 0
                e.gjump(bytes.fromhex("03450000"), e.regs, None)
                output    = e.regs
                answer    = list(range(11, 27))
                answer[4] = 0
                answer[0] = 12
                self.assertEqual(output, answer)

        def test_stop_emul(self):
                create_emu_mod()
                import __emulator__ as e ; importlib.reload(e)
                subprocess.call(["rm", "__emulator__.py"])

                e.regs = list(range(1, 17))
                e.stop(bytes.fromhex("0b100000"), e.regs, None)
                output = e.regs
                answer = list(range(1, 17))
                self.assertEqual(output, answer)

        def test_lots_1(self):
                program = \
"""
copy 0x8      r1
copy 0x9      r2
copy 0xaabbcc r10
add  r1 r2 r3
stop
"""
                output = get_output(program)
                answer = \
b"""
registers:

	 r0: 0x00000014
	 r1: 0x00000008
	 r2: 0x00000009
	 r3: 0x00000011
	 r4: 0x00000000
	 r5: 0x00000000
	 r6: 0x00000000
	 r7: 0x00000000
	 r8: 0x00000000
	 r9: 0x00000000
	r10: 0x00aabbcc
	r11: 0x00000000
	r12: 0x00000000
	r13: 0x00000000
	r14: 0x00000000
	r15: 0x00000000

memory:

	0x00000000: 0x80000081
	0x00000004: 0x80000092
	0x00000008: 0x8aabbcca
	0x0000000c: 0x01230000
	0x00000010: 0xb0000000
""".lstrip()
                self.assertEqual(output, answer)

        def test_lots_2(self):
                program = \
"""
copy 0x8      r1
copy 0x9      r2
copy 0xaabbcc r10
add  r1  r2 r3
sub  r10 r1 r4
stop
"""
                output = get_output(program)
                answer = \
b"""
registers:

	 r0: 0x00000018
	 r1: 0x00000008
	 r2: 0x00000009
	 r3: 0x00000011
	 r4: 0x00aabbc4
	 r5: 0x00000000
	 r6: 0x00000000
	 r7: 0x00000000
	 r8: 0x00000000
	 r9: 0x00000000
	r10: 0x00aabbcc
	r11: 0x00000000
	r12: 0x00000000
	r13: 0x00000000
	r14: 0x00000000
	r15: 0x00000000

memory:

	0x00000000: 0x80000081
	0x00000004: 0x80000092
	0x00000008: 0x8aabbcca
	0x0000000c: 0x01230000
	0x00000010: 0x1a140000
	0x00000014: 0xb0000000
""".lstrip()
                self.assertEqual(output, answer)

        def test_lots_3(self):
                program = \
"""
copy 0x8      r1
copy 0x9      r2
copy 0xaabbcc r10
add  r1  r2 r3
sub  r10 r1 r4
and  r10 r2 r5
or   r10 r2 r6
stop
"""
                output = get_output(program)
                answer = \
b"""
registers:

	 r0: 0x00000020
	 r1: 0x00000008
	 r2: 0x00000009
	 r3: 0x00000011
	 r4: 0x00aabbc4
	 r5: 0x00000008
	 r6: 0x00aabbcd
	 r7: 0x00000000
	 r8: 0x00000000
	 r9: 0x00000000
	r10: 0x00aabbcc
	r11: 0x00000000
	r12: 0x00000000
	r13: 0x00000000
	r14: 0x00000000
	r15: 0x00000000

memory:

	0x00000000: 0x80000081
	0x00000004: 0x80000092
	0x00000008: 0x8aabbcca
	0x0000000c: 0x01230000
	0x00000010: 0x1a140000
	0x00000014: 0x4a250000
	0x00000018: 0x5a260000
	0x0000001c: 0xb0000000
""".lstrip()
                self.assertEqual(output, answer)

        def test_lots_4(self):
                program = \
"""
      copy 0x8      r1
      copy 0x9      r2
      copy 0xaabbcc r10
      add  r1  r2 r3
      sub  r10 r1 r4
      and  r10 r2 r5
      or   r10 r2 r6
      copy data r7
      load r7   r8
      stop
data: 0xdeadbeef
"""
                output = get_output(program)
                answer = \
b"""
registers:

	 r0: 0x00000028
	 r1: 0x00000008
	 r2: 0x00000009
	 r3: 0x00000011
	 r4: 0x00aabbc4
	 r5: 0x00000008
	 r6: 0x00aabbcd
	 r7: 0x00000028
	 r8: 0xdeadbeef
	 r9: 0x00000000
	r10: 0x00aabbcc
	r11: 0x00000000
	r12: 0x00000000
	r13: 0x00000000
	r14: 0x00000000
	r15: 0x00000000

memory:

	0x00000000: 0x80000081
	0x00000004: 0x80000092
	0x00000008: 0x8aabbcca
	0x0000000c: 0x01230000
	0x00000010: 0x1a140000
	0x00000014: 0x4a250000
	0x00000018: 0x5a260000
	0x0000001c: 0x80000287
	0x00000020: 0x97800000
	0x00000024: 0xb0000000
	0x00000028: 0xdeadbeef
""".lstrip()
                self.assertEqual(output, answer)

        def test_lots_5(self):
                program = \
"""
      copy  0x8      r1
      copy  0x9      r2
      copy  0xaabbcc r10
      add   r1  r2 r3
      sub   r10 r1 r4
      and   r10 r2 r5
      or    r10 r2 r6
      copy  data r7
      load  r7   r8
      store r8   r2
      stop
data: 0xdeadbeef
"""
                output = get_output(program)
                answer = \
b"""
registers:

	 r0: 0x0000002c
	 r1: 0x00000008
	 r2: 0x00000009
	 r3: 0x00000011
	 r4: 0x00aabbc4
	 r5: 0x00000008
	 r6: 0x00aabbcd
	 r7: 0x0000002c
	 r8: 0xdeadbeef
	 r9: 0x00000000
	r10: 0x00aabbcc
	r11: 0x00000000
	r12: 0x00000000
	r13: 0x00000000
	r14: 0x00000000
	r15: 0x00000000

memory:

	0x00000000: 0x80000081
	0x00000004: 0x80000092
	0x00000008: 0x8adeadbe
	0x0000000c: 0xef230000
	0x00000010: 0x1a140000
	0x00000014: 0x4a250000
	0x00000018: 0x5a260000
	0x0000001c: 0x800002c7
	0x00000020: 0x97800000
	0x00000024: 0xa8200000
	0x00000028: 0xb0000000
	0x0000002c: 0xdeadbeef
""".lstrip()
                self.assertEqual(output, answer)

        def test_lots_6(self):
                program = \
"""
      copy  0xabc r1
      copy  0xdef r2
      copy      0 r3
      copy     bb r4
      zjump    r3 r4
aa:   copy  0x87c r5
bb:   copy  0xb31 r6
      stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()
                answer = \
"""
registers:

	 r0: 0x00000020
	 r1: 0x00000abc
	 r2: 0x00000def
	 r3: 0x00000000
	 r4: 0x00000018
	 r5: 0x00000000
	 r6: 0x00000b31
	 r7: 0x00000000
	 r8: 0x00000000
	 r9: 0x00000000
	r10: 0x00000000
	r11: 0x00000000
	r12: 0x00000000
	r13: 0x00000000
	r14: 0x00000000
	r15: 0x00000000
""".strip()
                self.assertEqual(output, answer)

        def test_lots_7(self):
                program = \
"""
      copy  0xabc r1
      copy  0xdef r2
      copy   0xab r3
      copy     bb r4
      zjump    r3 r4
aa:   copy  0x87c r5
bb:   copy  0xb31 r6
      stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()
                answer = \
"""
registers:

	 r0: 0x00000020
	 r1: 0x00000abc
	 r2: 0x00000def
	 r3: 0x000000ab
	 r4: 0x00000018
	 r5: 0x0000087c
	 r6: 0x00000b31
	 r7: 0x00000000
	 r8: 0x00000000
	 r9: 0x00000000
	r10: 0x00000000
	r11: 0x00000000
	r12: 0x00000000
	r13: 0x00000000
	r14: 0x00000000
	r15: 0x00000000
""".strip()
                self.assertEqual(output, answer)

        def test_lots_8(self):
                program = \
"""
      copy  0x8      r1
      copy  0x9      r2
      copy  0xaabbcc r10
      add   r1  r2 r3
      sub   r10 r1 r4
      mult  r1  r2 r5
      div   r4  r3 r6
      and   r6  r4 r7
      or    r7  r1 r8
      copy  data r9
      load  r9   r10
      add   r9   r2  r9
      store r10  r9
      stop
data: 0xdeadbeef
"""
                output = get_output(program)
                answer = \
b"""
registers:

	 r0: 0x00000038
	 r1: 0x00000008
	 r2: 0x00000009
	 r3: 0x00000011
	 r4: 0x00aabbc4
	 r5: 0x00000048
	 r6: 0x000a0b0b
	 r7: 0x000a0b00
	 r8: 0x000a0b08
	 r9: 0x00000041
	r10: 0xdeadbeef
	r11: 0x00000000
	r12: 0x00000000
	r13: 0x00000000
	r14: 0x00000000
	r15: 0x00000000

memory:

	0x00000000: 0x80000081
	0x00000004: 0x80000092
	0x00000008: 0x8aabbcca
	0x0000000c: 0x01230000
	0x00000010: 0x1a140000
	0x00000014: 0x21250000
	0x00000018: 0x34360000
	0x0000001c: 0x46470000
	0x00000020: 0x57180000
	0x00000024: 0x80000389
	0x00000028: 0x99a00000
	0x0000002c: 0x09290000
	0x00000030: 0xaa900000
	0x00000034: 0xb0000000
	0x00000038: 0xdeadbeef
	0x0000003c: 0x00000000
	0x00000040: 0x00deadbe
	0x00000044: 0xef000000
""".lstrip()
                self.assertEqual(output, answer)

        def test_func_calls(self):
                program = \
"""
# ------------------------------------------------------------------------------
# initial steps
# ------------------------------------------------------------------------------

# Sets r13 to zero for zjump instructions.
# Sets r14 to the address of f.

        copy  0x0  r13
        copy    f  r14

# Load word beginning at db, doubles it and stores in r10.

        copy  db   r10
        load  r10  r10
        add   r10  r10  r10

# Stores results in r10 at dbx2 using r11.

        copy  dbx2 r11
        store r10  r11

# ------------------------------------------------------------------------------
# first calculation
# ------------------------------------------------------------------------------

# Sets r1, r2, r3, r4 and r5 to be used as the arguments of f.
# Sets r15 to the return value.
# Invokes f.

c_1_b:  copy  0x1   r1
        copy  0x2   r2
        copy  0x3   r3
        copy  0x4   r4
        copy  0x5   r5
        copy  c_1_e r15
        zjump r13   r14

# Stores the result from r6 at ans_1 using r7.

c_1_e:  copy  ans_1 r7
        store r6    r7

# ------------------------------------------------------------------------------
# second calculation
# ------------------------------------------------------------------------------

# Sets r1, r2, r3, r4 and r5 to be used as the arguments of f.
# Sets r15 to the return value.
# Invokes f.

c_2_b:  copy  0xabcd r1
        copy  0x4a8d r2
        copy  0x9a7e r3
        copy  0xab23 r4
        copy  0xbb33 r5
        copy  c_2_e  r15
        zjump r13    r14

# Stores the result from r6 at ans_1 using r7.

c_2_e:  copy  ans_2 r7
        store r6    r7

# ------------------------------------------------------------------------------
# third calculation
# ------------------------------------------------------------------------------

# Sets r1, r2, r3, r4 and r5 to be used as the arguments of f.
# Sets r15 to the return value.
# Invokes f.

c_3_b:  copy  0x1f  r1
        copy  0x2f  r2
        copy  0x3f  r3
        copy  0x4f  r4
        copy  0x5f  r5
        copy  c_3_e r15
        zjump r13   r14

# Stores the result from r6 at ans_1 using r7.

c_3_e:  copy  ans_3 r7
        store r6    r7

# ------------------------------------------------------------------------------
# fourth calculation
# ------------------------------------------------------------------------------

# Sets r1, r2, r3, r4 and r5 to be used as the arguments of f.
# Sets r15 to the return value.
# Invokes f.

c_4_b:  copy  0x1ab r1
        copy  0x2bc r2
        copy  0x3cd r3
        copy  0x4de r4
        copy  0x5ef r5
        copy  c_4_e r15
        zjump r13   r14

# Stores the result from r6 at ans_1 using r7.

c_4_e:  copy  ans_4 r7
        store r6    r7

# ------------------------------------------------------------------------------
# Stop
# ------------------------------------------------------------------------------

        stop

# ------------------------------------------------------------------------------
# function definition
# ------------------------------------------------------------------------------

# f(a, b, c, d, e) = [(a + b - c) & d] | e

f:      add   r1  r2   r6
        sub   r6  r3   r6
        and   r6  r4   r6
        or    r6  r5   r6
        zjump r13 r15

# ------------------------------------------------------------------------------
# storage
# ------------------------------------------------------------------------------

ans_1:  0x0
ans_2:  0x0
ans_3:  0x0
ans_4:  0x0
db:     0xdeadbeef
dbx2:   0x0
"""
                output = get_output(program)
                output = "\n".join(output.decode().split("\n")[-7:]).lstrip()
                answer = \
"""
	0x000000c4: 0x00000005
	0x000000c8: 0x0000bb33
	0x000000cc: 0x0000005f
	0x000000d0: 0x000005ff
	0x000000d4: 0xdeadbeef
	0x000000d8: 0xbd5b7dde
""".lstrip()
                self.assertEqual(output, answer)

        def test_gt(self):
                program = \
"""
# This is a partial implementation of the greater than function.
# a > b is found, for some cases only, from the most significant bit of b - a.

# ------------------------------------------------------------------------------
# initial steps
# ------------------------------------------------------------------------------

# Sets r11 to the word length in bytes.
# Sets r12 to the value used to determine the most significant bits.
# Sets r13 to zero so zjump instructions will always jump.
# Sets r14 to the address of gt.

        copy  word r11
        load  r11  r11
        copy  mask r12
        load  r12  r12
        copy  0x0  r13
        copy  gt   r14

# ------------------------------------------------------------------------------
# c_1
# ------------------------------------------------------------------------------

# Sets r1 and r2 to be used as the arguments of gt.
# Sets r15 to the return value.
# Invokes gt.

c_1_b:  copy  args_1 r1
        load  r1     r1
        copy  args_1 r2
        add   r11    r2  r2
        load  r2     r2
        copy  c_1_e  r15
        zjump r13    r14

# Stores the result from r6 at ans_1 using r7.

c_1_e:  copy  ans_1 r7
        store r6    r7

# ------------------------------------------------------------------------------
# c_2
# ------------------------------------------------------------------------------

# Sets r1 and r2 to be used as the arguments of gt.
# Sets r15 to the return value.
# Invokes gt.

c_2_b:  copy  args_2 r1
        load  r1     r1
        copy  args_2 r2
        add   r11    r2  r2
        load  r2     r2
        copy  c_2_e  r15
        zjump r13    r14

# Stores the result from r6 at ans_2 using r7.

c_2_e:  copy  ans_2 r7
        store r6    r7

# ------------------------------------------------------------------------------
# c_3
# ------------------------------------------------------------------------------

# Sets r1 and r2 to be used as the arguments of gt.
# Sets r15 to the return value.
# Invokes gt.

c_3_b:  copy  args_3 r1
        load  r1     r1
        copy  args_3 r2
        add   r11    r2  r2
        load  r2     r2
        copy  c_3_e  r15
        zjump r13    r14

# Stores the result from r6 at ans_3 using r7.

c_3_e:  copy  ans_3 r7
        store r6    r7

# ------------------------------------------------------------------------------
# c_4
# ------------------------------------------------------------------------------

# Sets r1 and r2 to be used as the arguments of gt.
# Sets r15 to the return value.
# Invokes gt.

c_4_b:  copy  args_4 r1
        load  r1     r1
        copy  args_4 r2
        add   r11    r2  r2
        load  r2     r2
        copy  c_4_e  r15
        zjump r13    r14

# Stores the result from r6 at ans_4 using r7.

c_4_e:  copy  ans_4 r7
        store r6    r7

# ------------------------------------------------------------------------------
# c_5
# ------------------------------------------------------------------------------

# Sets r1 and r2 to be used as the arguments of gt.
# Sets r15 to the return value.
# Invokes gt.

c_5_b:  copy  args_5 r1
        load  r1     r1
        copy  args_5 r2
        add   r11    r2  r2
        load  r2     r2
        copy  c_5_e  r15
        zjump r13    r14

# Stores the result from r6 at ans_5 using r7.

c_5_e:  copy  ans_5 r7
        store r6    r7

# ------------------------------------------------------------------------------
# c_6
# ------------------------------------------------------------------------------

# Sets r1 and r2 to be used as the arguments of gt.
# Sets r15 to the return value.
# Invokes gt.

c_6_b:  copy  args_6 r1
        load  r1     r1
        copy  args_6 r2
        add   r11    r2  r2
        load  r2     r2
        copy  c_6_e  r15
        zjump r13    r14

# Stores the result from r6 at ans_6 using r7.

c_6_e:  copy  ans_6 r7
        store r6    r7

# ------------------------------------------------------------------------------
# c_7
# ------------------------------------------------------------------------------

# Sets r1 and r2 to be used as the arguments of gt.
# Sets r15 to the return value.
# Invokes gt.

c_7_b:  copy  args_7 r1
        load  r1     r1
        copy  args_7 r2
        add   r11    r2  r2
        load  r2     r2
        copy  c_7_e  r15
        zjump r13    r14

# Stores the result from r6 at ans_7 using r7.

c_7_e:  copy  ans_7 r7
        store r6    r7

# ------------------------------------------------------------------------------
# c_8
# ------------------------------------------------------------------------------

# Sets r1 and r2 to be used as the arguments of gt.
# Sets r15 to the return value.
# Invokes gt.

c_8_b:  copy  args_8 r1
        load  r1     r1
        copy  args_8 r2
        add   r11    r2  r2
        load  r2     r2
        copy  c_8_e  r15
        zjump r13    r14

# Stores the result from r6 at ans_8 using r7.

c_8_e:  copy  ans_8 r7
        store r6    r7

# ------------------------------------------------------------------------------
# c_9
# ------------------------------------------------------------------------------

# Sets r1 and r2 to be used as the arguments of gt.
# Sets r15 to the return value.
# Invokes gt.

c_9_b:  copy  args_9 r1
        load  r1     r1
        copy  args_9 r2
        add   r11    r2  r2
        load  r2     r2
        copy  c_9_e  r15
        zjump r13    r14

# Stores the result from r6 at ans_9 using r7.

c_9_e:  copy  ans_9 r7
        store r6    r7

# ------------------------------------------------------------------------------
# c_a
# ------------------------------------------------------------------------------

# Sets r1 and r2 to be used as the arguments of gt.
# Sets r15 to the return value.
# Invokes gt.

c_a_b:  copy  args_a r1
        load  r1     r1
        copy  args_a r2
        add   r11    r2  r2
        load  r2     r2
        copy  c_a_e  r15
        zjump r13    r14

# Stores the result from r6 at ans_a using r7.

c_a_e:  copy  ans_a r7
        store r6    r7

# ------------------------------------------------------------------------------
# c_b
# ------------------------------------------------------------------------------

# Sets r1 and r2 to be used as the arguments of gt.
# Sets r15 to the return value.
# Invokes gt.

c_b_b:  copy  args_b r1
        load  r1     r1
        copy  args_b r2
        add   r11    r2  r2
        load  r2     r2
        copy  c_b_e  r15
        zjump r13    r14

# Stores the result from r6 at ans_b using r7.

c_b_e:  copy  ans_b r7
        store r6    r7

# ------------------------------------------------------------------------------
# c_c
# ------------------------------------------------------------------------------

# Sets r1 and r2 to be used as the arguments of gt.
# Sets r15 to the return value.
# Invokes gt.

c_c_b:  copy  args_c r1
        load  r1     r1
        copy  args_c r2
        add   r11    r2  r2
        load  r2     r2
        copy  c_c_e  r15
        zjump r13    r14

# Stores the result from r6 at ans_c using r7.

c_c_e:  copy  ans_c r7
        store r6    r7

# ------------------------------------------------------------------------------
# c_d
# ------------------------------------------------------------------------------

# Sets r1 and r2 to be used as the arguments of gt.
# Sets r15 to the return value.
# Invokes gt.

c_d_b:  copy  args_d r1
        load  r1     r1
        copy  args_d r2
        add   r11    r2  r2
        load  r2     r2
        copy  c_d_e  r15
        zjump r13    r14

# Stores the result from r6 at ans_d using r7.

c_d_e:  copy  ans_d r7
        store r6    r7

# ------------------------------------------------------------------------------
# c_e
# ------------------------------------------------------------------------------

# Sets r1 and r2 to be used as the arguments of gt.
# Sets r15 to the return value.
# Invokes gt.

c_e_b:  copy  args_e r1
        load  r1     r1
        copy  args_e r2
        add   r11    r2  r2
        load  r2     r2
        copy  c_e_e  r15
        zjump r13    r14

# Stores the result from r6 at ans_e using r7.

c_e_e:  copy  ans_e r7
        store r6    r7

# ------------------------------------------------------------------------------
# Stop
# ------------------------------------------------------------------------------

        stop

# ------------------------------------------------------------------------------
# function definition
# ------------------------------------------------------------------------------

# gt(a, b) = 1 if a > b else 0

gt:     sub   r2     r1 r3
        and   r12    r3 r3
        copy  gt_ret    r4
        copy  gt_no     r5
        zjump r3        r5
gt_yes: copy  0x1       r6
        zjump r13       r4
gt_no:  copy  0x0       r6
gt_ret: zjump r13       r15

# ------------------------------------------------------------------------------
# storage
# ------------------------------------------------------------------------------

word:   0x0000004
mask:   0x8000000
args_1: 0xaaaaaaa
        0xf000000
args_2: 0xaaaaaaa
        0x1000000
args_3: 0xaaaaaaa
        0x0000006
args_4: 0xaaaaaaa
        0x8000000
args_5: 0xaaaaaaa
        0x0000000
args_6: 0xaaaaaaa
        0xfffffff
args_7: 0xaaaaaaa
        0x7ffffff
args_8: 0x000cccc
        0xf000000
args_9: 0x000cccc
        0x1000000
args_a: 0x000cccc
        0x0000006
args_b: 0x000cccc
        0x8000000
args_c: 0x000cccc
        0x0000000
args_d: 0x000cccc
        0xfffffff
args_e: 0x000cccc
        0x7ffffff

# 32 set bits denotes the beginning of the answers.

        0xffffffff

ans_1:  0x0
ans_2:  0x0
ans_3:  0x0
ans_4:  0x0
ans_5:  0x0
ans_6:  0x0
ans_7:  0x0
ans_8:  0x0
ans_9:  0x0
ans_a:  0x0
ans_b:  0x0
ans_c:  0x0
ans_d:  0x0
ans_e:  0x0

"""
                output = get_output(program)
                output = "\n".join(output.decode().split("\n")[-15:]).lstrip()
                answer = \
"""
	0x000002b4: 0x00000000
	0x000002b8: 0x00000000
	0x000002bc: 0x00000000
	0x000002c0: 0x00000001
	0x000002c4: 0x00000000
	0x000002c8: 0x00000000
	0x000002cc: 0x00000001
	0x000002d0: 0x00000001
	0x000002d4: 0x00000000
	0x000002d8: 0x00000001
	0x000002dc: 0x00000000
	0x000002e0: 0x00000001
	0x000002e4: 0x00000001
	0x000002e8: 0x00000000
""".lstrip()
                self.assertEqual(output, answer)

        def test_parse_arg(self):
                for e in [("32",        32),
                          ("32z",       ["32z"]),
                          ("0xabc",     0xabc),
                          ("0xabcz",    ["0xabcz"]),
                          ("r0",        "r0"),
                          ("r3",        "r3"),
                          ("r8",        "r8"),
                          ("r10",       "r10"),
                          ("r12",       "r12"),
                          ("r15",       "r15"),
                          ("r16",       ["r16"]),
                          ("r1y",       ["r1y"]),
                          ("r3+24",     ("r3", 24)),
                          ("r3-24",     ("r3", -24)),
                          ("r15+0xabc", ("r15",  0xabc)),
                          ("r15-0xabc", ("r15", -0xabc)),
                          ("label34",   ["label34"])]:
                        output  = macros.parse_arg(e[0])
                        answer  = e[1]
                        self.assertEqual(output, answer)

        def test_parse_args(self):
                output = macros.parse_args(" r1 r2 r3 ".split())
                answer = ["r1", "r2", "r3"]
                self.assertEqual(output, answer)

                output = macros.parse_args(" 42 0x123 r13 ".split())
                answer = [42, 0x123, "r13"]
                self.assertEqual(output, answer)

                output = macros.parse_args(" r7 + 6 r11 ".split())
                answer = [("r7", 6), "r11"]
                self.assertEqual(output, answer)

                output = macros.parse_args(" r7 + 6 r11 - 0xa r0 + 44 ".split())
                answer = [("r7", 6), ("r11", -10), ("r0", 44)]
                self.assertEqual(output, answer)

                output = macros.parse_args("r7 + 6 r11 charlie".split())
                answer = [("r7", 6), "r11", ["charlie"]]
                self.assertEqual(output, answer)

        def test_replace(self):
                asm = """

                     add  r1    r2    r3


label1:            add  r1 r2   r3

                      load r5 r8
                NOTH
label2:                NOTH
"""[1:]
                output  = macros.replace(asm)
                answer  = """
                  add     r1                r2                r3
label1:           add     r1                r2                r3
                  load    r5                r8
                  and     r1                r1                r1
                  and     r1                r1                r1
label2:           and     r1                r1                r1
                  and     r1                r1                r1
"""[1:]
                self.assertEqual(output, answer)

        def test_NOTH(self):
                asm = """
                NOTH
label:                NOTH
"""[1:]
                output  = macros.replace(asm)
                answer  = """
                  and     r1                r1                r1
                  and     r1                r1                r1
label:            and     r1                r1                r1
                  and     r1                r1                r1
"""[1:]
                self.assertEqual(output, answer)

        def test_COPY(self):
                asm = """
                COPY r1 r3
label:                COPY r14 r6
"""[1:]
                output  = macros.replace(asm)
                answer  = """
                  and     r1                r1                r1
                  and     r1                r1                r3
label:            and     r1                r1                r1
                  and     r14               r14               r6
"""[1:]
                self.assertEqual(output, answer)

                program = \
"""
                copy 0xabc r1
                COPY r1    r2
                stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[31:]
                answer = \
"""
	 r1: 0x00000abc
	 r2: 0x00000abc
	 r3: 0x00000000
	 r4: 0x00000000
	 r5: 0x00000000
	 r6: 0x00000000
	 r7: 0x00000000
	 r8: 0x00000000
	 r9: 0x00000000
	r10: 0x00000000
	r11: 0x00000000
	r12: 0x00000000
	r13: 0x00000000
	r14: 0x00000000
	r15: 0x00000000
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                COPY 0xdef        r12
                COPY 0xdeadbeef   r13
                COPY r12 + 0x7000 r14
                COPY r12 - 0x300  r15
                stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000def
	r13: 0xdeadbeef
	r14: 0x00007def
	r15: 0x00000aef
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                COPY 0xdeadbeef       r13
                COPY r13 + 0x10000000 r14
                stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000000
	r13: 0xdeadbeef
	r14: 0xeeadbeef
	r15: 0x00000000
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                and  r1 r1 r1
                and  r1 r1 r1
                and  r1 r1 r1
label:          and  r1 r1 r1
                COPY label        r12
                stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x0000000c
	r13: 0x00000000
	r14: 0x00000000
	r15: 0x00000000
""".strip()
                self.assertEqual(output, answer)

        def test_MULT(self):
                program = \
"""
                COPY 0x74 r12
                COPY 0x15 r13
                MULT r12  r13 r14
                MULT 0xf  16  r15
                stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000074
	r13: 0x00000015
	r14: 0x00000984
	r15: 0x000000f0
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                COPY 0x74 r12
                COPY 0x15 r13
                MULT r12 + 10 r13 - 0x3 r14
                stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000074
	r13: 0x00000015
	r14: 0x000008dc
	r15: 0x00000000
""".strip()
                self.assertEqual(output, answer)

        def test_DIV(self):
                program = \
"""
                DIV 0x6        0x2        r12
                DIV 0xdeadbeef 0xdeadbeef r13
                DIV 0xdeadbeef 0xdeadbeff r14
                DIV 0x1        0x80000000 r15
                stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000003
	r13: 0x00000001
	r14: 0x00000000
	r15: 0x00000000
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                COPY 0x7fffffff r12
                COPY 0x80000002 r13
                COPY 0x80000000 r14
                DIV  r12        r14 r12
                DIV  r13        r14 r13
                stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000000
	r13: 0x00000001
	r14: 0x80000000
	r15: 0x00000000
""".strip()
                self.assertEqual(output, answer)

        def test_SUB(self):
                program = \
"""
                SUB 0x6 0x2               r12
                SUB 0xdeadbeef 0xdeadbeef r13
                SUB 0xdeadbeef 0xdeadbef1 r14
                SUB 0xdeadbeff 0xdeadbeef r15
                stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000004
	r13: 0x00000000
	r14: 0xfffffffe
	r15: 0x00000010
""".strip()
                self.assertEqual(output, answer)

        def test_LOAD(self):
                program = \
"""
                and  r1 r1 r1
                and  r1 r1 r1
                and  r1 r1 r1
label:          and  r1 r1 r1
                and  r6 r6 r6
                LOAD 0x4     r12
                copy label   r13
                LOAD r13     r14
                LOAD label   r15
                stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x41110000
	r13: 0x0000000c
	r14: 0x41110000
	r15: 0x41110000
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                and  r1 r1 r1
                and  r2 r2 r2
label:          and  r3 r3 r3

                COPY 0x4     r12
                LOAD r12 + 4 r13

                stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000004
	r13: 0x43330000
	r14: 0x00000000
	r15: 0x00000000
""".strip()
                self.assertEqual(output, answer)

        def test_STORE(self):
                program = \
"""
                and  r1 r1 r1
                and  r1 r1 r1
label1:         and  r1 r1 r1
label2:         and  r1 r1 r1

                COPY  0xdeadbeef r13
                COPY  label1     r14
                COPY  label2     r15

                STORE r13        r14
                STORE 0xabcdef   r15

                stop
"""
                output = get_output(program)
                output = output.decode()
                beg    = output.find("memory")
                end    = output.find("	0x00000010: ")
                output = output[beg:end]
                answer = \
"""
memory:

	0x00000000: 0x41110000
	0x00000004: 0x41110000
	0x00000008: 0xdeadbeef
	0x0000000c: 0x00abcdef
""".lstrip()
                self.assertEqual(output, answer)

                program = \
"""
                and  r1 r1 r1
                and  r1 r1 r1
label1:         and  r1 r1 r1
label2:         and  r1 r1 r1

                COPY  0xdeadbeef r13

                STORE r13      label1
                STORE 0xabcdef label2

                stop
"""
                output = get_output(program)
                output = output.decode()
                beg    = output.find("memory")
                end    = output.find("	0x00000010: ")
                output = output[beg:end]
                answer = \
"""
memory:

	0x00000000: 0x41110000
	0x00000004: 0x41110000
	0x00000008: 0xdeadbeef
	0x0000000c: 0x00abcdef
""".lstrip()
                self.assertEqual(output, answer)

                program = \
"""
                and  r1 r1 r1
                and  r1 r1 r1
                and  r1 r1 r1
                and  r1 r1 r1

                COPY 0xabc r13
                COPY 0x8   r14

                STORE r13 + 0x1000 r14

                stop
"""
                output = get_output(program)
                output = output.decode()
                beg    = output.find("memory")
                end    = output.find("	0x00000010: ")
                output = output[beg:end]
                answer = \
"""
memory:

	0x00000000: 0x41110000
	0x00000004: 0x41110000
	0x00000008: 0x00001abc
	0x0000000c: 0x41110000
""".lstrip()
                self.assertEqual(output, answer)

                program = \
"""
                and  r1 r1 r1
                and  r1 r1 r1
                and  r1 r1 r1
                and  r1 r1 r1

                COPY 0xdeadbeef r13
                COPY 0x8        r14

                STORE r13 + 0x1000 r14

                stop
"""
                output = get_output(program)
                output = output.decode()
                beg    = output.find("memory")
                end    = output.find("	0x00000010: ")
                output = output[beg:end]
                answer = \
"""
memory:

	0x00000000: 0x41110000
	0x00000004: 0x41110000
	0x00000008: 0xdeadceef
	0x0000000c: 0x41110000
""".lstrip()
                self.assertEqual(output, answer)

                program = \
"""
                and  r1 r1 r1
                and  r1 r1 r1
label:          and  r1 r1 r1
                and  r1 r1 r1

                COPY 0xdeadbeef r13

                STORE r13 + 0x1000 label

                stop
"""
                output = get_output(program)
                output = output.decode()
                beg    = output.find("memory")
                end    = output.find("	0x00000010: ")
                output = output[beg:end]
                answer = \
"""
memory:

	0x00000000: 0x41110000
	0x00000004: 0x41110000
	0x00000008: 0xdeadceef
	0x0000000c: 0x41110000
""".lstrip()
                self.assertEqual(output, answer)

                program = \
"""
                and  r1 r1 r1
                and  r1 r1 r1
label:          and  r1 r1 r1
                and  r1 r1 r1

                COPY 0xdeadbeef r13
                copy 0x8        r14

                STORE r13 + 0x10000000 r14

                stop
"""
                output = get_output(program)
                output = output.decode()
                beg    = output.find("memory")
                end    = output.find("	0x00000010: ")
                output = output[beg:end]
                answer = \
"""
memory:

	0x00000000: 0x41110000
	0x00000004: 0x41110000
	0x00000008: 0xeeadbeef
	0x0000000c: 0x41110000
""".lstrip()
                self.assertEqual(output, answer)

                program = \
"""
                and  r1 r1 r1
                and  r1 r1 r1
label:          and  r1 r1 r1
                and  r1 r1 r1

                COPY 0xdeadbeef r13

                STORE r13 + 0x10000000 label

                stop
"""
                output = get_output(program)
                output = output.decode()
                beg    = output.find("memory")
                end    = output.find("	0x00000010: ")
                output = output[beg:end]
                answer = \
"""
memory:

	0x00000000: 0x41110000
	0x00000004: 0x41110000
	0x00000008: 0xeeadbeef
	0x0000000c: 0x41110000
""".lstrip()
                self.assertEqual(output, answer)

        def test_JUMP(self):
                program = \
"""
                copy 0x12 r12
                copy 0x13 r13
                copy 0x14 r14
                copy 0x15 r15
                JUMP label
                copy 0x22 r12
                copy 0x23 r13
                copy 0x24 r14
                copy 0x25 r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000012
	r13: 0x00000013
	r14: 0x00000014
	r15: 0x00000015
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy label   r11
                copy 0x13    r13
                copy 0x14    r14
                copy 0x15    r15
                JUMP r11 - 8
                copy 0x22    r12
                copy 0x23    r13
                copy 0x24    r14
                copy 0x25    r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000000
	r13: 0x00000013
	r14: 0x00000024
	r15: 0x00000025
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy  0x1c r12
                copy  0x0  r13
                zjump r13  r12
                copy  0x12 r12
                copy  0x13 r13
                copy  0x14 r14
                stop
label:          JUMP  0xc
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000012
	r13: 0x00000013
	r14: 0x00000014
	r15: 0x00000000
""".strip()
                self.assertEqual(output, answer)

        def test_ZJUMP(self):
                program = \
"""
                copy  0x12 r12
                copy  0x13 r13
                copy  0x14 r14
                copy  0x15 r15
                ZJUMP 0x0  label
                copy  0x22 r12
                copy  0x23 r13
                copy  0x24 r14
                copy  0x25 r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000012
	r13: 0x00000013
	r14: 0x00000014
	r15: 0x00000015
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy  label r11
                copy  0x13  r13
                copy  0x14  r14
                copy  0x15  r15
                ZJUMP 0x0   r11 - 8
                copy  0x22  r12
                copy  0x23  r13
                copy  0x24  r14
                copy  0x25  r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000000
	r13: 0x00000013
	r14: 0x00000024
	r15: 0x00000025
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy  0x1c r12
                copy  0x0  r13
                zjump r13  r12
                copy  0x12 r12
                copy  0x13 r13
                copy  0x14 r14
                stop
label:          ZJUMP 0x0  0xc
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000012
	r13: 0x00000013
	r14: 0x00000014
	r15: 0x00000000
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy  0x0  r12
                copy  0x13 r13
                copy  0x14 r14
                copy  0x15 r15
                ZJUMP r12  label
                copy  0x22 r12
                copy  0x23 r13
                copy  0x24 r14
                copy  0x25 r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000000
	r13: 0x00000013
	r14: 0x00000014
	r15: 0x00000015
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy  label      r11
                copy  0x13       r13
                copy  0x14       r14
                copy  0x15       r15
                ZJUMP r13 - 0x13 r11 - 8
                copy  0x22       r12
                copy  0x23       r13
                copy  0x24       r14
                copy  0x25       r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000000
	r13: 0x00000013
	r14: 0x00000024
	r15: 0x00000025
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy  label      r11
                copy  0x13       r13
                copy  0x14       r14
                copy  0x15       r15
                ZJUMP r13 - 0xab r11 - 8
                copy  0x22       r12
                copy  0x23       r13
                copy  0x24       r14
                copy  0x25       r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000022
	r13: 0x00000023
	r14: 0x00000024
	r15: 0x00000025
""".strip()
                self.assertEqual(output, answer)

        def test_GJUMP(self):
                program = \
"""
                copy  0x12    r12
                copy  0x13    r13
                copy  0x14    r14
                copy  0x15    r15
                GJUMP r13 r12 label
                copy  0x22    r12
                copy  0x23    r13
                copy  0x24    r14
                copy  0x25    r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000012
	r13: 0x00000013
	r14: 0x00000014
	r15: 0x00000015
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy  0x12 r12
                copy  0x13 r13
                copy  0x14 r14
                copy  0x15 r15
                GJUMP 0x88 0x77 label
                copy  0x22 r12
                copy  0x23 r13
                copy  0x24 r14
                copy  0x25 r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000012
	r13: 0x00000013
	r14: 0x00000014
	r15: 0x00000015
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy  label r11
                copy  0x13  r13
                copy  0x14  r14
                copy  0x15  r15
                GJUMP 0x15  0x14 r11 - 8
                copy  0x22  r12
                copy  0x23  r13
                copy  0x24  r14
                copy  0x25  r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000000
	r13: 0x00000013
	r14: 0x00000024
	r15: 0x00000025
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy  0x1c r12
                copy  0x0  r13
                zjump r13  r12
                copy  0x12 r12
                copy  0x13 r13
                copy  0x14 r14
                stop
label:          GJUMP 0x22 0x11 0xc
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000012
	r13: 0x00000013
	r14: 0x00000014
	r15: 0x00000000
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy  0x0  r12
                copy  0x13 r13
                copy  0x14 r14
                copy  0x15 r15
                GJUMP r13  0x12 label
                copy  0x22 r12
                copy  0x23 r13
                copy  0x24 r14
                copy  0x25 r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000000
	r13: 0x00000013
	r14: 0x00000014
	r15: 0x00000015
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy  label      r11
                copy  0x13       r13
                copy  0x14       r14
                copy  0x15       r15
                GJUMP r15 - 0x10 r13 - 0x10 r11 - 8
                copy  0x22       r12
                copy  0x23       r13
                copy  0x24       r14
                copy  0x25       r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000000
	r13: 0x00000013
	r14: 0x00000024
	r15: 0x00000025
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy  label      r11
                copy  0x13       r13
                copy  0x14       r14
                copy  0x15       r15
                GJUMP r13 - 0x10 r15 - 0x10 r11 - 8
                copy  0x22       r12
                copy  0x23       r13
                copy  0x24       r14
                copy  0x25       r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000022
	r13: 0x00000023
	r14: 0x00000024
	r15: 0x00000025
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy  label      r11
                copy  0x13       r13
                copy  0x14       r14
                copy  0x15       r15
                GJUMP r13 - 0x10 r13 - 0x10 r11 - 8
                copy  0x22       r12
                copy  0x23       r13
                copy  0x24       r14
                copy  0x25       r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000022
	r13: 0x00000023
	r14: 0x00000024
	r15: 0x00000025
""".strip()
                self.assertEqual(output, answer)

        def test_label_sys(self):
                importlib.reload(macros)

                output = macros.new_label()
                answer = ["_unique_1"]
                self.assertEqual(output, answer)

                macros.labels.append("_unique_2")
                output = macros.new_label()
                answer = ["_unique_3"]
                self.assertEqual(output, answer)

                for i in range(4, 101):
                        macros.new_label()
                output = macros.labels
                answer = ["_unique_{}".format(i) for i in range(1, 101)]
                self.assertEqual(output, answer)

        def test_PUSH(self):
                program = \
"""
                COPY  0x400            r1
                COPY  0xe123           r14
                PUSH  0xdeadbeef
                PUSH  r14
                PUSH  r14 + 0xabcd0000
                stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[output.find("	0x000003b0: "):].strip()
                answer = \
"""
	0x000003b0: 0x00000000
	0x000003b4: 0x00000000
	0x000003b8: 0x00000000
	0x000003bc: 0x00000000
	0x000003c0: 0x00000000
	0x000003c4: 0x00000000
	0x000003c8: 0x00000000
	0x000003cc: 0x00000000
	0x000003d0: 0x00000000
	0x000003d4: 0x00000000
	0x000003d8: 0x00000000
	0x000003dc: 0x00000000
	0x000003e0: 0x00000000
	0x000003e4: 0x00000000
	0x000003e8: 0x00000000
	0x000003ec: 0x00000000
	0x000003f0: 0x00000000
	0x000003f4: 0xabcde123
	0x000003f8: 0x0000e123
	0x000003fc: 0xdeadbeef
""".strip()
                self.assertEqual(output, answer)

        def test_POP(self):
                program = \
"""
                COPY  0x400            r1
                PUSH  0xdeadbeef
                PUSH  0x11223344
                PUSH  0xaabbccdd
                POP   r13
                POP   r14
                POP   r15
                stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000000
	r13: 0xaabbccdd
	r14: 0x11223344
	r15: 0xdeadbeef
""".strip()
                self.assertEqual(output, answer)

        def test_NOT(self):
                program = \
"""
                COPY  0x17       r12
                NOT   r12        r13
                NOT   0x45       r14
                NOT   r12 - 0x17 r15
                stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000017
	r13: 0xffffffe8
	r14: 0xffffffba
	r15: 0xffffffff
""".strip()
                self.assertEqual(output, answer)

        def test_GEJUMP(self):
                program = \
"""
                copy   0x12    r12
                copy   0x13    r13
                copy   0x14    r14
                copy   0x15    r15
                GEJUMP r13 r12 label
                copy   0x22    r12
                copy   0x23    r13
                copy   0x24    r14
                copy   0x25    r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000012
	r13: 0x00000013
	r14: 0x00000014
	r15: 0x00000015
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy   0x12 r12
                copy   0x13 r13
                copy   0x14 r14
                copy   0x15 r15
                GEJUMP 0x88 0x77 label
                copy   0x22 r12
                copy   0x23 r13
                copy   0x24 r14
                copy   0x25 r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000012
	r13: 0x00000013
	r14: 0x00000014
	r15: 0x00000015
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy   label r11
                copy   0x13  r13
                copy   0x14  r14
                copy   0x15  r15
                GEJUMP 0x15  0x14 r11 - 8
                copy   0x22  r12
                copy   0x23  r13
                copy   0x24  r14
                copy   0x25  r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000000
	r13: 0x00000013
	r14: 0x00000024
	r15: 0x00000025
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy   0x1c r12
                copy   0x0  r13
                zjump  r13  r12
                copy   0x12 r12
                copy   0x13 r13
                copy   0x14 r14
                stop
label:          GEJUMP 0x22 0x11 0xc
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000012
	r13: 0x00000013
	r14: 0x00000014
	r15: 0x00000000
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy   0x0  r12
                copy   0x13 r13
                copy   0x14 r14
                copy   0x15 r15
                GEJUMP r13  0x12 label
                copy   0x22 r12
                copy   0x23 r13
                copy   0x24 r14
                copy   0x25 r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000000
	r13: 0x00000013
	r14: 0x00000014
	r15: 0x00000015
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy   label      r11
                copy   0x13       r13
                copy   0x14       r14
                copy   0x15       r15
                GEJUMP r15 - 0x10 r13 - 0x10 r11 - 8
                copy   0x22       r12
                copy   0x23       r13
                copy   0x24       r14
                copy   0x25       r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000000
	r13: 0x00000013
	r14: 0x00000024
	r15: 0x00000025
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy   label      r11
                copy   0x13       r13
                copy   0x14       r14
                copy   0x15       r15
                GEJUMP r13 - 0x10 r15 - 0x10 r11 - 8
                copy   0x22       r12
                copy   0x23       r13
                copy   0x24       r14
                copy   0x25       r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000022
	r13: 0x00000023
	r14: 0x00000024
	r15: 0x00000025
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy   label      r11
                copy   0x13       r13
                copy   0x14       r14
                copy   0x15       r15
                GEJUMP r13 - 0x10 r13 - 0x10 r11 - 8
                copy   0x22       r12
                copy   0x23       r13
                copy   0x24       r14
                copy   0x25       r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000000
	r13: 0x00000013
	r14: 0x00000024
	r15: 0x00000025
""".strip()
                self.assertEqual(output, answer)

        def test_LJUMP(self):
                program = \
"""
                copy  0x12    r12
                copy  0x13    r13
                copy  0x14    r14
                copy  0x15    r15
                LJUMP r12 r13 label
                copy  0x22    r12
                copy  0x23    r13
                copy  0x24    r14
                copy  0x25    r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000012
	r13: 0x00000013
	r14: 0x00000014
	r15: 0x00000015
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy  0x12 r12
                copy  0x13 r13
                copy  0x14 r14
                copy  0x15 r15
                LJUMP 0x77 0x88 label
                copy  0x22 r12
                copy  0x23 r13
                copy  0x24 r14
                copy  0x25 r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000012
	r13: 0x00000013
	r14: 0x00000014
	r15: 0x00000015
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy  label r11
                copy  0x13  r13
                copy  0x14  r14
                copy  0x15  r15
                LJUMP 0x14  0x15 r11 - 8
                copy  0x22  r12
                copy  0x23  r13
                copy  0x24  r14
                copy  0x25  r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000000
	r13: 0x00000013
	r14: 0x00000024
	r15: 0x00000025
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy  0x1c r12
                copy  0x0  r13
                zjump r13  r12
                copy  0x12 r12
                copy  0x13 r13
                copy  0x14 r14
                stop
label:          LJUMP 0x11 0x22 0xc
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000012
	r13: 0x00000013
	r14: 0x00000014
	r15: 0x00000000
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy  0x0  r12
                copy  0x13 r13
                copy  0x14 r14
                copy  0x15 r15
                LJUMP r12  0x13 label
                copy  0x22 r12
                copy  0x23 r13
                copy  0x24 r14
                copy  0x25 r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000000
	r13: 0x00000013
	r14: 0x00000014
	r15: 0x00000015
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy  label      r11
                copy  0x13       r13
                copy  0x14       r14
                copy  0x15       r15
                LJUMP r13 - 0x10 r15 - 0x10 r11 - 8
                copy  0x22       r12
                copy  0x23       r13
                copy  0x24       r14
                copy  0x25       r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000000
	r13: 0x00000013
	r14: 0x00000024
	r15: 0x00000025
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy  label      r11
                copy  0x13       r13
                copy  0x14       r14
                copy  0x15       r15
                LJUMP r15 - 0x10 r13 - 0x10 r11 - 8
                copy  0x22       r12
                copy  0x23       r13
                copy  0x24       r14
                copy  0x25       r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000022
	r13: 0x00000023
	r14: 0x00000024
	r15: 0x00000025
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy  label      r11
                copy  0x13       r13
                copy  0x14       r14
                copy  0x15       r15
                LJUMP r13 - 0x10 r13 - 0x10 r11 - 8
                copy  0x22       r12
                copy  0x23       r13
                copy  0x24       r14
                copy  0x25       r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000022
	r13: 0x00000023
	r14: 0x00000024
	r15: 0x00000025
""".strip()
                self.assertEqual(output, answer)

        def test_LEJUMP(self):
                program = \
"""
                copy   0x12    r12
                copy   0x13    r13
                copy   0x14    r14
                copy   0x15    r15
                LEJUMP r12 r13 label
                copy   0x22    r12
                copy   0x23    r13
                copy   0x24    r14
                copy   0x25    r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000012
	r13: 0x00000013
	r14: 0x00000014
	r15: 0x00000015
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy   0x12 r12
                copy   0x13 r13
                copy   0x14 r14
                copy   0x15 r15
                LEJUMP 0x77 0x88 label
                copy   0x22 r12
                copy   0x23 r13
                copy   0x24 r14
                copy   0x25 r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000012
	r13: 0x00000013
	r14: 0x00000014
	r15: 0x00000015
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy   label r11
                copy   0x13  r13
                copy   0x14  r14
                copy   0x15  r15
                LEJUMP 0x14  0x15 r11 - 8
                copy   0x22  r12
                copy   0x23  r13
                copy   0x24  r14
                copy   0x25  r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000000
	r13: 0x00000013
	r14: 0x00000024
	r15: 0x00000025
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy   0x1c r12
                copy   0x0  r13
                zjump  r13  r12
                copy   0x12 r12
                copy   0x13 r13
                copy   0x14 r14
                stop
label:          LEJUMP 0x11 0x22 0xc
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000012
	r13: 0x00000013
	r14: 0x00000014
	r15: 0x00000000
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy   0x0  r12
                copy   0x13 r13
                copy   0x14 r14
                copy   0x15 r15
                LEJUMP 0x12 r13 label
                copy   0x22 r12
                copy   0x23 r13
                copy   0x24 r14
                copy   0x25 r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000000
	r13: 0x00000013
	r14: 0x00000014
	r15: 0x00000015
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy   label      r11
                copy   0x13       r13
                copy   0x14       r14
                copy   0x15       r15
                LEJUMP r13 - 0x10 r15 - 0x10 r11 - 8
                copy   0x22       r12
                copy   0x23       r13
                copy   0x24       r14
                copy   0x25       r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000000
	r13: 0x00000013
	r14: 0x00000024
	r15: 0x00000025
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy   label      r11
                copy   0x13       r13
                copy   0x14       r14
                copy   0x15       r15
                LEJUMP r15 - 0x10 r13 - 0x10 r11 - 8
                copy   0x22       r12
                copy   0x23       r13
                copy   0x24       r14
                copy   0x25       r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000022
	r13: 0x00000023
	r14: 0x00000024
	r15: 0x00000025
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy   label      r11
                copy   0x13       r13
                copy   0x14       r14
                copy   0x15       r15
                LEJUMP r13 - 0x10 r13 - 0x10 r11 - 8
                copy   0x22       r12
                copy   0x23       r13
                copy   0x24       r14
                copy   0x25       r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000000
	r13: 0x00000013
	r14: 0x00000024
	r15: 0x00000025
""".strip()
                self.assertEqual(output, answer)

        def test_EJUMP(self):
                program = \
"""
                copy   label      r11
                copy   0x13       r13
                copy   0x14       r14
                copy   0x15       r15
                EJUMP  r13 - 0x10 r13 - 0x10 r11 - 8
                copy   0x22       r12
                copy   0x23       r13
                copy   0x24       r14
                copy   0x25       r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000000
	r13: 0x00000013
	r14: 0x00000024
	r15: 0x00000025
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy   label      r11
                copy   0x13       r13
                copy   0x14       r14
                copy   0x15       r15
                EJUMP  r13 - 0x44 r13 - 0x77 r11 - 8
                copy   0x22       r12
                copy   0x23       r13
                copy   0x24       r14
                copy   0x25       r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000022
	r13: 0x00000023
	r14: 0x00000024
	r15: 0x00000025
""".strip()
                self.assertEqual(output, answer)

        def test_NEJUMP(self):
                program = \
"""
                copy    label      r11
                copy    0x13       r13
                copy    0x14       r14
                copy    0x15       r15
                NEJUMP  r13 - 0x44 r13 - 0x77 r11 - 8
                copy    0x22       r12
                copy    0x23       r13
                copy    0x24       r14
                copy    0x25       r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000000
	r13: 0x00000013
	r14: 0x00000024
	r15: 0x00000025
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy    label      r11
                copy    0x13       r13
                copy    0x14       r14
                copy    0x15       r15
                NEJUMP  r13 - 0x10 r13 - 0x10 r11 - 8
                copy    0x22       r12
                copy    0x23       r13
                copy    0x24       r14
                copy    0x25       r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000022
	r13: 0x00000023
	r14: 0x00000024
	r15: 0x00000025
""".strip()
                self.assertEqual(output, answer)

        def test_NZJUMP(self):
                program = \
"""
                copy   0x12 r12
                copy   0x13 r13
                copy   0x14 r14
                copy   0x15 r15
                NZJUMP 0xae label
                copy   0x22 r12
                copy   0x23 r13
                copy   0x24 r14
                copy   0x25 r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000012
	r13: 0x00000013
	r14: 0x00000014
	r15: 0x00000015
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy   label r11
                copy   0x13  r13
                copy   0x14  r14
                copy   0x15  r15
                NZJUMP 0xb3  r11 - 8
                copy   0x22  r12
                copy   0x23  r13
                copy   0x24  r14
                copy   0x25  r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000000
	r13: 0x00000013
	r14: 0x00000024
	r15: 0x00000025
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy   0x1c r12
                copy   0x0  r13
                zjump  r13  r12
                copy   0x12 r12
                copy   0x13 r13
                copy   0x14 r14
                stop
label:          NZJUMP 0x9a 0xc
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000012
	r13: 0x00000013
	r14: 0x00000014
	r15: 0x00000000
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy   0xe2 r12
                copy   0x13 r13
                copy   0x14 r14
                copy   0x15 r15
                NZJUMP r12  label
                copy   0x22 r12
                copy   0x23 r13
                copy   0x24 r14
                copy   0x25 r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x000000e2
	r13: 0x00000013
	r14: 0x00000014
	r15: 0x00000015
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy   label      r11
                copy   0x13       r13
                copy   0x14       r14
                copy   0x15       r15
                NZJUMP r13 - 0xa3 r11 - 8
                copy   0x22       r12
                copy   0x23       r13
                copy   0x24       r14
                copy   0x25       r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000000
	r13: 0x00000013
	r14: 0x00000024
	r15: 0x00000025
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                copy   label      r11
                copy   0x13       r13
                copy   0x14       r14
                copy   0x15       r15
                NZJUMP r13 - 0x13 r11 - 8
                copy   0x22       r12
                copy   0x23       r13
                copy   0x24       r14
                copy   0x25       r15
label:          stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000022
	r13: 0x00000023
	r14: 0x00000024
	r15: 0x00000025
""".strip()
                self.assertEqual(output, answer)

        def test_XOR(self):
                program = \
"""
                COPY  0x17                   r12
                XOR   r12       0x24         r13
                XOR   0x45      0xaa         r14
                XOR   r12 - 0xa r14 + 0xabcd r15
                stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000017
	r13: 0x00000033
	r14: 0x000000ef
	r15: 0x0000acb1
""".strip()
                self.assertEqual(output, answer)

        def test_NEG(self):
                program = \
"""
                COPY  0x17       r12
                NEG   r12        r13
                NEG   0xdeadbeef r14
                NEG   r12 - 0xa  r15
                stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000017
	r13: 0xffffffe9
	r14: 0x21524111
	r15: 0xfffffff3
""".strip()
                self.assertEqual(output, answer)

                program = \
"""
                NEG   0x0        r12
                NEG   0x1        r13
                NEG   0xffffffff r14
                stop
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000000
	r13: 0xffffffff
	r14: 0x00000001
	r15: 0x00000000
""".strip()
                self.assertEqual(output, answer)

        def test_CALL(self):
                program = \
"""
                COPY  0x400 r1
                CALL  adder 0x2 0x4 0x6
                stop

adder:          POP   r12
                POP   r13
                POP   r14

                ADD   r12   r13 r15
                ADD   r15   r14 r15
                POP   r11
                JUMP  r11
"""
                output = get_output(program)
                output = output.decode()
                output = output[:output.find("memory")].strip()[30 + 11 * 17:]
                answer = \
"""
	r12: 0x00000002
	r13: 0x00000004
	r14: 0x00000006
	r15: 0x0000000c
""".strip()
                self.assertEqual(output, answer)

unittest.main()
