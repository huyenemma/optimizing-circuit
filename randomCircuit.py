from cirq import *
import random


def generate_random_circuit(qubits, depth, template):
    """
    Generate random quantum circuit which has chosen template identity appeared at least once
    :param qubits: list of qubits to apply on the circuit
    :param depth: maximum number of gates
    :param template: a character to define which template
    :return: New quantum circuit
    """
    circuit = Circuit()
    # all common gates in cirq
    gates = [X, Y, Z, H, S, T, CZ, CNOT, SWAP, ISWAP, XX, YY, ZZ]
    # randomly chose the qubit to apply operation
    control = random.choice(qubits)
    template_added = False
    operations = []
    for i in range(depth):
        template_new = generate_template(qubits, depth, template)
        num = random.randint(0, len(gates))

        if num == len(gates):
            gate = template_new
        else:
            gate = gates[num]

        if gate in gates[6:]:
            target = random.choice(qubits)
            while control == target:
                target = random.choice(qubits)
            operations.append(gate(control, target))
        elif gate == template_new:
            operations.append(template_new)
            template_added = True
        else:
            print("current gate: ", gate)
            operations.append(gate(control))

        if not template_added:
            operations[0] = template_new

    circuit.append(operations)
    return circuit


def generate_template(qubits, depth, template):

    control = random.choice(qubits)

    match template:
        case 'a':
            if len(qubits) < 4 or depth < 9:
                print("To use template a, you should have at least 4 qubits")
                return
            target = random.choice(qubits)
            control2 = random.choice(qubits)
            control3 = random.choice(qubits)
            while control2 == control or control2 == control3 or control == control3  \
                    or control2 == target or control3 == target or control == target:
                target = random.choice(qubits)
                control2 = random.choice(qubits)
                control3 = random.choice(qubits)
            template_generated = [H(control), H(control2), H(control3), CNOT(control, target), CNOT(control2, target),
                                  CNOT(control3, target), H(control), H(control2), H(control3)]
            return template_generated

        case 'b':
            if len(qubits) < 1 or depth < 2:
                print("To use template b, you should have at least 1 qubits")
                return
            template_generated = [H(control), H(control)]
            return template_generated

        case 'c':
            if len(qubits) < 2 or depth < 2:
                print("To use template c, you should have at least 2 qubits")
                return
            target = random.choice(qubits)
            while target == control:
                target = random.choice(qubits)
            template_generated = [CNOT(control, target), CNOT(control, target)]
            return template_generated

        case 'd':
            if len(qubits) < 3 or depth < 2:
                print("To use template d, you should have at least 3 qubits")
                return
            target1 = random.choice(qubits)
            target2 = random.choice(qubits)
            while target2 == target1 or target2 == control or target1 == control:
                target1 = random.choice(qubits)
                target2 = random.choice(qubits)
            template_generated = [CNOT(control, target1), CNOT(control, target2)]
            return template_generated

        case 'e':
            if len(qubits) < 2 or depth < 1:
                print("To use template e, you should have at least 2 qubits")
                return
            target = random.choice(qubits)
            while target == control:
                target = random.choice(qubits)
            template_generated = [CNOT(control, target)]
            return template_generated

        case 'f':
            if len(qubits) < 2 or depth < 5:
                print("To use template f, you should have at least 2 qubits")
                return
            target = random.choice(qubits)
            while target == control:
                target = random.choice(qubits)
            template_generated = [H(control), H(target), CNOT(control, target), H(control), H(target)]
            return template_generated
        case _:
            print("Undefined template. Choose template a, b, c, d, e, f")
            return


if __name__ == '__main__':
    qubits = [LineQubit(i) for i in range(4)]
    cir = generate_random_circuit(qubits, 10, 'a')
    print(cir)
