import os

import numpy as np
from zquantum.core.interfaces.backend import QuantumSimulator
from zquantum.core.circuit import save_circuit
from zquantum.core.measurement import (
    load_wavefunction,
    load_expectation_values,
    sample_from_wavefunction,
    ExpectationValues,
    expectation_values_to_real,
    Measurements,
)
from zquantum.core.openfermion import qubitop_to_pyquilpauli
from pyquil.api import WavefunctionSimulator, get_qc
import subprocess
import socket, errno


class ForestSimulator(QuantumSimulator):
    supports_batching = False

    def __init__(self, device_name, n_samples=None, nthreads=1):
        super().__init__(n_samples)
        self.nthreads = nthreads
        self.n_samples = n_samples
        self.device_name = device_name

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
            circuit (zquantum.core.circuit.Circuit): the circuit to prepare the state
            n_samples (int): The number of samples to measure. If None, then the
                number of samples is taken from the n_samples attribute.
        Returns:
            a list of bitstrings (a list of tuples)
        """
        if n_samples is None:
            n_samples = self.n_samples
        super().run_circuit_and_measure(circuit)
        cxn = get_forest_connection(self.device_name)
        bitstrings = cxn.run_and_measure(circuit.to_pyquil(), trials=n_samples)
        if isinstance(bitstrings, dict):
            bitstrings = np.vstack([bitstrings[q] for q in sorted(cxn.qubits())]).T

        # Store the bitstrings as a list of tuples, with each tuple representing one bitstring
        bitstrings = [tuple(b) for b in bitstrings.tolist()]
        return Measurements(bitstrings)

    def get_exact_expectation_values(self, circuit, qubit_operator, **kwargs):
        self.number_of_jobs_run += 1
        self.number_of_circuits_run += 1
        if self.device_name != "wavefunction-simulator" or self.n_samples is not None:
            raise Exception(
                f"""To compute exact expectation values, (i) the device name must be "wavefunction-simulator" and (ii) n_samples 
                    must be None. The device name is currently {self.device_name} and n_samples is {self.n_samples}."""
            )
        cxn = get_forest_connection(self.device_name)

        # Pyquil does not support PauliSums with no terms.
        if len(qubit_operator.terms) == 0:
            return ExpectationValues(np.zeros((0,)))

        pauli_sum = qubitop_to_pyquilpauli(qubit_operator)
        expectation_values = np.real(
            cxn.expectation(circuit.to_pyquil(), pauli_sum.terms)
        )

        if expectation_values.shape[0] != len(pauli_sum):
            raise (
                RuntimeError(
                    "Expected {} expectation values but received {}.".format(
                        len(pauli_sum), expectation_values.shape[0]
                    )
                )
            )
        return ExpectationValues(expectation_values)

    def get_wavefunction(self, circuit):
        super().get_wavefunction(circuit)
        cxn = get_forest_connection(self.device_name)
        wavefunction = cxn.wavefunction(circuit.to_pyquil())
        return wavefunction


def get_forest_connection(device_name):
    """Get a connection to a forest backend

    Args:
        device_name (string): the device to connect to

    Returns:
        A connection to either a pyquil simulator or a QPU
    """
    if device_name == "wavefunction-simulator":
        return WavefunctionSimulator()
    else:
        return get_qc(device_name)
