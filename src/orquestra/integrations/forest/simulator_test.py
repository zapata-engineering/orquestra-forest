import pytest
import numpy as np
from zquantum.core.circuit import Circuit
from zquantum.core.interfaces.backend_test import QuantumSimulatorTests
from openfermion.ops import QubitOperator
from .simulator import ForestSimulator
from pyquil import Program
from pyquil.gates import X


@pytest.fixture(
    params=[
        {"device_name": "wavefunction-simulator"},
        {"device_name": "3q-qvm", "n_samples": 10000},
        {"device_name": "3q-noisy-qvm", "n_samples": 10000},
    ]
)
def backend(request):
    return ForestSimulator(**request.param)


@pytest.fixture(
    params=[
        {"device_name": "wavefunction-simulator"},
    ]
)
def wf_simulator(request):
    return ForestSimulator(**request.param)


class TestForest(QuantumSimulatorTests):
    def test_exact_expectation_values_without_wavefunction_simulator(self, backend):
        if backend.device_name != "wavefunction-simulator":
            backend.n_samples = None
            operator = QubitOperator("Z0 Z1")
            circuit = Circuit(Program([X(0), X(1)]))
            with pytest.raises(Exception):
                backend.get_exact_expectation_values(circuit, operator)

    def test_exact_expectation_values_with_n_samples(self, wf_simulator):
        wf_simulator.n_samples = 1000
        operator = QubitOperator("Z0 Z1")
        circuit = Circuit(Program([X(0), X(1)]))
        with pytest.raises(Exception):
            wf_simulator.get_exact_expectation_values(circuit, operator)

    def test_multiple_simulators_does_not_cause_errors(self):
        simulator1 = ForestSimulator("wavefunction-simulator")
        simulator2 = ForestSimulator("wavefunction-simulator")
