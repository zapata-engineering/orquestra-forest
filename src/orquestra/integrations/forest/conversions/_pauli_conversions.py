################################################################################
# © Copyright 2021-2022 Zapata Computing Inc.
################################################################################
############################################################################
#   Copyright 2017 Rigetti Computing, Inc.
#   Modified by Zapata Computing 2020 for the performance reasons.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
############################################################################
"""
Translates Orquestra pauli representation objects to pyQuil objects and vice versa.
"""
from typing import Union

from orquestra.quantum.operators import PauliRepresentation, PauliSum, PauliTerm
from pyquil.paulis import PauliSum as PyquilPauliSum
from pyquil.paulis import PauliTerm as PyquilPauliTerm


def orq_to_pyquil(
    pauli_operator: PauliRepresentation,
) -> Union[PyquilPauliSum, PyquilPauliTerm]:
    """
    Convert an Orquestra PauliSum or PauliTerm to a pyQuil PauliSum or PauliTerm,
    respectively.

    Args:
        pauli_operator: Orquestra PauliSum or PauliTerm to convert to a pyquil PauliSum
            or PauliTerm

    Returns:
        PauliSum or PauliTerm representing the input pauli operator
    """
    if not isinstance(pauli_operator, (PauliSum, PauliTerm)):
        raise TypeError(
            "pauli_operator must be an Orquestra PauliSum or PauliTerm object"
        )

    if isinstance(pauli_operator, PauliTerm):
        return _orq_to_pyquil_term(pauli_operator)

    terms = [_orq_to_pyquil_term(term) for term in pauli_operator.terms]
    paulisum = PyquilPauliSum(terms)

    return paulisum.simplify()


def pyquil_to_orq(
    pyquil_pauli: Union[PyquilPauliTerm, PyquilPauliSum]
) -> PauliRepresentation:
    """
    Convert a pyQuil PauliSum or PauliTerm to an Orquestra PauliSum or PauliTerm,
        respectively.

    Args:
        pyquil_pauli: pyQuil PauliTerm or PauliSum to convert to an Orquestra PauliTerm
            or PauliSum

    Returns:
        Orquestra PauliSum or PauliTerm representing the pyQuil PauliTerm or PauliSum
    """

    if not isinstance(pyquil_pauli, (PyquilPauliSum, PyquilPauliTerm)):
        raise TypeError("pyquil_pauli must be a pyquil PauliSum or PauliTerm object")

    if isinstance(pyquil_pauli, PyquilPauliTerm):
        return _pyquil_to_orq_term(pyquil_pauli)

    transformed_term = PauliSum()
    # iterate through the PauliTerms of PauliSum
    for pauli_term in pyquil_pauli.terms:
        transformed_term += _pyquil_to_orq_term(pauli_term)

    return transformed_term


def _orq_to_pyquil_term(orq_term: PauliTerm) -> PyquilPauliTerm:
    base_term = PyquilPauliTerm("I", 0)
    for idx, op in orq_term.operations:
        product = base_term * PyquilPauliTerm(op, idx)
        assert isinstance(product, PyquilPauliTerm)
        base_term = product
    return orq_term.coefficient * base_term


def _pyquil_to_orq_term(pyquil_term: PyquilPauliTerm) -> PauliTerm:
    try:
        return PauliTerm(pyquil_term._ops, pyquil_term.coefficient)  # type: ignore
    except TypeError:
        raise ValueError(
            "All qubit indices of pyQuil pauli must be integers. "
            "Offending term: {}".format(pyquil_term)
        )
