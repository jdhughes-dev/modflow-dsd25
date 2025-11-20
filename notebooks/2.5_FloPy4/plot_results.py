import flopy
import matplotlib.pyplot as plt

MOSAIC = [["a"], ["b"], ["c"]]
cbar_kwargs = {"location": "bottom"}

def plot_heads(head4, head3, workspace, layer=0, time=0):
    with flopy.plot.styles.USGSMap():
        fig, axd = plt.subplot_mosaic(
            MOSAIC,
            figsize=(4,8),
            layout="constrained",
            sharey=True,
            )

    # Plot head results
    ax = axd["a"]
    head4.isel(layer=layer, time=time).plot.contourf(ax=ax, cbar_kwargs=cbar_kwargs)
    ax.set_title("FloPy 4 TWRI Head")
 
    ax = axd["b"]
    head3.isel(layer=layer, time=time).plot.contourf(ax=ax, cbar_kwargs=cbar_kwargs)
    ax.set_title("FloPy 3 TWRI Head")

    diff43 = head4 - head3
    ax = axd["c"]
    diff43.isel(layer=layer, time=time).plot.contourf(ax=ax, cbar_kwargs=cbar_kwargs)
    ax.set_title("FloPy 4 - FloPy 3 TWRI Head")

    for ax in axd.values():
        ax.set_ylabel("y")
        ax.grid(True)
 
    fig.savefig(workspace / "head.png", dpi=300)