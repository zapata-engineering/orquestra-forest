import pytest
from zquantum.core.circuits import Circuit, X, CNOT, H
from zquantum.core.interfaces.backend_test import (
    QuantumSimulatorTests,
    QuantumSimulatorGatesTest,
)
from openfermion.ops import QubitOperator
from qeforest.simulator import ForestSimulator


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
        {"device_name": "3q-qvm", "n_samples": 1000},
    ]
)
def backend_for_gates_test(request):
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
            circuit = Circuit([X(0), X(1)])
            with pytest.raises(Exception):
                backend.get_exact_expectation_values(circuit, operator)

    def test_exact_expectation_values_with_n_samples(self, wf_simulator):
        wf_simulator.n_samples = 1000
        operator = QubitOperator("Z0 Z1")
        circuit = Circuit([X(0), X(1)])
        with pytest.raises(Exception):
            wf_simulator.get_exact_expectation_values(circuit, operator)

    def test_multiple_simulators_does_not_cause_errors(self):
        simulator1 = ForestSimulator("wavefunction-simulator")
        simulator2 = ForestSimulator("wavefunction-simulator")

    def test_get_wavefunction_seed(self):
        # Given
        circuit = Circuit([H(0), CNOT(0, 1), CNOT(1, 2)])
        backend1 = ForestSimulator("wavefunction-simulator", seed=5324)
        backend2 = ForestSimulator("wavefunction-simulator", seed=5324)

        # When
        wavefunction1 = backend1.get_wavefunction(circuit)
        wavefunction2 = backend2.get_wavefunction(circuit)

        # Then
        for (ampl1, ampl2) in zip(wavefunction1.amplitudes, wavefunction2.amplitudes):
            assert ampl1 == ampl2


class TestForestGates(QuantumSimulatorGatesTest):
    pass
