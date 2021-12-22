#CEA MAI BUNA ECHIPA
def read_file(file_name):
    instruction_codes = []
    last_address = int("80000000", 16)
    with open(file_name, "r") as f:
        f.readline()
        for line in f.readlines():
            try:
                address, instruction_code = line.split()
            except:
                continue
            if instruction_code[0] != "<":
                for i in range(0, 4):
                    instruction_codes.append(int(instruction_code[i * 2:(i+1)*2], 16))
                # if instruction_code == "80000000":
                #     instruction_codes.extend([0] * 8)
                if address != "800029e0:":
                    address = int(address[:-1], 16)
                    if (address - last_address) > 4:
                        instruction_codes.extend([0] * (address - last_address - 4))
                    last_address = address
                else:
                    address = int(address[:-1], 16)
                    last_address = address
                
    return bytearray(instruction_codes)

def complement_two(nr):
    string = bin(nr)[3:]
    string = "0" * (32 - len(string)) + string
    s = []
    for ch in (string):
        s.append(int(ch) ^ 1)
    s = "".join([str(x) for x in s])
    decimal = int(s, 2) + 1
    s = bin(decimal)[2:]
    if len(s) > 32:
        s = s [1:]
    return s


def my_bin(x):
    return "0" * (8 - len(bin(x)[2:])) + bin(x)[2:] 

def rev(string):
    return string[::-1]

def sign_extend(string):
    if string[0] == "1":
        return "1" * (32 - len(string)) + string
    return "0" * (32 - len(string)) + string

def ADD(a, b):
    s = [0] * 32
    carry = 0
    i = 31
    while i >= 0:
        s[i] = (int(a[i]) ^ int(b[i]) ^ carry) 
        carry = ((int(a[i]) & int(b[i])) | ((int(a[i]) | int(b[i])) & carry))
        i -= 1
    # print(s)
    return "".join([str(x) for x in s])


def OR(a, b):
    s = []
    for i in range(32):
        s.append(int(a[i]) | int(b[i]))
    return "".join([str(x) for x in s])

def SLL(a, shamt):
    s = a[shamt:] + "0" * shamt
    return "".join([str(x) for x in s])


def LUI(a):
    s = a + "0" * 12
    return s 


def BNE(imm1, imm2, value1, value2, program_counter):
    if value1 == value2:
        return program_counter
    imm = imm2[0] + imm1[-1] + imm2[1:] + imm1[:-1]
    offset = (int(imm[1: ], 2) - (2 ** (len(imm) - 1)) * int(imm[0])) * 2 
    return program_counter + offset - 4
    

def BEQ(imm1, imm2, value1, value2, program_counter):
    if value1 != value2:
        return program_counter
    imm = imm2[0] + imm1[-1] + imm2[1:] + imm1[:-1]
    offset = (int(imm[1:], 2) - (2 ** (len(imm) - 1)) * int(imm[0])) * 2 
    return program_counter + offset - 4

def JAL(imm, rd, program_counter):
    # bitul de semn
    new_imm = imm[0] + imm[12:] + imm[11] + imm[1:11]
    offset = int(new_imm, 2) * 2
    # print("offset = ", offset)
    return program_counter + offset

def SRL(nr, reg_shamt):
    shamt = (int(reg_shamt[1:], 2) - (2 ** (len(reg_shamt) - 1)) * int(reg_shamt[0]))
    shamt = shamt % 32
    if shamt != 0:
        s = "0" * shamt + nr[:-shamt]
        return s
    else:
        return nr

def XOR(a, b):
    s = []
    for i in range(32):
        s.append(int(a[i]) ^ int(b[i]))
    return "".join([str(x) for x in s])
    
def REM(a, b):
    a = (int(a[1:], 2) - (2 ** (len(a) - 1)) * int(a[0]))
    b = (int(b[1:], 2) - (2 ** (len(b) - 1)) * int(b[0]))
    rest = a % b
    if (a * b) < 0:
        rest = rest - b
        return complement_two(rest)
    return "0" * (32 - len(bin(rest)[2:])) + bin(rest)[2:] 

def AUIPC(imm, program_counter):
    start_address = int("80000000", 16)
    s = imm + "0" * 12
    offset = (int(s[1: ], 2) - (2 ** (len(s) - 1)) * int(s[0]))
    offset2 = 10584
    s = bin(offset + program_counter + start_address + offset2 - 4)[2:]
    return "0" * (32 - len(s)) + s, program_counter


def SW(imm, base, value, byte_array):
    start_address = int("80000000", 16)
    offset = (int(imm[1: ], 2) - (2 ** (len(imm) - 1)) * int(imm[0]))
    source_address = int(base, 2)
    offset2 = 10584
    dest_address = offset + source_address
    ct = dest_address - start_address - offset2
    for i in range(0, 4):
        byte_array[ct + i] = int(value[i * 8:(i + 1) * 8], 2) 


def LW(imm, base, byte_array):
    start_address = int("80000000", 16)
    offset2 = 10584
    offset = (int(imm[1:], 2) - (2 ** (len(imm) - 1)) * int(imm[0]))
    base = int(base, 2)
    source_address = offset + base - start_address - offset2
    s = []
    for i in range(0, 4):
        b = bin(byte_array[source_address + i])[2:]
        s.append("0" * (8 - len(b)) + b)
    s = "".join(s)
    return s
    


def instruction_fetch(byte_array, program_counter):
    return program_counter + 4, byte_array[program_counter:program_counter + 4]


def instruction_decode(instruction_code):
    instr = ""
    for hex in instruction_code:
        instr += my_bin(hex)
    instr = instr[::-1]
                
    if instr == "11001110000000000000000000000000": # ecall
        return ("ecall",)
    if instr == "11001110000010000000000000000011": # unimp 
        return ("unimp",)
    if instr == "11001000000000000000000000000000":
        return ("nop",)
    opcode = instr[0:7]
    funct3 = instr[12:15]
    funct7 = instr[25:]
    if opcode == "1100100" and funct3 == "000": # addi
        rd = int(rev(instr[7:12]), 2)
        rs1 = int(rev(instr[15:20]), 2)
        imm = rev(instr[20:])
        return ("addi", imm, rs1, rd)
    if opcode == "1100100" and funct3 == "011": # ori
        rd = int(rev(instr[7:12]), 2)
        rs1 = int(rev(instr[15:20]), 2)
        imm = rev(instr[20:])
        return ("ori", imm, rs1, rd)
    if opcode == "1100100" and funct3 == "100" and funct7 == "0000000": # slli
        rd = int(rev(instr[7:12]), 2)
        rs1 = int(rev(instr[15:20]), 2)
        shamt = int(rev(instr[20:25]), 2)
        return ("slli", shamt, rs1, rd)
    if opcode == "1110110": # lui
        rd = int(rev(instr[7:12]), 2)
        imm = rev(instr[12:])
        return ("lui", imm, rd)
    if opcode == "1100011" and funct3 == "100": # bne
        imm1 = rev(instr[7:12])
        rs1 = int(rev(instr[15:20]), 2)
        rs2 = int(rev(instr[20:25]), 2)
        imm2 = rev(instr[25:])
        return ("bne", imm1, imm2, rs1, rs2)
    if opcode == "1100011" and funct3 == "000": # beq
        imm1 = rev(instr[7:12])
        rs1 = int(rev(instr[15:20]), 2)
        rs2 = int(rev(instr[20:25]), 2)
        imm2 = rev(instr[25:])
        return ("beq", imm1, imm2, rs1, rs2)
    if opcode == "1111011": # jal
        imm = rev(instr[12:])
        rd = int(rev(instr[7:12]))
        return ("jal", imm, rd)
    if opcode == "1100110" and funct3 == "101" and funct7 == "0000000": # srl
        rd = int(rev(instr[7:12]), 2)
        rs1 = int(rev(instr[15:20]), 2)
        rs2 = int(rev(instr[20:25]), 2) 
        return ("srl", rs2, rs1, rd)
    if opcode == "1100110" and funct3 == "001" and funct7 == "0000000": # xor
        rd = int(rev(instr[7:12]), 2)
        rs1 = int(rev(instr[15:20]), 2)
        rs2 = int(rev(instr[20:25]), 2)
        return ("xor", rs2, rs1, rd)
    if opcode == "1100110" and funct3 == "011" and funct7 == "1000000": # rem
        rd = int(rev(instr[7:12]), 2)
        rs1 = int(rev(instr[15:20]), 2)
        rs2 = int(rev(instr[20:25]), 2)
        return ("rem", rs2, rs1, rd)
    if opcode == "1110100": # auipc
        rd = int(rev(instr[7:12]), 2)
        imm = rev(instr[12:])
        return ("auipc", imm, rd)
    if opcode == "1100010" and funct3 == "010": #sw
        imm1 = rev(instr[7:12])
        rs1 = int(rev(instr[15:20]), 2)
        rs2 = int(rev(instr[20:25]), 2)
        imm2 = rev(instr[25:])
        return ("sw", imm1, imm2, rs1, rs2)
    if opcode == "1100000" and funct3 == "010": #lw
        rd = int(rev(instr[7:12]), 2)
        rs1 = int(rev(instr[15:20]), 2)
        imm = rev(instr[20:])
        return ("lw", imm, rs1, rd)



def write_back(register_file, reg, value):
    register_file[reg] = value

        
def execute(register_file, instr, program_counter, byte_array):
    if instr[0] == "ecall":
        return "exit", program_counter # s-ar putea sa trebuiasca sa facem ceva in functie de valorile din registri
    if instr[0] == "unimp":
        return "exit", program_counter
    if instr[0] == "addi":
        imm, rs1, rd = instr[1:]
        # exception when destination register is zero
        if rd == 0:
            rs1, rd = rd, rs1
        # print(sign_extend(register_file[rs1]), sign_extend(imm))
        register_file[rd] = ADD(sign_extend(register_file[rs1]), sign_extend(imm))
        return None, program_counter
    if instr[0] == "ori":
        imm, rs1, rd = instr[1:]
        register_file[rd] = OR(sign_extend(register_file[rs1]), sign_extend(imm))
        return None, program_counter
    if instr[0] == "slli":
        shamt, rs1, rd = instr[1:]
        register_file[rd] = SLL(sign_extend(register_file[rs1]), shamt)
        return None, program_counter
    if instr[0] == "lui":
        imm, rd = instr[1:]
        register_file[rd] = LUI(imm)
        return None, program_counter
    if instr[0] == "bne":
        imm1, imm2, rs1, rs2 = instr[1:]
        program_counter = BNE(imm1, imm2, register_file[rs1], register_file[rs2], program_counter)
        return None, program_counter
    if instr[0] == "beq":
        imm1, imm2, rs1, rs2 = instr[1:]
        program_counter = BEQ(imm1, imm2, register_file[rs1], register_file[rs2], program_counter)
        return None, program_counter
    if instr[0] == "jal":
        # print(instr)
        imm, rd = tuple(instr[1:])
        program_counter = JAL(imm, rd, program_counter)
        return None, program_counter
    if instr[0] == "srl":
        rs2, rs1, rd = instr[1:]
        if rd == 0:
            print("ExceptionError: zero register can not be destination")
            return None, program_counter
        # TREBUIE SA TRATAM EXCEPTIA SRL ZERO
        register_file[rd] = SRL(sign_extend(register_file[rs1]), sign_extend(register_file[rs2]))
        return None, program_counter
    if instr[0] == "nop":
        return None, program_counter
    if instr[0] == "xor":
        rs2, rs1, rd = instr[1:]
        if rd == 0:
            print("ExceptionError: zero register can not be destination")
            return None, program_counter
        register_file[rd] = XOR(sign_extend(register_file[rs1]), sign_extend(register_file[rs2]))
        return None, program_counter
    if instr[0] == "rem":
        rs2, rs1, rd = instr[1:]
        register_file[rd] = REM(sign_extend(register_file[rs1]), sign_extend(register_file[rs2]))
        return None, program_counter
    if instr[0] == "auipc":
        imm, rd = instr[1:]
        register_file[rd], program_counter = AUIPC(imm, program_counter)
        return None, program_counter
    if instr[0] == "sw":
        imm1, imm2, rs1, rs2 = instr[1:]
        imm = imm2 + imm1
        SW(imm, register_file[rs1], sign_extend(register_file[rs2]), byte_array)
        return None, program_counter
    if instr[0] == "lw":
        imm, rs1, rd = instr[1:]
        register_file[rd] = LW(imm, register_file[rs1], byte_array)
        return None, program_counter

    

def main():
    byte_array = read_file("rv32ui-v-sw.mc")
    # print(byte_array)
    # print(len(byte_array))
    program_counter = 0
    register_file = ["0" * 32] * 32

    while True:
        program_counter, instruction_code = instruction_fetch(byte_array, program_counter)
        # print(instruction_code, program_counter)
        instruction = instruction_decode(instruction_code)
        # print(instruction)
        message, program_counter = execute(register_file, instruction, program_counter, byte_array)
        # print(*[int(x, 2) for x in register_file])
        if message == "exit":
            break
    print(int(register_file[3], 2))


if __name__ == "__main__":
    main()

# Probleme deschise si teme de dezbatut: 
# 1. ecall si unimp
# 2. registrul zero pe post de destinatie
# 3. continuam cautarile
# 20.12.2021:
# addi
# srl
# xor
# beq
# to be continued
# va asteptam si maine!!