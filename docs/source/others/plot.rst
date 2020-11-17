Plotting template
=================

.. _plot-usage:

Usage
-----

Plot objects that inherit from the template plot classes have the following properties.

- Fast plotting by use of `matplotlib.canvas.blit`.
- Redrawing past iterations of the figure by storing all changes in history.
- Keyboard navigation for iteration selection.
- Plot object information by picking.

When the focus is on the figure, indicated by a green circle in the bottom right corner, the user can navigate through the history of the figure by the commands below. 

==================  ==============================================
key                 function
==================  ==============================================
h                   show help
i                   show all iterations
enter or right      go to next iteration, enter iteration number
backspace or left   go to previous iteration
n                   go to newest iteration
0-9                 input iteration number
==================  ==============================================

If the focus is lost, it can be regained by calling `template.focus` on the plot object. 

Default values for plot properties such as colors and linewidths are saved in a *plot.ini* file. Any plot property can be overwritten by supplying the override value as a keyword argument during object initialization or a custom *plot.ini* file in the working directory.


Development
-----------

.. automodule:: qsurface.plot
    :members:
    :member-order: bysource