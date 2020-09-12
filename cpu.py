"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256 # Hold 256 bytes of memory 
        self.reg = [0] * 8 # Hold 8 general-purpose registers
        self.reg[7] = 0xF4
        self.pc = 0 
        self.fl = 0b00000000
        self.branch_table = {
            0b10000010: self.LDI,  
            0b01000111: self.PRN, 
            0b00000001: self.HLT,  
            0b10100010: self.MUL, 
            0b10100000: self.ADD, 
            0b01000101: self.PUSH,
            0b01000110: self.POP,
            0b01010000: self.CALL,
            0b00010001: self.RET,
            0b10100111: self.CMP,
            0b01010100: self.JMP,
            0b01010101: self.JEQ,
            0b01010110: self.JNE,
            0b10101000: self.AND,  
            0b10101010: self.OR,
            0b10101011: self.XOR
        }


    # Accept the address to read and return the value stored there
    def ram_read(self, MAR):
        return self.ram[MAR]

    # Accept a value to write, and the address to write it to
    def ram_write(self, MDR, MAR):
        self.ram[MAR] = MDR

    # Load / Set a specified register to a specified value
    def LDI(self): 
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.reg[operand_a] = operand_b
        self.pc += 3
   
   # Print numeric value store in a register
    def PRN(self): 
        operand_a = self.ram_read(self.pc + 1)
        print(self.reg[operand_a])
        self.pc += 2

    # Halt the CPU and exit the emulator
    def HLT(self): 
        sys.exit()
        self.pc += 1

    # Multiply the values in 2 registers
    def MUL(self): 
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu('MUL', operand_a, operand_b)
        self.pc += 3

    # Add the values in 2 registers
    def ADD(self): 
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu('ADD', operand_a, operand_b)
        self.pc += 3

    def PUSH(self): 
        given_register = self.ram[self.pc + 1]
        value_in_register = self.reg[given_register]
        # decrement the stack pointer
        self.reg[7] -= 1
        # write the value at the given register to memory at the stack pointer location
        self.ram[self.reg[7]] = value_in_register
        self.pc += 2

    def POP(self): 
        given_register = self.ram[self.pc + 1]
        # write the value in memory at the top of the stack to the given register
        value_from_memory = self.ram[self.reg[7]]
        self.reg[given_register ] = value_from_memory
        # increment the stack pointer
        self.reg[7] += 1
        self.pc += 2
  
    def CALL(self): 
        # get the given register in the operand
        given_register = self.ram[self.pc + 1]
        # store the return address (self.pc + 2) onto the stack and decrement the SP
        self.reg[7] -= 1
        # write the return address
        self.ram[self.reg[7]] = self.pc + 2
        # set pc to value inside given_regrister
        self.pc = self.reg[given_register]
    
    def RET(self): 
        # set pc to value at the top of the stack
        self.pc = self.ram[self.reg[7]]
        # pop from the stack 
        self.reg[7] += 1

    def CMP(self): 
        # Compare the values in two registers
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu('CMP', operand_a, operand_b)
        self.pc += 3

    def JMP(self): 
        # jump to the address stored in the given register
        given_register = self.ram[self.pc + 1]
        # set pc to the address stored in the given register
        self.pc = self.reg[given_register]
 
    def JEQ(self): 
        # if `equal` flag is set true
        # jump to the address stored in the given register
        given_register = self.ram[self.pc + 1]
        if self.fl & 0b00000001 == 1:
            self.pc = self.reg[given_register]
        else:
            self.pc += 2
 
    def JNE(self): 
        # if `E` flag is false
        # jump to the address stored in the given
        given_register = self.ram[self.pc + 1]
        if self.fl & 0b00000001 == 0:
            self.pc = self.reg[given_register]
        else:
            self.pc += 2

    def AND(self): 
        operand_a = self.reg[self.ram_read(self.pc + 1)]
        operand_b = self.reg[self.ram_read(self.pc + 2)]
        self.reg[self.ram_read(self.pc + 1)] = (operand_a & operand_b)
        self.pc += 3

    def OR(self): 
        operand_a = self.reg[self.ram_read(self.pc + 1)]
        operand_b = self.reg[self.ram_read(self.pc + 2)]
        self.reg[self.ram_read(self.pc + 1)] = (operand_a | operand_b)
        self.pc += 3

    def XOR(self): 
        operand_a = self.reg[self.ram_read(self.pc + 1)]
        operand_b = self.reg[self.ram_read(self.pc + 2)]
        self.reg[self.ram_read(self.pc + 1)] = (operand_a ^ operand_b)
        self.pc += 3

    def load(self):
        """Load a program into memory."""
        if len(sys.argv) < 2:
            print('second filename missing')
            sys.exit(1)
    
        filename = sys.argv[1]
        try:  
            address = 0
            with open(filename) as file:
                for line in file:
                    split_line = line.split('#') # split line on # symbol
                    code_value = split_line[0].strip() # remove white space and /n character
                    if code_value == '':
                        continue
                    instruction = int(code_value, 2)
                    self.ram[address] = instruction
                    address += 1
        except FileNotFoundError:
            print(f'{sys.argv[1]} file not found')
            sys.exit(2)

    # Math operations
    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == "CMP":
            # 00000LGE flags
            if self.reg[reg_a] == self.reg[reg_b]:
                # set E flag = 1
                self.fl = 0b00000001
            elif self.reg[reg_a] > self.reg[reg_b]:
                # set G flag = 1
                self.fl = 0b00000010
            elif self.reg[reg_a] < self.reg[reg_b]:
                # L flag = 1
                self.fl = 0b00000100 
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')
        print()

    def run(self):
        """Run the CPU."""
        running = True
        while running:
            IR = self.ram[self.pc] 
            if IR in self.branch_table:
                self.branch_table[IR]()

# py -3 ls8.py sctest.ls8

# py -3 ls8.py examples/mult.ls8
# py -3 ls8.py examples/stack.ls8
# py -3 ls8.py examples/and.ls8
# py -3 ls8.py examples/or.ls8
# py -3 ls8.py examples/xor.ls8

# print(int(0b00001000 & 0b00001001))
# print(int(0b00001000 | 0b00001001))
# print(int(0b00001000 ^ 0b00001001))