"""Spatial position and occupancy related functions."""

import numpy as np
import pandas as pd

###################################################################################################
###################################################################################################

def compute_spatial_bin_edges(position, bins, area_range=None):
    """Compute spatial bin edges.

    Parameters
    ----------
    position : 2d array
        Position values across a 2D space.
    bins : list of [int, int]
        The number of bins to divide up the space, defined as [number of x_bins, number of y_bins].
    area_range : list of list, optional
        Edges of the area to bin, defined as [[x_min, x_max], [y_min, y_max]].
        Any values outside this range will be considered outliers, and not used to compute edges.

    Returns
    -------
    x_edges, y_edges : 1d array
        Edge definitions for the spatial binning.

    Examples
    --------
    Compute bin edges for an example rectangular field, with x-range of 1 - 5 & y-range of 6 - 10:
    So, position points are: (1, 6), (2, 7), (3, 8), (4, 9), (5, 10).

    >>> position = np.array([[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]])
    >>> bins = [5, 4]
    >>> compute_spatial_bin_edges(position, bins)
    (array([1. , 1.8, 2.6, 3.4, 4.2, 5. ]), array([ 6.,  7.,  8.,  9., 10.]))
    """

    _, x_edges, y_edges = np.histogram2d(position[0, :], position[1, :],
                                         bins=bins, range=area_range)

    return x_edges, y_edges


def compute_spatial_bin_assignment(position, x_edges, y_edges, include_edge=True):
    """Compute spatial bin assignment.

    Parameters
    ----------
    position : 2d array
        Position information across a 2D space.
    x_edges, y_edges : 1d array
        Edge definitions for the spatial binning.
        Values within the arrays should be monotonically increasing.
    include_edge : bool, optional, default: True
        Whether to include positions on the edge into the bin.

    Returns
    -------
    x_bins, y_bins : 1d array
        Bin assignments for each position.

    Notes
    -----
    - In the case of zero outliers (all positions are between edge ranges), the returned
      values are encoded as bin position, with values between {1, n_bins}.
    - If there are outliers (some position values that are outside the given edges definitons),
      these are encoded as 0 (left side) or n_bins + 1 (right side).
    - By default position values equal to the left-most & right-most edges are treated as
      within the bounds (not treated as outliers), unless `include_edge` is set as False.

    Examples
    --------
    Compute bin assignment of position, given existing spatial bins:

    >>> position = np.array([[1.5, 2.5, 3.5, 5], [6.5, 7.5, 8.5, 9]])
    >>> x_edges = np.array([1, 2, 3, 4, 5])
    >>> y_edges = np.array([6, 7, 8, 9, 10])
    >>> x_bins, y_bins = compute_spatial_bin_assignment(position, x_edges, y_edges)
    """

    x_bins = np.digitize(position[0, :], x_edges, right=False)
    y_bins = np.digitize(position[1, :], y_edges, right=False)

    if include_edge:
        x_bins = _include_bin_edge(position[0, :], x_bins, x_edges, side='left')
        y_bins = _include_bin_edge(position[1, :], y_bins, y_edges, side='left')

    return x_bins, y_bins


def compute_bin_time(timestamps):
    """Compute the time duration of each position sample.

    Parameters
    ----------
    timestamps : 1d array
        Timestamps.

    Returns
    -------
    1d array
        Width, in time, of each bin.

    Examples
    --------
    Compute times between timestamp samples:

    >>> timestamp = np.array([0, 10, 30, 60, 80, 90])
    >>> compute_bin_time(timestamp)
    array([10, 20, 30, 20, 10,  0])
    """

    return np.append(np.diff(timestamps), 0)


def compute_occupancy(position, timestamps, bins, speed=None, speed_thresh=5e-6,
                      area_range=None, set_nan=False, normalize=False):
    """Compute occupancy across spatial bin positions.

    Parameters
    ----------
    position : 2d array
        Position information across a 2D space.
    timestamps : 1d array
        Timestamps.
    bins : list of int
        Binning to use for dividing up the space.
    speed : 1d array
        Current speed for each position.
        Should be the same length as timestamps.
    speed_thresh : float, optional
        Speed threshold to apply.
    area_range : list of list, optional
        Edges of the area to bin, defined as [[x_min, x_max], [y_min, y_max]].
    set_nan : bool, optional, default: False
        Whether to set zero occupancy locations as NaN.
    normalize : bool, optional, default: False
        Whether to normalize occupancy to sum to 1.

    Returns
    -------
    2d array
        Occupancy.

    Examples
    --------
    Get occupancy for points:
    (x, y) =  (1, 6), (2, 7), (3, 8), (4, 9), (5, 10), (0, 0), (1, 6), (2, 6), (5, 4).

    >>> position = np.array([[1, 2, 3, 4, 5, 0, 1, 2, 5], [6, 7, 8, 9, 10, 0, 6, 6, 4]])
    >>> timestamps = np.linspace(0, 1000, position.shape[1])
    >>> bins = [5, 5]
    >>> occ = compute_occupancy(position, timestamps, bins)
    """

    # Compute spatial bins & binning
    x_edges, y_edges = compute_spatial_bin_edges(position, bins, area_range)
    x_bins, y_bins = compute_spatial_bin_assignment(position, x_edges, y_edges)
    bin_time = compute_bin_time(timestamps)

    # Make a temporary pandas dataframe
    df = pd.DataFrame({
        'xbins' : pd.Categorical(x_bins, categories=list(range(1, bins[0] + 1)), ordered=True),
        'ybins' : pd.Categorical(y_bins, categories=list(range(1, bins[1] + 1)), ordered=True),
        'bin_time' : bin_time})

    # Apply the speed threshold (dropping slow / stationary timepoints)
    if np.any(speed):
        df = df[speed > speed_thresh]

    # Group each position into a spatial bin, summing total time spent there
    df = df.groupby(['xbins', 'ybins'])['bin_time'].sum()

    # Extract and re-organize occupancy into 2d array
    occ = np.squeeze(df.values.reshape(*bins, -1)) / 1000

    if normalize:
        occ = occ / np.sum(occ)

    if set_nan:
        occ[occ == 0.] = np.nan

    return occ


def _include_bin_edge(position, bin_pos, edges, side='left'):
    """Update bin assignment so last bin includes edge values.

    Parameters
    ----------
    position : 1d array
        The position values.
    bin_pos : 1d array
        The bin assignment for each position.
    edges : 1d array
        The bin edge definitions.
    side : {'left', 'right'}
        Which side was used to compute bin assignment.

    Returns
    -------
    bin_pos : 1d array
        The bin assignment for each position.

    Notes
    -----
    For any position values that exactly match the left-most or right-most bin edges, by default
    (from np.digitize), one of these sides will be considered an outlier. This is because bin
    assignment is computed as `pos >= left_bin_edge & pos < right_bin_edge (flipped if right=True).
    To address this, this function resets position values == edges as with the bin on the edge.
    """

    if side == 'left':

        # If side left, right position == edge gets set as len(bins), so decrement by 1
        mask = position == edges[-1]
        bin_pos[mask] = bin_pos[mask] - 1

    elif side == 'right':

        # If side right, left position == edge gets set as 0, so increment by 1
        mask = position == edges[0]
        bin_pos[mask] = bin_pos[mask] + 1

    else:
        raise ValueError("Input for 'side' not understood.")

    return bin_pos
