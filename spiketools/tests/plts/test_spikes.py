"""Tests for spiketools.plts.spikes"""

import numpy as np

from spiketools.tests.tutils import plot_test
from spiketools.tests.tsettings import TEST_PLOTS_PATH

from spiketools.plts.spikes import *

###################################################################################################
###################################################################################################

@plot_test
def test_plot_waveform(twaveform):

    plot_waveform(twaveform,
                  file_path=TEST_PLOTS_PATH, file_name='tplot_waveform1.png')

    plot_waveform(np.array([twaveform, twaveform + 1, twaveform -1]),
                  average='mean', shade='var', add_traces=True,
                  file_path=TEST_PLOTS_PATH, file_name='tplot_waveform2.png')

@plot_test
def test_plot_waveforms3d(twaveform):

    plot_waveforms3d(np.arange(len(twaveform)), np.vstack([twaveform] *  3),
                     file_path=TEST_PLOTS_PATH, file_name='tplot_waveforms3d.png')

@plot_test
def plot_spikehist2d(twaveform):

    plot_spikehist2d(np.arange(len(twaveform)), np.vstack([twaveform] *  3),
                     file_path=TEST_PLOTS_PATH, file_name='tplot_spikehist2d.png')

@plot_test
def test_plot_isis(tisis):

    plot_isis(tisis,
              file_path=TEST_PLOTS_PATH, file_name='tplot_isis.png')

@plot_test
def test_plot_unit_frs():

    plot_unit_frs(np.array([2.5, 0.5, 1.2, 3.4]),
                  file_path=TEST_PLOTS_PATH, file_name='tplot_units_frs.png')
