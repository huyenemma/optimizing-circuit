from testing import *


if __name__ == '__main__':
    # simple_test('b')
    qubits = [cirq.LineQubit(i) for i in range(4)]
    origin = generate_random_circuit(qubits, 6, 'd')
    print(origin)
    opt = two_cx_to_cxx(origin)
    print(opt)
    simulator_test(origin, opt)


