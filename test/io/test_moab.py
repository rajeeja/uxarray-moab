import importlib.util

import pytest

import uxarray as ux
from uxarray.io._moab import _moab_connectivity_to_indices


def test_moab_connectivity_maps_handles_to_zero_based_indices():
    vertices = [10, 20, 30, 40]
    connectivity = [[10, 20, 30], [10, 30, 40]]

    assert _moab_connectivity_to_indices(vertices, connectivity) == [
        [0, 1, 2],
        [0, 2, 3],
    ]


def test_moab_backend_requires_optional_pymoab_when_missing():
    if importlib.util.find_spec("pymoab") is not None:
        pytest.skip("pymoab is installed in this environment")

    with pytest.raises(ImportError, match="pymoab"):
        ux.Grid.from_file("dummy.h5m", backend="moab")
