################################################################################
# © Copyright 2021-2022 Zapata Computing Inc.
################################################################################
import pytest
from orquestra.quantum.api.backend_test import (
    QuantumSimulatorGatesTest,
    QuantumSimulatorTests,
)
from orquestra.quantum.circuits import CNOT, Circuit, H, X
from orquestra.quantum.operators import PauliTerm

from orquestra.integrations.forest.simulator import ForestSimulator


@pytest.fixture(
    scope="module",
    params=[
        {"device_name": "wavefunction-simulator"},
        {"device_name": "3q-qvm"},
        {"device_name": "3q-noisy-qvm"},
    ],
)
def backend(request):
    return ForestSimulator(**request.param)


@pytest.fixture(
    scope="module",
    params=[
        {"device_name": "3q-qvm"},
    ],
)
def backend_for_gates_test(request):
    return ForestSimulator(**request.param)


@pytest.fixture(
    scope="module",
    params=[
        {"device_name": "wavefunction-simulator"},
    ],
)
def wf_simulator(request):
    return ForestSimulator(**request.param)


@pytest.mark.xfail
class TestForest(QuantumSimulatorTests):
    def test_exact_expectation_values_without_wavefunction_simulator(self, backend):
        if backend.device_name != "wavefunction-simulator":
            operator = PauliTerm("Z0*Z1")
            circuit = Circuit([X(0), X(1)])
            with pytest.raises(Exception):
                backend.get_exact_expectation_values(circuit, operator)

    def test_multiple_simulators_does_not_cause_errors(self):
        simulator1 = ForestSimulator("wavefunction-simulator")  # noqa: F841
        simulator2 = ForestSimulator("wavefunction-simulator")  # noqa: F841

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

    @pytest.mark.xfail
    def test_get_wavefunction_uses_provided_initial_state(self, wf_simulator):
        super().test_get_wavefunction_uses_provided_initial_state(wf_simulator)


@pytest.mark.xfail
class TestForestGates(QuantumSimulatorGatesTest):
    pass
