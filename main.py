from transformer import *
from randomCircuit import *
from testing import *
from cirq import *


if __name__ == '__main__':
    # simple_test('b')
    # simple_test('c')
    # simple_test('d')
    # simple_test('e')
    # simple_test('f')

    qubits = [LineQubit(i) for i in range(4)]
    origin = generate_random_circuit(qubits, 10, 'a')
    print("Origin circuit:\n", origin)
    opt = merge_flip_cnot(origin)
    print("Optimized circuit:\n", opt)
    simulator_test(origin, opt)

