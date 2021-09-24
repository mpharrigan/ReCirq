# Copyright 2021 Google
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
from functools import lru_cache
from typing import Optional

from cirq.protocols.json_serialization import ObjectFactory, DEFAULT_RESOLVERS

from .loschmidt import (
    TiltedSquareLatticeLoschmidtData, TiltedSquareLatticeLoschmidtSpec, process_results,
    flat_results_to_dataframe
)


@lru_cache()
def _resolve_json(cirq_type: str) -> Optional[ObjectFactory]:
    if not cirq_type.startswith('recirq.algo_benchmarks.'):
        return None

    cirq_type = cirq_type[len('recirq.algo_benchmarks.'):]
    return {
        'TiltedSquareLatticeLoschmidtSpec': TiltedSquareLatticeLoschmidtSpec,
        'TiltedSquareLatticeLoschmidtData': TiltedSquareLatticeLoschmidtData,
    }.get(cirq_type, None)


DEFAULT_RESOLVERS.append(_resolve_json)
