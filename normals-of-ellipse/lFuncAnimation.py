import numpy as np
from matplotlib.animation import FuncAnimation
from ellipseLib import *

a, b = 2, 1

# Set up arrays
scaleFactor = 2
y1s = np.linspace(-b * scaleFactor, b * scaleFactor, 50)
x1s = np.linspace(-a * scaleFactor / 2, a * scaleFactor / 2, 50)
t = np.linspace(0, 2 * np.pi, 1000)


# Generate the information for each frame of animation showing how the function and it's derivative change as we move the point to the same positions as in the other animation
animFrames = np.zeros([x1s.size * y1s.size, t.size])
mult = 1
frameNum = 0
for x1 in x1s:
	mult *= -1
	for y1 in y1s:
		animFrames[frameNum, :] = lFunc(t, a, b, x1, y1)[:]
		frameNum += 1

# Make the animation
fig, ax = plt.subplots()
animation = FuncAnimation(fig, lFuncAnimationFrame, frames = animFrames.shape[0], interval = 1, repeat = True, fargs = (ax, t, animFrames))
plt.show()