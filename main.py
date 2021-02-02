from collections import deque

PC = 0
number_of_registers = 0
instruction_window_size = 0
program = []
finished = False


class Instruction(object):
    def __init__(self, adrs, op, dest, s1, s2=None):
        self.adress = adrs
        self.opname = op
        self.destination = dest
        self.source1 = s1
        self.source2 = s2

    def toString(self):
        st = ''
        if self.opname == 'LD':
            st = self.opname + '  ' + str(self.destination) + ', ' + str(self.source1)
        elif self.opname =='BGE':
            st = self.opname + ' ' + str(self.source1) + ', ' + str(self.source2) + ', ' + str(self.destination)
        else:
            st = self.opname + ' ' + self.destination + ', ' + str(self.source1) + ', ' + str(self.source2)
        return st


class InstructionQueue(object):
    def __init__(self, window_size):
        self.instructions = deque()
        self.window_size = window_size

    def add(self, instruction):
        self.instructions.append(instruction)

    def isEmpty(self):
        if len(self.instructions) == 0:
            return True
        else:
            return False

    def isFull(self):
        if len(self.instructions) == self.window_size:
            return True
        else:
            return False

    def head(self):
        return self.instructions[0]

    def pop(self):
        return self.instructions.popleft()

    def clear(self):
        self.instructions = deque()

    def toString(self):
        st = "Instruction Window\n"
        for i in self.instructions:
            st += i.toString() + '\n'
        return st


class ReservationStation(object):
    def __init__(self):
        self.opName = ''
        self.busy = False
        self.Vj = None
        self.Vk = None
        self.Qj = None
        self.Qk = None
        self.destination = None
        self.cyclesRemained = None

    def clear(self):
        self.opName = ''
        self.busy = False
        self.Vj = None
        self.Vk = None
        self.Qj = None
        self.Qk = None
        self.destination = None
        self.cyclesRemained = None

    def execute(self):
        if self.opName == 'ADD':
            return self.Vj + self.Vk
        elif self.opName == 'SUB':
            return self.Vj - self.Vk
        elif self.opName == 'MUL':
            return self.Vj * self.Vk
        elif self.opName == 'DIV':
            return self.Vj / self.Vk
        elif self.opName == 'LD':
            return self.Vj

    def toString(self):
        st = ' '
        if self.busy:
            st = self.opName + ' '
            if self.opName == 'LD':
                st += ' '
            if self.Vj is None:
                st += self.Qj + ' '
            else:
                st += str(self.Vj) + '  '
            if self.Vk is None:
                if self.Qk is None:
                    st += '-  '
                else:
                    st += self.Qk + ' '
            else:
                st += str(self.Vk) + '  '
            st += self.destination
        return st


class RegisterFile(object):
    def __init__(self, num_of_registers):
        self.size = num_of_registers
        self.registerList = [Register(i) for i in range(num_of_registers)]

    def flush(self,list):
        for register in self.registerList:
            for name in list:
                if register.robId == name:
                    register.clear()

    def toString(self):
        st = 'Registers\n'
        for reg in self.registerList:
            st += reg.toString() + '\n'
        return st


class Register(object):
    def __init__(self, i):
        self.name = 'R' + str(i)
        self.value = None
        self.robId = None
        self.busy = False

    def clear(self):
        self.robId = None
        self.busy = False

    def toString(self):
        st = self.name + ': '
        if self.value is None:
            st += '-   '
        else:
            st += str(self.value) + ' '
        if self.robId is None:
            st += '-'
        else:
            st += self.robId
        return st


class ReorderBuffer(object):
    def __init__(self, size=5):
        self.size = size
        self.head = 0
        self.tail = -1
        self.list = [ReorderBufferEntry(i) for i in range(self.size)]
        self.numelements = 0

    def isFull(self):
        if self.numelements == self.size:
            return True
        else:
            return False

    def createRoBEntry(self, i):
        index = self.tail + 1
        index %= self.size
        self.list[index].opname = i.opname
        self.list[index].destination = i.destination
        self.list[index].busy = True
        self.tail += 1
        self.tail %= self.size
        self.numelements += 1
        return self.list[index].name

    def gethead(self):
        return self.list[self.head]

    def pop(self):
        self.list[self.head].clear()
        self.head += 1
        self.head %= self.size
        self.numelements -= 1

    def flush(self, destination):
        index = 0
        for entry in self.list:
            if entry.name == destination:
                index = self.list.index(entry)
                break

        listtoremove = []
        while (self.tail - index) % self.size != 0:
            index += 1
            index %= self.size
            listtoremove.append(self.list[index].name)
            self.list[index].clear()

        self.tail -= len(listtoremove)
        self.tail %= self.size
        self.numelements -= len(listtoremove)
        return listtoremove

    def toString(self):
        st = 'Reorder Buffer\n'
        i = 0
        for entry in self.list:
            st += entry.toString()
            if i == self.head:
                st += ' (H)'
            if i == self.tail:
                st += ' (T)'
            st += '\n'
            i += 1
        return st

    def findlastentry(self, register):
        index = self.tail
        for i in range(ROB.numelements):
            if self.list[index].destination == register.name:
                return self.list[index]
            index -= 1
            index %= self.size
        return None


class ReorderBufferEntry(object):
    def __init__(self, i):
        self.name = 'ROB' + str(i)
        self.opname = ''
        self.busy = False
        self.ready = False
        self.destination = ''
        self.value = None

    def clear(self):
        self.opname = ''
        self.busy = False
        self.ready = False
        self.destination = ''
        self.value = None

    def toString(self):
        st = self.name + ': '
        if self.ready:
            st += self.opname + ' '
            if self.opname == 'LD':
                st += ' '
            st += self.destination + ' ' + str(self.value)
        elif self.busy:
            st += self.opname + ' '
            if self.opname == 'LD':
                st += ' '
            st += self.destination + ' -'
        return st


class FunctionalUnit(object):
    def __init__(self, supportedIns, cyclenums):
        self.supportedInstructions = supportedIns
        self.cycles = cyclenums
        self.reservationStation = ReservationStation()

    def clear (self):
        self.reservationStation = ReservationStation()


class CommonDataBus(object):
    def __init__(self):
        self.value = None
        self.address = None
        self.busy = False

    def toString(self):
        st ='Common Data Bus\n'
        if self.busy:
            st += str(self.value) + ' ' + self.address
        return st


class FunctionalUnits(object):
    def __init__(self):
        self.fuList = []

    def add(self, fu):
        self.fuList.append(fu)

    def findAvailable(self, opname):
        for funtionalunit in self.fuList:
            if not funtionalunit.reservationStation.busy:
                if opname in funtionalunit.supportedInstructions:
                    return funtionalunit
        return False

    def isAvailable(self, opname):
        for fu in self.fuList:
            if opname in fu.supportedInstructions:
                if not fu.reservationStation.busy:
                    return True
        return False

    def flush(self,list):
        for fu in self.fuList:
            for robId in list:
                rs = fu.reservationStation
                if rs.Qj == robId or rs.Qk == robId or rs.destination == robId:
                    fu.clear()

    def toString(self):
        st = 'Reservation Stations\n'
        i = 0
        for fu in self.fuList:
            st += 'RS' + str(i) + ': ' + fu.reservationStation.toString() + '\n'
            i += 1
        return st




def read_parameters_file():
    global number_of_registers, instruction_window_size
    parameters_file = open("Parameters.txt", 'r')
    for line in parameters_file.readlines():
        args = line.split()
        if args[0] == 'number_of_registers:':
            number_of_registers = int(args[1])
        elif args[0] == 'instruction_window_size:':
            instruction_window_size = int(args[1])


def read_units_file():
    units_file = open("Units.txt", 'r')
    for line in units_file.readlines():
        args = line.split()
        if args[0] == '#':
            pass
        elif len(args) == 0:
            pass
        else:
            supported_instructions = args[1].split(',')
            cycles = int(args[2])
            FU.add(FunctionalUnit(supported_instructions, cycles))


def read_program_file():
    program_file = open("Program.txt", 'r')
    for line in program_file.readlines():
        args = line.split()
        if args[0] == '#':
            pass
        elif len(args) == 0:
            pass
        else:
            adress = int(args[0].split(':')[0])
            opname = args[1]
            destination = args[2].split(',')[0]
            source1 = args[3].split(',')[0]
            if opname == 'LD':
                instruction = Instruction(adress, opname, destination, source1)
            elif opname == 'BGE':
                instruction = Instruction(adress, opname, args[4], destination, source1)
            else:
                source2 = args[4]
                instruction = Instruction(adress, opname, destination, source1, source2)
            program.append(instruction)


def fetch():
    global PC
    while IQ.isFull() is False and int(PC) < 4 * len(program) and PC != -1:
        for i in program:
            if i.adress == PC:
                IQ.add(i)
                if i.opname == 'BGE':
                    PC = int(i.destination)
                else:
                    PC = PC + 4
                break


def issue():
    if ROB.isFull() is False and PC != -1 and FU.isAvailable(IQ.head().opname):
        inst = IQ.pop()
        fu = FU.findAvailable(inst.opname)
        find = False
        for register in RF.registerList:
            if register.name == inst.source1:
                if register.busy:
                    h = ROB.findlastentry(register)
                    # for robEntry in ROB.list:
                    #     if robEntry.name == h:
                    #         if robEntry.ready:
                    if h is not None and h.ready:
                        fu.reservationStation.Vj = h.value
                    else:
                        fu.reservationStation.Qj = h.name
                else:
                    fu.reservationStation.Vj = register.value
                find = True
        if not find:
            fu.reservationStation.Vj = float(inst.source1)

        find = False
        for register in RF.registerList:
            if register.name == inst.source2:
                if register.busy:
                    h = ROB.findlastentry(register)
                    # for robEntry in ROB.list:
                    #     if robEntry.name == h:
                    #         if robEntry.ready:
                    if h is not None and h.ready:
                        fu.reservationStation.Vk = h.value
                    else:
                        fu.reservationStation.Qk = h.name
                else:
                    fu.reservationStation.Vk = register.value
                find = True
        if not find and inst.source2 is not None:
            fu.reservationStation.Vk = float(inst.source2)

        b = ROB.createRoBEntry(inst)

        if inst.destination != 'BGE':
            for register in RF.registerList:
                if register.name == inst.destination:
                    if not register.busy:
                        register.robId = b
                        register.busy = True
                        break
        fu.reservationStation.destination = b
        fu.reservationStation.busy = True
        fu.reservationStation.opName = inst.opname
        fu.reservationStation.cyclesRemained = fu.cycles


def execute():
    for fu in FU.fuList:
        rs = fu.reservationStation
        if rs.busy and rs.Vj is not None:
            if rs.opName == 'LD':
                rs.cyclesRemained -= 1
            elif rs.Vk is not None:
                rs.cyclesRemained -= 1


def writeResult():
    global PC
    CDB.busy = False
    for fu in FU.fuList:
        rs = fu.reservationStation
        if rs.cyclesRemained is not None and rs.busy is True:
            if rs.cyclesRemained <= 0 and not CDB.busy:
                rs.busy = False
                if rs.opName != 'BGE':
                    result = rs.execute()
                    b = rs.destination
                    CDB.busy = True
                    CDB.value = result
                    CDB.address = b
                    for robentry in ROB.list:
                        if robentry.name == b:
                            robentry.value = result
                            robentry.ready = True
                            break
                    for fu2 in FU.fuList:
                        rs2 = fu2.reservationStation
                        if rs2.Qj == b:
                            rs2.Vj = result
                            rs2.Qj = None
                        if rs2.Qk == b:
                            rs2.Vk = result
                            rs2.Qk = None
                    fu.busy = False
                    rs.clear()
                elif rs.opName == 'BGE':
                    if not rs.Vj >= rs.Vk:
                        listtoremove = ROB.flush(rs.destination)
                        FU.flush(listtoremove)
                        RF.flush(listtoremove)
                        IQ.clear()

                        PC = -1
                    for e in ROB.list:
                        if e.name == rs.destination:
                            e.ready = True
                    rs.clear()



def commit():
    global PC, finished
    head = ROB.gethead()
    if head.ready:
        if head.opname == 'BGE':
            if PC == -1:
                finished = True
            ROB.pop()
        else:
            d = head.destination
            for reg in RF.registerList:
                if reg.name == d:
                    reg.value = head.value
                    reg.robId = None
                    reg.busy = False
                    index = ROB.head
                    for i in range(ROB.numelements-1):
                        index += 1
                        index %= ROB.size
                        if ROB.list[index].destination == reg.name:
                            reg.robId = ROB.list[index].name
                            reg.busy = True
                            break
            ROB.pop()


def print_report():
    global cycles
    report_file = open("Report.txt", "a")
    report_file.write("------------------------\n")
    report_file.write("CYCLE " + str(cycles) + '\n\n')
    report_file.write(IQ.toString() + '\n')
    report_file.write(RF.toString() + '\n')
    report_file.write(FU.toString() + '\n')
    report_file.write(ROB.toString() + '\n')
    report_file.write(CDB.toString() + '\n')
    report_file.close()


FU = FunctionalUnits()
CDB = CommonDataBus()
read_units_file()
read_parameters_file()
read_program_file()

IQ = InstructionQueue(instruction_window_size)
RF = RegisterFile(number_of_registers)
ROB = ReorderBuffer(len(FU.fuList))
cycles = 0
rf = open("Report.txt", "w")
rf.close()

while not finished:
    commit()
    writeResult()
    execute()
    fetch()
    issue()
    print_report()
    cycles += 1

if finished:
    print('R0:', RF.registerList[0].value)
