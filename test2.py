import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.patches import Circle
from mpl_toolkits.mplot3d import art3d
from matplotlib.blocking_input import BlockingInput

# class BlockingKeyInput(BlockingInput):
#     """Blocking class to receive key presses.

#     See Also
#     --------
#     `matplotlib.blocking_input.BlockingInput` : Inherited blocking class.
#     """

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, eventslist=("button_press_event", "key_press_event"), **kwargs)

#     def __call__(self, timeout=30):
#         """Blocking call to retrieve a single key press."""
#         return super().__call__(n=1, timeout=timeout)[-1]


# def wait_fig(blocker):
#     blocker.fig.canvas.draw()
#     while True:
#         event = blocker(-1)
#         if event.key in ["enter", "right"]:
#             break

fig = plt.figure()
# blocker = BlockingKeyInput(fig)
ax = plt.axes(projection="3d")
circle = Circle((0.5,0.5))
ax.add_patch(circle)
art3d.patch_2d_to_3d(circle)

circle.set_facecolor("r")

fig.canvas.draw()
print(circle.get_facecolor())


# wait_fig(blocker)
# circle.set_facecolor((1,0,0,1))


# wait_fig(blocker)

# print()
# circle.set_facecolor((1,1,0,1))
# wait_fig(blocker)