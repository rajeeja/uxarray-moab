from pymoab import core, types
import numpy as np
from uxarray.grid.coordinates import xyz_to_lonlat_deg
from uxarray.constants import INT_DTYPE, INT_FILL_VALUE
from uxarray.conventions import ugrid


def _read_moab(filename):
    """Reads in a MOAB formatted mesh file and encodes it in the UGRID
    conventions.

    Parameters
    ----------
    filename: str
        Path to the MOAB mesh file.

    Returns
    -------
    out_ds: xr.Dataset
        MOAB mesh encoded in the UGRID conventions.
    source_dims_dict: dict
        Mapping of MOAB dimensions to UGRID dimensions.
    """

    # Initialize MOAB core
    mb = core.Core()

    # Load the mesh file
    mb.load_file(filename)

    # Get all vertices
    vertices = mb.get_entities_by_type(0, types.MBVERTEX)
    coords = mb.get_coords(vertices).reshape(-1, 3)  # Assuming 3D coordinates

    # Get 2D polygonal elements
    elements = mb.get_entities_by_dimension(0, 2)

    # Get connectivity for each polygon
    connectivity = [mb.get_connectivity(e) for e in elements]

    # Ensure all indices are 0-based if necessary (adjust for 1-based indexing)
    connectivity = [[idx - 1 for idx in face] for face in connectivity]

    # Convert to spherical coordinates (longitude, latitude)
    lon, lat = xyz_to_lonlat_deg(coords)

    # Convert connectivity list to numpy array, ensuring it is the correct shape
    max_face_nodes = max(len(face) for face in connectivity)
    face_node_connectivity = np.full((len(connectivity), max_face_nodes),
                                     INT_FILL_VALUE,
                                     dtype=INT_DTYPE)

    # Populate the array
    for i, face in enumerate(connectivity):
        face_node_connectivity[i, :len(face)] = face

    # Create the output dataset
    out_ds = ux.Dataset()
    out_ds[ugrid.NODE_COORDINATES[0]] = xr.DataArray(
        lon, dims=[ugrid.NODE_DIM], attrs=ugrid.NODE_LON_ATTRS)
    out_ds[ugrid.NODE_COORDINATES[1]] = xr.DataArray(
        lat, dims=[ugrid.NODE_DIM], attrs=ugrid.NODE_LAT_ATTRS)
    out_ds["face_node_connectivity"] = xr.DataArray(
        data=face_node_connectivity,
        dims=ugrid.FACE_NODE_CONNECTIVITY_DIMS,
        attrs=ugrid.FACE_NODE_CONNECTIVITY_ATTRS,
    )

    source_dims_dict = {
        "n_nodes": ugrid.NODE_DIM,
        "n_faces": ugrid.FACE_DIM,
    }

    return out_ds, source_dims_dict