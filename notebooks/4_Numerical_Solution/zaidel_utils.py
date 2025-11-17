
import flopy
from flopy.plot.styles import styles

import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

hclose = 1.0e-6

def plot_results(sim, confined=True, show_spdis=False):
    figure_size = (6.3, 5.0)

    with styles.USGSMap():
    
        # plot head
        gwf_model = sim.get_model()
        delr = gwf_model.modelgrid.delr[0]
        ncol = gwf_model.modelgrid.ncol

        vmin, vmax = 0, 25
        bot_arr = gwf_model.dis.botm.array
        xedge = gwf_model.modelgrid.xvertices[0]
        zedge = np.array([bot_arr[0, 0, 0]] + bot_arr.flatten().tolist())

        # Create figure for simulation
        extents = (0, ncol * delr, -1, 25.0)
        fig, (ax1, ax2) = plt.subplots(
            2,
            1,
            figsize=figure_size,
            dpi=300,
            constrained_layout=True,
        )

        ax1.set_yscale('linear')

        ax1.set_xlim(extents[:2])
        ax1.set_ylim(extents[2:])

        # model cross section
        fmp = flopy.plot.PlotCrossSection(
            model=gwf_model, ax=ax1, extent=extents, line={"row": 0}
        )
        ax1.fill_between(xedge, zedge, y2=-1, color="0.75", step="pre", lw=0.0)

        # plot head
        head = gwf_model.output.head().get_data()
        wt = head
        if confined:
            wt = None
        pa = fmp.plot_array(head, head=wt, vmin=vmin, vmax=vmax)

        fmp.plot_bc("CHD", color="cyan", head=head)
        ax1.set_xlabel("x-coordinate, in meters")
        ax1.set_ylabel("Elevation, in meters")

        # create legend
        ax1.plot(
            -10000,
            -10000,
            lw=0,
            marker="s",
            ms=10,
            mfc="cyan",
            mec="cyan",
            label="Constant Head",
        )
        ax1.plot(
            -10000,
            -10000,
            lw=0,
            marker="s",
            ms=10,
            mfc="0.75",
            mec="0.75",
            label="Model Base",
        )
        styles.graph_legend(ax1, ncol=2, loc="upper right")

        # plot colorbar
        cax = plt.axes([0.60, 0.82, 0.325, 0.025])
        cbar = plt.colorbar(pa, shrink=0.8, orientation="horizontal", cax=cax)
        cbar.ax.tick_params(size=0)
        cbar.ax.set_xlabel(r"Head, $m$", fontsize=9)

        if show_spdis:
            cbc = gwf_model.output.budget().get_data(text="DATA-SPDIS")[0]
            fmp.plot_vector(cbc["qx"], cbc["qy"], cbc["qz"])

        
        ims_csv = os.path.join(sim.sim_path, "ims.csv")
        df = pd.read_csv(ims_csv)        
        x_ninners = df["total_inner_iterations"].array
        y_dvmax = abs(df["solution_inner_dvmax"].array)      
        ax2.plot(x_ninners, y_dvmax, label="dvmax")
        ax2.set_xlabel("inner iteration number")
        ax2.set_ylabel("dvmax")

        nr_iters = df["total_inner_iterations"].array[-1]
        min_y = 10e-2 * min(y_dvmax)
        max_y = 10e+3 * max(y_dvmax)

        # mark next outer
        nouter_diff = [int(df["nouter"][i + 1] - df["nouter"][i]) for i in range(df["nouter"].size - 1)]
        new_outers = np.where(np.asarray(nouter_diff) == 1)[0] + 1
        for idx_outer in new_outers:
            ax2.vlines(idx_outer + 0.5, min_y, max_y, color='grey', linestyle='dashed', linewidth=0.8)
        ax2.hlines(hclose, 1, nr_iters, color='darkgreen', label="dvclose")

        ax2.set_ylim(min_y, max_y)
        ax2.set_yscale("log")
        ax2.xaxis.set_major_locator(mpl.ticker.MaxNLocator(integer=True))
        styles.graph_legend(ax2, ncol=2, loc="upper right")

        plt.show()