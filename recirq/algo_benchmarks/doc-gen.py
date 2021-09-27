import dataclasses
from dataclasses import dataclass
from typing import Type, Callable

import pandas as pd

from recirq.algo_benchmarks.loschmidt.loschmidt import (
    TiltedSquareLatticeLoschmidtSpec,
    TiltedSquareLatticeLoschmidtData,
    get_all_tilted_square_lattice_executables
)
from recirq.algo_benchmarks.xx_model.single_noninteracting import (
    SingleNoninteractingXxData,
    SingleNoninteractingXxSpec,
    get_all_single_noninteracting_xx_executables
)
from recirq.cirqflow.quantum_executable import ExecutableSpec, QuantumExecutableGroup


@dataclass
class AlgoBenchmark:
    module: str
    submodule: str
    executable_family: str
    spec_class: Type[ExecutableSpec]
    data_class: Type
    gen_func: Callable[[...], QuantumExecutableGroup]

    def as_strings(self):
        ret = {k: str(v) for k, v in dataclasses.asdict(self).items()}
        ret['spec_class'] = self.spec_class.__name__
        ret['data_class'] = self.data_class.__name__
        ret['gen_func'] = self.gen_func.__name__
        return ret


DATA = [
    AlgoBenchmark(
        module='recirq.algo_benchmarks.loschmidt',
        submodule='loschmidt',
        executable_family='recirq.algo_benchmarks.tilted_square_lattice_loschmidt',
        spec_class=TiltedSquareLatticeLoschmidtSpec,
        data_class=TiltedSquareLatticeLoschmidtData,
        gen_func=get_all_tilted_square_lattice_executables,
    ),
    AlgoBenchmark(
        module='recirq.algo_benchmarks.xx_model',
        submodule='single_noninteracting',
        executable_family='recirq.algo_benchmarks.???',
        spec_class=SingleNoninteractingXxSpec,
        data_class=SingleNoninteractingXxData,
        gen_func=get_all_single_noninteracting_xx_executables,
    )
]


def main():
    for algo in DATA:
        # assert algo.executable_family == algo.spec_class.executable_family
        print(algo.executable_family, algo.spec_class.executable_family)

        #assert algo.gen_fn == f'{algo.submodule}-gen.py'
        #assert algo.run_fn == f'{algo.submodule}-run.py'
        #assert algo.plot_fn == f'{algo.submodule}-plots.ipynb'

    df = pd.DataFrame([algo.as_strings() for algo in DATA]).set_index('executable_family')

    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    print(df.transpose())


if __name__ == '__main__':
    main()
