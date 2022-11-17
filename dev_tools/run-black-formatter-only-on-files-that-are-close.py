from pathlib import Path
from subprocess import run

SRC_DIR = Path(__file__).parent / '..'

YES = ['recirq/__init__.py', 'recirq/_version.py', 'recirq/benchmarks/__init__.py',
       'recirq/benchmarks/rabi_oscillations.py', 'recirq/benchmarks/rabi_oscillations_test.py',
       'recirq/benchmarks/rep_rate/__init__.py', 'recirq/benchmarks/xeb/__init__.py',
       'recirq/beyond_classical/__init__.py',
       'recirq/beyond_classical/google_v2_beyond_classical_test.py', 'recirq/cirqflow/__init__.py',
       'recirq/fermi_hubbard/publication_test.py', 'recirq/hfvqe/__init__.py',
       'recirq/hfvqe/molecular_data/__init__.py', 'recirq/hfvqe/third_party/__init__.py',
       'recirq/optimize/__init__.py', 'recirq/optimize/_util.py',
       'recirq/otoc/loschmidt/tilted_square_lattice/__init__.py', 'recirq/qaoa/__init__.py',
       'recirq/qaoa/experiments/__init__.py', 'recirq/qml_lfe/__init__.py',
       'recirq/qml_lfe/circuit_blocks_test.py', 'recirq/qml_lfe/data/__init__.py',
       'recirq/qml_lfe/dynamics_flags.py', 'recirq/qml_lfe/learn_dynamics_c.py',
       'recirq/qml_lfe/learn_dynamics_c_test.py', 'recirq/qml_lfe/learn_dynamics_q.py',
       'recirq/qml_lfe/learn_dynamics_q_test.py', 'recirq/qml_lfe/learn_states_c.py',
       'recirq/qml_lfe/learn_states_c_test.py', 'recirq/qml_lfe/learn_states_q.py',
       'recirq/qml_lfe/learn_states_q_test.py', 'recirq/qml_lfe/run_config.py',
       'recirq/qml_lfe/run_config_test.py', 'recirq/qml_lfe/state_flags.py',
       'recirq/quantum_chess/__init__.py', 'recirq/readout_scan/__init__.py',
       'recirq/time_crystals/__init__.py', 'recirq/time_crystals/dtc_simulation.py',
       'recirq/time_crystals/dtc_simulation_test.py', 'recirq/time_crystals/dtcexperiment.py',
       'recirq/time_crystals/dtcexperiment_test.py', 'recirq/toric_code/__init__.py',
       'recirq/toric_code/optimizers.py', 'recirq/toric_code/optimizers_test.py',
       'recirq/toric_code/readout_unfolding.py', 'recirq/toric_code/readout_unfolding_test.py',
       'recirq/toric_code/toric_code_plaquettes.py',
       'recirq/toric_code/toric_code_plaquettes_test.py', 'recirq/toric_code/toric_code_plotter.py',
       'recirq/toric_code/toric_code_plotter_test.py', 'recirq/toric_code/toric_code_rectangle.py',
       'recirq/toric_code/toric_code_rectangle_test.py',
       'recirq/toric_code/toric_code_state_prep.py',
       'recirq/toric_code/toric_code_state_prep_test.py']

NO = {'recirq/algorithmic_benchmark_library.py': 204,
      'recirq/algorithmic_benchmark_library_test.py': 129,
      'recirq/benchmarks/rep_rate/rep_rate_calculator.py': 296,
      'recirq/benchmarks/rep_rate/rep_rate_calculator_test.py': 173,
      'recirq/benchmarks/xeb/grid_parallel_two_qubit_xeb.py': 105,
      'recirq/benchmarks/xeb/grid_parallel_two_qubit_xeb_test.py': 14,
      'recirq/benchmarks/xeb/xeb_results.py': 28,
      'recirq/beyond_classical/google_v2_beyond_classical.py': 48,
      'recirq/cirqflow/run_utils.py': 30, 'recirq/cirqflow/run_utils_test.py': 32,
      'recirq/documentation_utils.py': 65, 'recirq/documentation_utils_test.py': 30,
      'recirq/engine_utils.py': 342, 'recirq/engine_utils_test.py': 90,
      'recirq/fermi_hubbard/__init__.py': 69, 'recirq/fermi_hubbard/circuits.py': 563,
      'recirq/fermi_hubbard/converting_sampler.py': 116,
      'recirq/fermi_hubbard/data_plotting.py': 1129, 'recirq/fermi_hubbard/decomposition.py': 418,
      'recirq/fermi_hubbard/decomposition_test.py': 169, 'recirq/fermi_hubbard/execution.py': 322,
      'recirq/fermi_hubbard/execution_test.py': 422,
      'recirq/fermi_hubbard/fermionic_circuits.py': 158,
      'recirq/fermi_hubbard/fermionic_circuits_test.py': 63, 'recirq/fermi_hubbard/layouts.py': 364,
      'recirq/fermi_hubbard/parameters.py': 560, 'recirq/fermi_hubbard/parameters_test.py': 79,
      'recirq/fermi_hubbard/post_processing.py': 787,
      'recirq/fermi_hubbard/post_processing_test.py': 735,
      'recirq/fermi_hubbard/publication.py': 255, 'recirq/hfvqe/analysis.py': 375,
      'recirq/hfvqe/analysis_test.py': 283, 'recirq/hfvqe/circuits.py': 189,
      'recirq/hfvqe/circuits_test.py': 735, 'recirq/hfvqe/gradient_hf.py': 77,
      'recirq/hfvqe/gradient_hf_test.py': 30, 'recirq/hfvqe/mfopt.py': 681,
      'recirq/hfvqe/molecular_data/hydrogen_chains/make_rhf_simulations.py': 100,
      'recirq/hfvqe/molecular_data/molecular_data_construction.py': 188,
      'recirq/hfvqe/molecular_data/molecular_data_construction_test.py': 16,
      'recirq/hfvqe/molecular_example.py': 107, 'recirq/hfvqe/objective.py': 251,
      'recirq/hfvqe/objective_test.py': 159, 'recirq/hfvqe/opdm_functionals.py': 134,
      'recirq/hfvqe/opdm_functionals_test.py': 71, 'recirq/hfvqe/third_party/higham.py': 77,
      'recirq/hfvqe/third_party/higham_test.py': 61, 'recirq/hfvqe/util.py': 40,
      'recirq/hfvqe/util_test.py': 21, 'recirq/optimize/mgd.py': 179,
      'recirq/optimize/mgd_test.py': 117, 'recirq/optimize/minimize.py': 29,
      'recirq/optimize/minimize_test.py': 33, 'recirq/optimize/mpg.py': 220,
      'recirq/optimize/mpg_test.py': 15, 'recirq/otoc/__init__.py': 16,
      'recirq/otoc/loschmidt/__init__.py': 26,
      'recirq/otoc/loschmidt/tilted_square_lattice/analysis.py': 259,
      'recirq/otoc/loschmidt/tilted_square_lattice/gen-small-cz-v1.py': 40,
      'recirq/otoc/loschmidt/tilted_square_lattice/gen-small-v1.py': 39,
      'recirq/otoc/loschmidt/tilted_square_lattice/run-simulator.py': 44,
      'recirq/otoc/loschmidt/tilted_square_lattice/tilted_square_lattice.py': 200,
      'recirq/otoc/loschmidt/tilted_square_lattice/tilted_square_lattice_test.py': 133,
      'recirq/otoc/otoc_circuits.py': 119, 'recirq/otoc/otoc_example.py': 32,
      'recirq/otoc/otoc_test.py': 17, 'recirq/otoc/parallel_xeb.py': 195,
      'recirq/otoc/parallel_xeb_example.py': 59, 'recirq/otoc/parallel_xeb_test.py': 17,
      'recirq/otoc/utils.py': 88, 'recirq/qaoa/circuit_structure.py': 117,
      'recirq/qaoa/circuit_structure_test.py': 287,
      'recirq/qaoa/classical_angle_optimization.py': 144,
      'recirq/qaoa/classical_angle_optimization_test.py': 27,
      'recirq/qaoa/experiments/angle_precomputation_tasks.py': 128,
      'recirq/qaoa/experiments/optimization_tasks.py': 342,
      'recirq/qaoa/experiments/p1_landscape_tasks.py': 452,
      'recirq/qaoa/experiments/precomputed_execution_tasks.py': 203,
      'recirq/qaoa/experiments/problem_generation_tasks.py': 325,
      'recirq/qaoa/experiments/run-angle-precomputation.py': 83,
      'recirq/qaoa/experiments/run-optimization.py': 157,
      'recirq/qaoa/experiments/run-p1-landscape.py': 95,
      'recirq/qaoa/experiments/run-precomputed-data-collection.py': 111,
      'recirq/qaoa/experiments/run-problem-generation.py': 69,
      'recirq/qaoa/gates_and_compilation.py': 708, 'recirq/qaoa/gates_and_compilation_test.py': 323,
      'recirq/qaoa/placement.py': 543, 'recirq/qaoa/placement_test.py': 151,
      'recirq/qaoa/problem_circuits.py': 217, 'recirq/qaoa/problem_circuits_test.py': 88,
      'recirq/qaoa/problems.py': 224, 'recirq/qaoa/problems_test.py': 152,
      'recirq/qaoa/simulation.py': 402, 'recirq/qaoa/simulation_test.py': 122,
      'recirq/qml_lfe/circuit_blocks.py': 18, 'recirq/readout_scan/run-readout-scan.py': 48,
      'recirq/readout_scan/tasks.py': 141, 'recirq/serialization_utils.py': 285,
      'recirq/serialization_utils_test.py': 55}


def get_close_black(add_only: bool = True):
    o = run(['git', 'ls-files'], capture_output=True, universal_newlines=True, cwd=SRC_DIR)

    fns = [line for line in o.stdout.splitlines() if
           line.startswith('recirq/') and line.endswith('.py')]
    yes = []
    no = {}
    for fn in fns:
        if fn in YES and add_only:
            continue
        o = run(['black', fn, '--diff'], cwd=SRC_DIR, capture_output=True, universal_newlines=True)
        diffsize = len(o.stdout.splitlines())
        if diffsize <= 10:
            yes.append(fn)
        else:
            no[fn] = diffsize
        print('.', end='')
    print()
    print(repr(yes))
    print(repr(no))


def do_close():
    run(['black'] + YES, cwd=SRC_DIR)


if __name__ == '__main__':
    # get_close_black()
    do_close()
