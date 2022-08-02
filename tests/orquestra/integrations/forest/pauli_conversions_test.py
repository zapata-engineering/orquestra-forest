################################################################################
# © Copyright 2021-2022 Zapata Computing Inc.
################################################################################
############################################################################
#   Copyright 2017 Rigetti Computing, Inc.
#   Modified by Zapata Computing 2020.
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

import numpy as np
import pytest
from orquestra.quantum.openfermion.ops import (
    FermionOperator,
    InteractionOperator,
    InteractionRDM,
)
from pyquil.paulis import PauliSum as PyquilPauliSum, PauliTerm as PyquilPauliTerm
from pyquil.quilatom import Expression, QubitPlaceholder
from orquestra.quantum.wip.operators import (
    PauliSum as OrqPauliSum,
    PauliTerm as OrqPauliTerm,
)

from orquestra.integrations.forest.conversions import pyquil_to_orq, orq_to_pyquil


def test_translation_type_enforcement():
    """
    Make sure type check works
    """
    create_one = FermionOperator("1^")
    empty_one_body = np.zeros((2, 2))
    empty_two_body = np.zeros((2, 2, 2, 2))
    interact_one = InteractionOperator(1, empty_one_body, empty_two_body)
    interact_rdm = InteractionRDM(empty_one_body, empty_two_body)

    with pytest.raises(TypeError):
        orq_to_pyquil(create_one)
    with pytest.raises(TypeError):
        orq_to_pyquil(interact_one)
    with pytest.raises(TypeError):
        orq_to_pyquil(interact_rdm)

    # don't accept anything other than pyquil PauliSum or PauliTerm
    with pytest.raises(TypeError):
        orq_to_pyquil(create_one)
    with pytest.raises(TypeError):
        orq_to_pyquil(interact_one)
    with pytest.raises(TypeError):
        orq_to_pyquil(interact_rdm)


def test_orq_paulisum_to_pyquil():
    """
    Conversion of PauliSum to pyquil; accuracy test
    """
    pauli_term = OrqPauliSum("0.5*X0*Z1*X2 + 0.5*Y0*Z1*Y2")

    forest_term = orq_to_pyquil(pauli_term)
    ground_truth = (
        PyquilPauliTerm("X", 0) * PyquilPauliTerm("Z", 1) * PyquilPauliTerm("X", 2)
    )
    ground_truth += (
        PyquilPauliTerm("Y", 0) * PyquilPauliTerm("Z", 1) * PyquilPauliTerm("Y", 2)
    )
    ground_truth *= 0.5

    assert ground_truth == forest_term
    assert isinstance(forest_term, PyquilPauliSum)


def test_orq_pauliterm_to_pyquil():
    """
    Conversion of PauliTerm to pyquil; accuracy test
    """
    pauli_term = OrqPauliTerm("2.25*Y0*X1*Z2*X4")

    pyquil_op = orq_to_pyquil(pauli_term)

    ground_truth = (
        PyquilPauliTerm("Y", 0)
        * PyquilPauliTerm("X", 1)
        * PyquilPauliTerm("Z", 2)
        * PyquilPauliTerm("X", 4)
        * 2.25
    )

    assert ground_truth == pyquil_op
    assert isinstance(pyquil_op, PyquilPauliTerm)


def test_orq_to_pyquil_zero():
    identity_term = OrqPauliTerm("I0", 0)
    forest_term = orq_to_pyquil(identity_term)
    ground_truth = PyquilPauliTerm("I", 0, 0)

    assert ground_truth == forest_term


def test_pyquil_pauliterm_to_orq():
    pyquil_term = PyquilPauliTerm("X", 0) * PyquilPauliTerm("Y", 5)
    orq_term = OrqPauliTerm("X0*Y5")

    test_orq_term = pyquil_to_orq(pyquil_term)
    assert test_orq_term == orq_term
    assert isinstance(test_orq_term, OrqPauliTerm)


def test_pyquil_paulisum_to_orq():
    pyquil_term = PyquilPauliSum([PyquilPauliTerm("X", 0) * PyquilPauliTerm("Y", 5)])
    orq_term = OrqPauliTerm("X0*Y5")

    test_orq_term = pyquil_to_orq(pyquil_term)
    assert test_orq_term == orq_term
    assert isinstance(test_orq_term, OrqPauliSum)


def test_pyquil_to_orq_type_enforced():
    """Enforce the appropriate type"""
    create_one = FermionOperator("1^")
    empty_one_body = np.zeros((2, 2))
    empty_two_body = np.zeros((2, 2, 2, 2))
    interact_one = InteractionOperator(1, empty_one_body, empty_two_body)
    interact_rdm = InteractionRDM(empty_one_body, empty_two_body)

    with pytest.raises(TypeError):
        pyquil_to_orq(create_one)
    with pytest.raises(TypeError):
        pyquil_to_orq(interact_one)
    with pytest.raises(TypeError):
        pyquil_to_orq(interact_rdm)

    # don't accept anything other than pyquil PyquilPauliSum or PyquilPauliTerm
    with pytest.raises(TypeError):
        pyquil_to_orq(create_one)
    with pytest.raises(TypeError):
        pyquil_to_orq(interact_one)
    with pytest.raises(TypeError):
        pyquil_to_orq(interact_rdm)


def test_pyquil_to_orq_raises_error_when_qubit_index_not_integer():
    with pytest.raises(ValueError) as e:
        pyquil_to_orq(PyquilPauliTerm("X", QubitPlaceholder()))
        assert "must be integer" in e.value
