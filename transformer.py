from cirq import *


def cancel_adj_h(circuit):
    """
    Apply the template b: a sequence of two Hadamard gate is cancelled
    :param circuit: a circuit to optimize
    :return: new circuit
    """
    opt_circuit = Circuit()
    # dictionary to keep track H gates on individual qubits in circuit
    hadamard_gates = {qubit: None for qubit in circuit.all_qubits()}
    for moment in circuit:
        for op in moment:
            qubit = op.qubits[0]
            prev_hadamard_op = hadamard_gates[qubit]
            if isinstance(op.gate, HPowGate):
                if prev_hadamard_op is not None:
                    # if the qubit already has a H gate, cancel the sequence by setting the previous
                    # Hadamard gate to None
                    hadamard_gates[qubit] = None
                else:
                    # store the current H gate
                    hadamard_gates[qubit] = op
            else:
                # if current operation is not H, the previous H on this qubit (if existed) should be added
                if prev_hadamard_op is not None:
                    opt_circuit.append(prev_hadamard_op)
                    hadamard_gates[qubit] = None
                # add the current operation
                opt_circuit.append(op)

    # add any remaining H gates in the dictionary to the optimized circuit
    for qubit, hadamard_op in hadamard_gates.items():
        if hadamard_op is not None:
            opt_circuit.append(hadamard_op)

    return opt_circuit


def cancel_adj_cnot(circuit):
    """
    Apply the template c: a sequence of two CNOT gates is cancelled
    :param circuit: a circuit to optimize
    :return: new circuit
    """
    opt_circuit = Circuit()
    # dictionary to keep track CNOT gates on tuple (control, target) qubits in circuit
    cnot_gates = {}
    prev_op = None
    for moment in circuit:
        for op in moment:
            if isinstance(op.gate, CXPowGate):
                control = op.qubits[0]
                target = op.qubits[1]
                if (control, target) in cnot_gates.keys():
                    del cnot_gates[(control, target)]
                    continue  # Skip adding the current CNOT gate
                else:
                    # store the current CNOT gate into dictionary
                    cnot_gates[(control, target)] = op
            else:
                qubit = op.qubits[0]
                is_qb_in_cnot_gates = any(qubit in key for key in cnot_gates.keys())
                # if current operation is not CNOT, the previous CNOT (if existed) should be added
                if isinstance(prev_op.gate, CXPowGate) and prev_op is not None and is_qb_in_cnot_gates:
                    control = prev_op.qubits[0]
                    target = prev_op.qubits[1]
                    opt_circuit.append(prev_op)
                    del cnot_gates[(control, target)]

                # add the current operation
                opt_circuit.append(op)
            prev_op = op

    # add any remaining CNOT gates in the dictionary to the optimized circuit
    for operation in cnot_gates.values():
        if operation is not None:
            opt_circuit.append(operation)

    return opt_circuit


def two_cx_to_toffoli(circuit):
    opt_circuit = Circuit()
    # dictionary to keep track CNOT gates on control qubits in circuit
    cnot_gates = {}
    prev_op = None
    for moment in circuit:
        for op in moment:
            if isinstance(op.gate, CXPowGate):
                control = op.qubits[0]
                target = op.qubits[1]
                if control in cnot_gates.keys():
                    opt_circuit.append(TOFFOLI(control, cnot_gates[control].qubits[1], target))
                    del cnot_gates[control]
                    continue  # Skip adding the current CNOT gate
                else:
                    # store the current CNOT gate into dictionary
                    cnot_gates[control] = op
            else:
                qubit = op.qubits[0]
                is_qb_in_cnot_gates = any(qubit in key for key in cnot_gates.keys())
                # if current operation is not CNOT, the previous CNOT (if existed) should be added
                if isinstance(prev_op.gate, CXPowGate) and prev_op is not None and is_qb_in_cnot_gates:
                    control = prev_op.qubits[0]
                    target = prev_op.qubits[1]
                    opt_circuit.append(prev_op)
                    del cnot_gates[(control, target)]

                # add the current operation
                opt_circuit.append(op)
            prev_op = op

    # add any remaining CNOT gates in the dictionary to the optimized circuit
    for operation in cnot_gates.values():
        if operation is not None:
            opt_circuit.append(operation)

    return opt_circuit


def flip_cnot(circuit):
    """
    Apply template e. Flip a cnot gate and add surrounding H gates on the qubit the CX gate applied
    :param circuit
    :return:
    """
    opt_circuit = Circuit()
    for moment in circuit:
        new_ops = []
        for op in moment:
            if isinstance(op.gate, CXPowGate):
                q0, q1 = op.qubits
                new_ops.extend([H(q0), H(q1), CNOT(q1, q0), H(q1), H(q0)])
            else:
                new_ops.append(op)
        opt_circuit.append(new_ops)
    return opt_circuit


# a helper function while using template f
def _is_subsequence(subsequence, sequence):
    sub_len = len(subsequence)
    seq_len = len(sequence)

    # If the subsequence is longer than the sequence, it cannot be a subsequence
    if sub_len > seq_len:
        return False

    # Initialize pointers for the subsequence and sequence
    sub_ptr = 0
    seq_ptr = 0

    while seq_ptr < seq_len:
        # If the elements match, move both pointers forward
        if subsequence[sub_ptr] is sequence[seq_ptr].gate:
            sub_ptr += 1
            # If we have found all elements of the subsequence, it is present
            if sub_ptr == sub_len:
                return True
        seq_ptr += 1

    return False


def reverse_cnot_with_hgate(circuit):
    """
    Apply template f. When both control and target qubits of a CX gate sandwiched by Hadamard gates, we can delete
    sandwiched the H gates and flip CX gate to optimize
    :param circuit
    :return: new optimized circuit
    """
    opt_circuit = Circuit()

    # find all operations applied on a qubit
    gates_by_qubit = {qubit: [] for qubit in circuit.all_qubits()}
    for moment in circuit:
        for op in moment:
            for qb in op.qubits:
                gates_by_qubit[qb].append(op)

    subsequence = [H, CNOT, H]
    q_has_subsequence = []
    for key in gates_by_qubit:
        if _is_subsequence(subsequence, gates_by_qubit[key]):
            q_has_subsequence.append(key)

    for qb in q_has_subsequence:
        operation = gates_by_qubit[qb]
        for op in operation:
            if isinstance(op.gate, CXPowGate):
                control, target = op.qubits
                if target in q_has_subsequence and control == qb:
                    ops1 = gates_by_qubit[target]
                    i = ops1.index(op)
                    del ops1[i-1]
                    del ops1[i-1]
                    del ops1[i-1]
                    gates_by_qubit[target] = ops1

                    ops2 = gates_by_qubit[control]
                    j = ops2.index(op)
                    del ops2[j-1]
                    del ops2[j-1]
                    del ops2[j-1]
                    ops2.insert(j-1, CNOT(target, control))
                    gates_by_qubit[control] = ops2

    max_len = max(len(v) for v in gates_by_qubit.values())
    for i in range(max_len):
        for key in gates_by_qubit:
            values = gates_by_qubit[key]
            if i < len(values):
                opt_circuit.append(values[i])

    return opt_circuit
