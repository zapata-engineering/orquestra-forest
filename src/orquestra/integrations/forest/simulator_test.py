import unittest
import numpy as np
from zquantum.core.circuit import Circuit
from zquantum.core.bitstring_distribution import BitstringDistribution
from zquantum.core.interfaces.backend_test import QuantumSimulatorTests
from openfermion.ops import QubitOperator, IsingOperator
from .simulator import ForestSimulator
from pyquil import Program
from pyquil.gates import H, CNOT, RX, CZ, X


class TestForest(unittest.TestCase, QuantumSimulatorTests):
    def setUp(self):
        self.wf_simulator = ForestSimulator("wavefunction-simulator")
        self.sampling_simulator = ForestSimulator("3q-qvm", n_samples=10000)
        self.noisy_simulator = ForestSimulator("3q-noisy-qvm", n_samples=10000)

        # Inherited tests
        self.backends = [
            self.sampling_simulator,
            self.noisy_simulator,
            self.wf_simulator,
        ]
        self.wf_simulators = [self.wf_simulator]

    def test_exact_expectation_values_without_wavefunction_simulator(self):
        self.sampling_simulator.n_samples = None
        operator = QubitOperator("Z0 Z1")
        circuit = Circuit(Program([X(0), X(1)]))
        with self.assertRaises(Exception):
            self.sampling_simulator.get_exact_expectation_values(circuit, operator)

    def test_exact_expectation_values_with_n_samples(self):
        self.wf_simulator.n_samples = 1000
        operator = QubitOperator("Z0 Z1")
        circuit = Circuit(Program([X(0), X(1)]))
        with self.assertRaises(Exception):
            self.wf_simulator.get_exact_expectation_values(circuit, operator)
