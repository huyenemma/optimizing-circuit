from transformer import *
from randomCircuit import *
from testing import *
from cirq import *


if __name__ == '__main__':
    simple_test('a')
    simple_test('b')
    simple_test('c')
    simple_test('d')
    simple_test('e')
    simple_test('f')

    qubits = [LineQubit(i) for i in range(4)]
    origin = generate_random_circuit(qubits, 6, 'd')
    print(origin)
    opt = two_cx_to_cxx(origin)
    print(opt)
    simulator_test(origin, opt)

