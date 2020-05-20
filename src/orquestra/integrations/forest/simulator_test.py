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
        self.backends = [self.sampling_simulator, self.noisy_simulator, self.wf_simulator]
        self.wf_simulators = [self.wf_simulator]
