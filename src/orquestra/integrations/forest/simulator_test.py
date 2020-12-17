import pytest
import numpy as np
from zquantum.core.circuit import Circuit
from zquantum.core.bitstring_distribution import BitstringDistribution
from zquantum.core.interfaces.backend_test import QuantumSimulatorTests
from openfermion.ops import QubitOperator, IsingOperator
from .simulator import ForestSimulator
from pyquil import Program
from pyquil.gates import H, CNOT, RX, CZ, X


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
    pass