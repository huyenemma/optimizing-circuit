import matplotlib.pyplot as plt
from transformer import *
from randomCircuit import *


# simple test: show that all transformer work exactly like the identities
def simple_test(template):
    """
    :param template: a character to point the template to test correctness
    """
    transformers_dict = {'a': merge_flip_cnot, 'b': cancel_adj_h, 'c': cancel_adj_cnot, 'd': two_cx_to_cxx,
                         'e': flip_cnot, 'f': reverse_cnot_with_hgate}
    num_qb = 0
    cir_depth = 0
    match template:
        case 'a':
            num_qb = 4
            cir_depth = 9
        case 'b':
            num_qb = 1
            cir_depth = 2
        case 'c':
            num_qb = 2
            cir_depth = 2
        case 'd':
            num_qb = 3
            cir_depth = 2
        case 'e':
            num_qb = 2
            cir_depth = 1
        case 'f':
            num_qb = 2
            cir_depth = 5
        case _:
            print("Undefined template. Choose template a, b, c, d, e, f")
    print("\nTesting template", template)
    qubits = [LineQubit(i) for i in range(num_qb)]
    origin = generate_random_circuit(qubits, cir_depth, template)
    print("Origin circuit:\n", origin)

    opt = transformers_dict[template](origin)
    print("Optimized circuit:\n", opt)
    return origin, opt


def compare_circuit_depth(origin, opt):
    # Compare the circuit depths
    depth1 = len(list(origin.all_operations()))
    depth2 = len(list(opt.all_operations()))
    print(f"Origin Circuit Depth: {depth1}")
    print(f"Optimized Circuit Depth: {depth2}")

    # Check if the optimized circuit is correct
    if depth2 < depth1:
        print("Optimizer successfully reduced circuit depth.")
    else:
        print("Optimizer did not reduce circuit depth.")

    return


def simulator_test(origin, opt):
    origin.measure_all()
    opt.measure_all()
    simulator = Simulator()
    origin_result = simulator.run(origin, repetitions=1000)
    opt_result = simulator.run(opt, repetitions=1000)

    fig, ax = plt.subplots()  # Create a figure and axis object
    _ = plot_state_histogram(origin_result, ax, title="origin circuit")  # Use the axis object to plot the histogram
    plt.savefig("origin")  # Save the figure

    fig, ax = plt.subplots()  # Create a new figure and axis object for the next histogram
    _ = plot_state_histogram(opt_result, ax, title="optimized circuit")  # Use the axis object to plot the histogram
    plt.savefig("opt")

    return
