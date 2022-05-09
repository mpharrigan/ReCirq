# Copyright 2022 Google
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Generate the QuantumExecutableGroup for the small-cz-v1 configuration of the
loschmidt.tilted_square_lattice benchmark.

The `small-cz-v1` configuration is A 'small' configuration for quick verification
of Loschmidt echos using the CZ gate.

This configuration uses small grid topologies (making it suitable for
running on simulators) and a small number of random instances making it
suitable for getting a quick reading on processor performance in ~minutes.

To run:

    python gen-small-cz-v1.py

"""

import numpy as np

import cirq
from recirq.qaoa.sk_model import get_all_sk_model_qaoa_executables

EXES_FILENAME = 'sk_model.8q-v1.json.gz'


def main():
    exes = get_all_sk_model_qaoa_executables(
        n_instances=10,min_size=8, max_size=8, p_depths=[1],
    )
    print(len(exes), 'executables')

    cirq.to_json_gzip(exes, EXES_FILENAME)
    print(f'Wrote {EXES_FILENAME}')


if __name__ == '__main__':
    main()
