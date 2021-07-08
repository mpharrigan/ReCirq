from dataclasses import dataclass
from typing import Any, Union, List, Optional

import cirq.work
from recirq.quantum_executable import ProgramGroup


class QuantumRuntime:
    pass


class GateSynthesizer:
    pass


class AutoCalibrator:
    pass


import cirq_google as cg


@dataclass
class QCSRuntime(QuantumRuntime):
    sampler: cirq.Sampler
    device: cirq.Device = None
    gate_synthesizer: GateSynthesizer = None
    calibrator: AutoCalibrator = None
    readout_corrector = None
    qubit_placer = None
    batcher = None

    @classmethod
    def from_device_name(cls, processor_id, gate_set_name, **kwargs):
        return cls(
            sampler=cg.get_engine_sampler(processor_id, gate_set_name=gate_set_name),
            device=cg.get_engine_device(processor_id),
            **kwargs
        )

    def execute(self, program_group: ProgramGroup):
        pass


@dataclass
class MockRuntime(QuantumRuntime):
    sampler: cirq.Sampler
    device: cirq.Device = None
    # ...


@dataclass
class TryRandomLocations:
    trials: int


runtime1 = QCSRuntime.from_device_name(
    processor_id='weber',
    qubit_placer=TryRandomLocations(trials=10),
)

runtime2 = MockRuntime(
    sampler=cirq.Simulator(),
    device=cg.Sycamore23,
    # ...
)
