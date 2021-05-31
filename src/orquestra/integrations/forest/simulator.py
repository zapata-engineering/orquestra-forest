import errno
import socket
import subprocess

import numpy as np
from pyquil.api import WavefunctionSimulator, get_qc
from zquantum.core.circuits import Circuit
from zquantum.core.interfaces.backend import QuantumSimulator
from zquantum.core.measurement import (
    ExpectationValues,
    Measurements,
)
from zquantum.core.openfermion import qubitop_to_pyquilpauli
from zquantum.core.wip.circuits import export_to_pyquil


class ForestSimulator(QuantumSimulator):
    supports_batching = False

    def __init__(self, device_name, n_samples=None, seed=None, nthreads=1):
        super().__init__(n_samples)
        self.nthreads = nthreads
        self.n_samples = n_samples
        self.device_name = device_name
        self.seed = seed

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            s.bind(("127.0.0.1", 5000))
            subprocess.Popen(["qvm", "-S"])
        except socket.error as e:
            if e.errno == errno.EADDRINUSE:
                print("QVM is already running")
            else:
                print(e)
        try:
            s.bind(("127.0.0.1", 5555))
            subprocess.Popen(["quilc", "-S"])
        except socket.error as e:
            if e.errno == errno.EADDRINUSE:
                print("Quilc is already running")
            else:
                print(e)

        s.close()

    def run_circuit_and_measure(self, circuit, n_samples=None, **kwargs):
        """Run a circuit and measure a certain number of bitstrings. Note: the number
        of bitstrings measured is derived from self.n_samples

        Args:
            circuit: the circuit to prepare the state
            n_samples: The number of samples to measure. If None, then the
                number of samples is taken from the n_samples attribute.
        Returns:
            a list of bitstrings (a list of tuples)
        """
        if n_samples is None:
            n_samples = self.n_samples
        super().run_circuit_and_measure(circuit)
        cxn = get_forest_connection(self.device_name, self.seed)
        bitstrings = cxn.run_and_measure(export_to_pyquil(circuit), trials=n_samples)
        if isinstance(bitstrings, dict):
            bitstrings = np.vstack([bitstrings[q] for q in sorted(cxn.qubits())]).T

        bitstrings = [tuple(b) for b in bitstrings.tolist()]
        return Measurements(bitstrings)

    def get_exact_expectation_values(self, circuit, qubit_operator, **kwargs):
        self.number_of_jobs_run += 1
        self.number_of_circuits_run += 1
        if self.device_name != "wavefunction-simulator" or self.n_samples is not None:
            raise RuntimeError(
                "To compute exact expectation values, (i) the device name must be "
                '"wavefunction-simulator" and (ii) n_samples must be None. The device '
                f"name is currently {self.device_name} and n_samples is {self.n_samples}."
            )
        cxn = get_forest_connection(self.device_name, self.seed)

        # Pyquil does not support PauliSums with no terms.
        if len(qubit_operator.terms) == 0:
            return ExpectationValues(np.zeros((0,)))

        pauli_sum = qubitop_to_pyquilpauli(qubit_operator)
        expectation_values = np.real(
            cxn.expectation(export_to_pyquil(circuit), pauli_sum.terms)
        )

        if expectation_values.shape[0] != len(pauli_sum):
            raise (
                RuntimeError(
                    f"Expected {len(pauli_sum)} expectation values but received "
                    f"{expectation_values.shape[0]}."
                )
            )
        return ExpectationValues(expectation_values)

    def get_wavefunction(self, circuit):
        super().get_wavefunction(circuit)
        cxn = get_forest_connection(self.device_name, self.seed)
        wavefunction = cxn.wavefunction(export_to_pyquil(circuit))
        return wavefunction


def get_forest_connection(device_name: str, seed=None):
    """Get a connection to a forest backend

    Args:
        device_name: the device to connect to

    Returns:
        A connection to either a pyquil simulator or a QPU
    """
    if device_name == "wavefunction-simulator":
        return WavefunctionSimulator(random_seed=seed)
    else:
        return get_qc(device_name)
