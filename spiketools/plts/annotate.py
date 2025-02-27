"""Helper functions to annotate plots with extra elements / information."""

import matplotlib.pyplot as plt

###################################################################################################
###################################################################################################

def _add_vlines(vline, ax, **plt_kwargs):
    """Add vertical line(s) to a plot axis.

    Parameters
    ----------
    vline : float or list
        Positions(s) of the vertical lines to add to the plot.
    ax : Axes, optional
        Axis object upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    if vline is not None:
        vline = [vline] if isinstance(vline, (int, float)) else vline
        for line in vline:
            ax.axvline(line, **plt_kwargs)


def _add_shade(shade, ax, **plt_kwargs):
    """Add vertical shading to a plot axis.

    Parameters
    ----------
    shade : list of float
        Region of the plot to shade in.
    ax : Axes, optional
        Axis object upon which to plot.
    plt_kwargs
        Additional arguments to pass into the plot function.
    """

    if shade is not None:
        ax.axvspan(*shade, **plt_kwargs)


def _add_significance_to_plot(stats, sig_level=0.05, x_vals=None, ax=None):
    """Add markers to a plot to label statistical significance.

    Parameters
    ----------
    stats : list
        Statistical results, including p-values, to use to annotate the plot.
        List can contain floats, or statistical results if it has a `pvalue` field.
    sig_level : float, optional, default: 0.05
        Threshold level to consider a result significant.
    x_vals : 1d array, optional
        Values for the x-axis, for example time values or bin numbers.
        If not provided, x-values are accessed from the plot.
    ax : Axes, optional
        Axis object upon which to plot.
    """

    if not ax:
        ax = plt.gca()

    if not x_vals:
        x_vals = ax.lines[0].get_xdata()

    if not isinstance(stats[0], (float)):
        stats = [stat.pvalue for stat in stats]

    for ind, stat in enumerate(stats):
        if stat < sig_level:
            ax.plot(x_vals[ind], 0, '*', color='black')
