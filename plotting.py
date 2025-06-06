import copy
import warnings
import run_params
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm, colors
from io_funcs import verify_file_extension
from df_handling import unique_df, filter_df
from tb_helpers_v2025 import get_layer_energies, calc_freq
from run_params import EVENT_ID_COL, CHANNEL_COL, AMPLITUDE_COL, SHOWER_ENERGY_COL


def plot_1d_hist(data, ax=None, bin_num=None, bin_step=None, log=False, title='Histogram', x_label='',
                 y_label='Entries', path='./', out_filename=None, x_lim=None, y_lim=None):
    """
    Creates a 1D histogram of the data and saves.
    :param list data: Data desired to be plotted to a histogram
    :param matplotlib.pyplot.axes ax: Optional. Axes to plot histogram onto. If None, creates a new figure.
    :param int bin_num: Optional. Number of bins to be passed onto the histogram.
    :param int bin_step: Optional. Width of bins in histogram.
    :param bool log: Optional. Flag for using log scale for the y-axis. Default is False.
    :param str title: Optional. Title of the histogram. Default is 'Histogram'.
    :param str x_label: Optional. Label of the x-axis. Default is an empty string.
    :param str y_label: Optional. Label of the y-axis. Default is 'Entries'.
    :param str path: Optional. Path to which the plot will be saved. Default is current directory.
    :param str out_filename: Optional. File name of the histogram. Default is the title param.
    :param tuple x_lim: Optional. x-axis limits. Default is None.
    :param tuple y_lim: Optional. y-axis limits. Default is None.
    """
    # validate input data
    if data is None or len(data) == 0:
        warnings.warn("Cannot plot empty data.")
        return

    if ax is None:
        fig, ax = plt.subplots(1)
        save = True
    else:
        save = False

    if out_filename is None:
        out_filename = title

    bins = 'auto'
    if bin_num:
        bins = bin_num
    elif bin_step:
        min_val = min(np.min(data), 0)
        bins = get_equal_bins(min_val, np.max(data), step=bin_step)

    # calculate histogram statistics
    mean_val = np.mean(data)
    std_val = np.std(data)
    entry_count = len(data)

    # create histogram
    ax.hist(data, bins=bins, histtype='bar', ec='black')
    ax.grid(axis='y', alpha=0.75)  # add vertical grid

    # set labels etc. and save figure
    mean_str, std_str = set_significant_digits_str(mean_val, std_val)
    legend_lst = [f'Entries = {entry_count}\nMean Value = {mean_str}\nStd = {std_str}']
    style_fig(ax, title, x_label, y_label, x_lim, y_lim, log, legend_lst)
    if save:
        save_fig(fig, path, out_filename)

    
def scatter_plot(x, y, x_error=None, y_error=None, log=False, title='Scatter plot', x_label='', y_label='',
                 path='./', out_filename=None, x_lim=None, y_lim=None):
    """
    Creates a scatter plot of the data and saves.
    :param list x: x-axis data
    :param list y: y-axis data
    :param list x_error: Optional. x-axis errors. Default is None.
    :param list y_error: Optional. y-axis errors. Default is None.
    :param bool log: Optional. Flag for using log scale for the y-axis. Default is False.
    :param str path: Optional. Path to which the plot will be saved. Default is current directory.
    :param str title: Optional. Title of the plot. Default is 'Scatter plot'.
    :param str x_label: Optional. Label of x-axis. Default is an empty string.
    :param str y_label: Optional. Label of y-axis. Default is an empty string.
    :param str out_filename: Optional. File name of the histogram. Default is the title param.
    :param tuple x_lim: Optional. x-axis limits. Default is None.
    :param tuple y_lim: Optional. y-axis limits. Default is None.
    """

    if out_filename is None:
        out_filename = title

    fig, ax = plt.subplots(1)
    ax.errorbar(x, y, y_error, x_error, fmt='o', capsize=5)
    plt.xticks(x)  # Ensure all layer indices are shown
    plt.grid(True)

    style_fig(ax, title, x_label, y_label, x_lim, y_lim, log)
    save_fig(fig, path, out_filename)

    return


# plots the energy distribution for the given pad number in the given layer
def plot_channel_energy_dist(df, pad_num, layer_num):
    channel_df = filter_df(df, planes=layer_num, channels=pad_num)
    channel_energies = channel_df[AMPLITUDE_COL].to_numpy()
    path = run_params.RESULTS_DIR + f"/Run {run_params.RUN_NUM}/"
    path += f'Energy per channel/Layer {layer_num}/'
    plot_1d_hist(channel_energies, bin_step=1, title=f'Channel {pad_num} Layer {layer_num}', x_label='ADC counts',
                 path=path, out_filename=f'Channel_{pad_num}_layer_{layer_num}_energy_distribution.png')
    plt.close('all')


def plot_layer_energy_dist(df, layer_num, path, ax):
    layer_energies = get_layer_energies(df, layer_num)
    plot_1d_hist(layer_energies, ax, bin_step=10,
                 title=f'Total energy distribution - layer {layer_num}', x_label='ADC counts',
                 path=path, out_filename=f'Layer_{layer_num}_energy_distribution.png')


def plot_shower_energy_dist(df):
    showers = unique_df(df[[EVENT_ID_COL, SHOWER_ENERGY_COL]])
    shower_energies = showers[SHOWER_ENERGY_COL].to_numpy()
    path = run_params.RESULTS_DIR + f"/Run {run_params.RUN_NUM}/"
    plot_1d_hist(shower_energies, bin_step=100, title='Total energy distribution (showers)', x_label='ADC counts',
                 path=path, out_filename='Shower_energy_distribution.png')
    plt.close('all')


def plot_all_layers_energy_dist(df):
    layers = run_params.LAYERS

    # Create a figure and a 3x4 grid of subplots
    fig, ax = plt.subplots(3, 4, figsize=(30, 15), constrained_layout=True)
    ax = ax.flatten()  # Flatten the 2D array of axes for easy iteration

    path = run_params.RESULTS_DIR + f"/Run {run_params.RUN_NUM}/"
    for i, layer in enumerate(layers):
        ax_num = i
        if i >= 8:
            ax_num += 1
        plot_layer_energy_dist(df, layer, path, ax[ax_num])
        ax[ax_num].set_title(f"Layer {layer}")

    fig.delaxes(ax[8])
    fig.delaxes(ax[11])

    save_fig(fig, path=path, out_filename="Energy_dist_all_layers")
    plt.close('all')


def plot_heatmap(data, fig=None, ax=None, log=False, title='Heatmap', x_label='', y_label='', path='./',
                 out_filename=None, v_min=None, v_max=None):
    """
    Plots a 2D histogram of the data and saves.
    :param 2D-array data: 2D array of bin heights
    :param matplotlib.pyplot.figure fig: Optional. Figure to plot heatmap onto. If None, creates a new figure.
    :param matplotlib.pyplot.axes ax: Optional. Axes to plot heatmap onto. If None, creates a new figure.
    :param bool log: Optional. Flag for using log scale. Default is False.
    :param str title: Optional. Title of the heatmap. Default is 'Heatmap'.
    :param str x_label: Optional. Label of the x-axis. Default is an empty string.
    :param str y_label: Optional. Label of the y-axis. Default is an empty string.
    :param str path: Optional. Path to which the plot will be saved. Default is current directory.
    :param str out_filename: Optional. File name of the heatmap. Default is the title param.
    """

    if fig is None or ax is None:
        fig, ax = plt.subplots(1)
        save = True
    else:
        save = False

    if out_filename is None:
        out_filename = title

    # plot heatmap
    freq, cmap, colorscale = adjust_colors(data, log=log)
    im = ax.imshow(data, vmin=v_min, vmax=v_max, cmap=cmap, norm=colorscale)
    # for (i, j), z in np.ndenumerate(data):
    #     ax.text(j, i, '{:0.2f}'.format(z), ha='center', va='center')

    set_heatmap_properties(ax)

    # set labels etc. and save figure
    style_fig(ax, title, x_label, y_label)
    if save:
        save_fig(fig, path, out_filename)

    return im


def adjust_colors(data, log=False):
    data[data == 0] = -1
    cmap = copy.copy(cm.get_cmap("jet"))
    cmap.set_under('white')
    colorscale = colors.LogNorm() if log else None
    return data, cmap, colorscale


def set_heatmap_properties(ax):
    rows = 13
    cols = 20
    y_labels = [rows - i - 1 for i in range(rows)]
    ax.set_xticks(list(range(cols)))
    ax.set_yticks(list(range(rows)), labels=y_labels)

    # set grid lines to form pads visually
    for i in range(cols-1):
        if i < rows-1:
            ax.axhline(0.5 + i, color='gray', linewidth=0.5)
        ax.axvline(0.5 + i, color='gray', linewidth=0.5)


def plot_channel_frequency(df):
    num_events = len(np.unique(df[EVENT_ID_COL].to_numpy()))

    layers = run_params.LAYERS

    # Create a figure and a 3x4 grid of subplots
    fig, ax = plt.subplots(3, 4, figsize=(30, 15), constrained_layout=True)
    ax = ax.flatten()  # Flatten the 2D array of axes for easy iteration

    path = run_params.RESULTS_DIR + f"/Run {run_params.RUN_NUM}/"
    for i, layer in enumerate(layers):
        ax_num = i
        if i >= 8:
            ax_num += 1
        channel_data = filter_df(df, planes=layer)
        channel_data = unique_df(channel_data[[EVENT_ID_COL, CHANNEL_COL]])
        channel_hits = channel_data[CHANNEL_COL].to_numpy()
        freq = calc_freq(channel_hits)
        freq /= num_events
        im = plot_heatmap(freq, fig, ax[ax_num], x_label='Column', y_label='Row', path=path, v_min=0, v_max=1)
        ax[ax_num].set_title(f"Layer {layer}")

    fig.delaxes(ax[8])
    fig.delaxes(ax[11])

    fig.colorbar(im, ax=ax.ravel().tolist())
    save_fig(fig, path=path, out_filename="Channels_frequency_all_layers")
    plt.close('all')
    return


def plot_average_longitudinal_profile(df):
    layers = run_params.LAYERS
    mean_vals = []
    std_vals = []

    # Get average ADC for each layer
    for layer in layers:
        layer_data = get_layer_energies(df, layer)
        mean_vals.append(np.mean(layer_data))
        std_vals.append(np.std(layer_data) / np.sqrt(len(layer_data)))  # Optional: SEM

    path = run_params.RESULTS_DIR + f"/Run {run_params.RUN_NUM}/"
    scatter_plot(layers, mean_vals, y_error=std_vals, title='Average Longitudinal Profile', x_label='Layer Index',
                 y_label='ADC Average', path=path, out_filename='Average_Longitudinal_Profile')
    plt.close('all')


def style_fig(ax, title, x_label, y_label, x_lim=None, y_lim=None, y_log=False, legend_lst=None):
    # set axis limits
    if x_lim is not None:
        ax.set_xlim(x_lim[0], x_lim[1])
    if y_lim is not None:
        ax.set_ylim(y_lim[0], y_lim[1])
    if y_log:
        ax.set_yscale('log')
        y_label += ' (log scale)'

    # set labels and titles
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    if legend_lst is not None:
        ax.legend(legend_lst, loc='best')


def save_fig(fig, path, out_filename):
    full_path = path + f'/{out_filename}'
    full_path = verify_file_extension(full_path, '.png')
    fig.savefig(full_path)


def format_latex(num_val, sig_digits=3):
    """Format value with `×10^{}` style if large, otherwise regular float."""
    if sig_digits == 0:
        sig_digits = 3

    num_str = str(f"{num_val:.3g}")
    if "e" in num_str:
        exponent = int(np.floor(np.log10(abs(num_val))))
        mantissa = num_val / (10 ** exponent)
        return f"{mantissa:.{sig_digits - 1}f}×10$^{{{exponent}}}$"
    else:
        return num_str


def set_significant_digits_str(value, uncertainty):

    # Count sig digits in std (mantissa part) to match precision
    if uncertainty == 0:
        return format_latex(value), str(0)

    uncertainty_str = str(f"{uncertainty:.3g}")
    uncertainty_dec = 0
    uncertainty_dig = 0
    if "e" in uncertainty_str:
        return format_latex(value), format_latex(uncertainty)
    else:
        uncertainty_prec = len(uncertainty_str.split(".")[-1]) if "." in uncertainty_str else 0
        if uncertainty_prec > 0:
            uncertainty_dec += uncertainty_prec
        else:
            uncertainty_dig += len(uncertainty_str)

    if uncertainty_dec == 0:
        if uncertainty_dig > 0:
            value_str = str(f"{value:.{uncertainty_dig}g}")
        else:
            value_str = str(f"{value:.3g}")
    else:
        value_str = str(f"{value:.{uncertainty_dec}f}")

    return value_str, uncertainty_str


def get_equal_bins(min_val, max_val, step):
    return np.arange(min_val, max_val + step, step=step)