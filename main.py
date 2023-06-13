from transformer import *
from randomCircuit import *
from customGate import *
from testing import *
from cirq import *


if __name__ == '__main__':
    qubits = [LineQubit(i) for i in range(4)]
    cir = generate_random_circuit(qubits, 11, 'a')
    print(cir)
    a = flip_cnot(cir)
    #print(a)
    b = cancel_adj_h(a)
    #print(b)
    opt = merge_flip_cnot(cir)
    print(opt)

