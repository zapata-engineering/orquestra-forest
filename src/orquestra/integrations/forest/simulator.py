import os

import numpy as np
from zquantum.core.interfaces.backend import QuantumSimulator
from zquantum.core.circuit import save_circuit
from zquantum.core.measurement import (load_wavefunction, load_expectation_values, sample_from_wavefunction,
                                        ExpectationValues, get_expectation_values_from_measurements, expectation_values_to_real)
from forestopenfermion import qubitop_to_pyquilpauli
from pyquil.api import WavefunctionSimulator, get_qc


class ForestSimulator(QuantumSimulator):
    def __init__(self, device_name, n_samples=None, nthreads=1):
        self.nthreads = nthreads
        self.n_samples = n_samples
        self.device_name = device_name

    def run_circuit_and_measure(self, circuit, **kwargs):
        '''
        Run a circuit and measure a certain number of bitstrings. Note: the number
        of bitstrings measured is derived from self.n_samples

        Args:
            circuit (zquantum.core.circuit.Circuit): the circuit to prepare the state
        Returns:
            a list of bitstrings (a list of tuples)
        '''
        cxn = get_forest_connection(self.device_name)
        bitstrings = cxn.run_and_measure(circuit.to_pyquil(), trials=self.n_samples)
        if isinstance(bitstrings, dict):
            bitstrings = np.vstack(bitstrings[q] for q in sorted(cxn.qubits())).T

        # Store the bitstrings as a list of tuples, with each tuple representing one bitstring
        bitstrings = [tuple(b) for b in bitstrings.tolist()]
        return bitstrings

    def get_expectation_values(self, circuit, qubit_operator, **kwargs):
        if self.device_name == 'wavefunction-simulator' and self.n_samples==None:
            return self.get_exact_expectation_values(circuit, qubit_operator, **kwargs)
        else:
            measurements = self.run_circuit_and_measure(circuit, nthreads=self.nthreads)
            expectation_values = get_expectation_values_from_measurements(
                                    measurements, qubit_operator)

            expectation_values = expectation_values_to_real(expectation_values)
            return expectation_values
            
    def get_exact_expectation_values(self, circuit, qubit_operator, **kwargs):
        if self.device_name != 'wavefunction-simulator' and self.n_samples!=None:
            raise Exception("Exact expectation values work only for the wavefunction simulator and n_samples equal to None.")
        cxn = get_forest_connection(self.device_name)

        # Pyquil does not support PauliSums with no terms.
        if len(qubit_operator.terms) == 0:
            return ExpectationValues(np.zeros((0,)))

        pauli_sum = qubitop_to_pyquilpauli(qubit_operator)
        expectation_values = cxn.expectation(circuit.to_pyquil(), pauli_sum.terms)
        if expectation_values.shape[0] != len(pauli_sum):
            raise(RuntimeError("Expected {} expectation values but received {}.".format(len(pauli_sum), expectation_values.shape[0])))
        return ExpectationValues(expectation_values)

    def get_wavefunction(self, circuit):
        cxn = get_forest_connection(self.device_name)
        wavefunction = cxn.wavefunction(circuit.to_pyquil())
        return wavefunction


def get_forest_connection(device_name):
    '''Get a connection to a forest backend

    Args:
        device_name (string): the device to connect to

    Returns:
        A connection to either a pyquil simulator or a QPU
    '''
    if device_name == 'wavefunction-simulator':
        return WavefunctionSimulator()
    else:
        return get_qc(device_name)
