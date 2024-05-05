from ellipseLib import *
from matplotlib.animation import FuncAnimation

a, b, = 2, 1

scaleFactor = 1.5
y1s = np.linspace(-b * scaleFactor, b * scaleFactor, 50)
x1s = np.linspace(-a * scaleFactor, a * scaleFactor, 50)

t = np.linspace(0, 2 * np.pi, 1000)
allFrameThetas = [] # List of lists of angles of points to use
points = np.zeros([x1s.size * y1s.size, 2]) # The points corresponding to the angles in allFrameThetas
lFrames = np.zeros([x1s.size * y1s.size, t.size]) # The values of l to plot against t
dldtFrames = np.zeros([x1s.size * y1s.size, t.size]) # The values of dl/dt to plot against t

# Get solution for a grid of points
frameNum = 0
mult = 1 # This is just to make the animation look nicer
for x1 in x1s:
	mult *= -1
	for y1 in y1s:
		# Assume that any solutions which are the same to 5 d.p. are the same
		sol = findAngles(a, b, x1, mult * y1)
		sol = np.unique(np.round(sol, 5))
		allFrameThetas.append(sol)
		points[frameNum, :] = np.array([x1, mult * y1])

		# Calculate l(t)
		lFrames[frameNum, :] = lFunc(t, a, b, x1, mult * y1)

		# Calculate dl(t)/dt
		dldtFrames[frameNum, :] = dldtFullFunc(t, a, b, x1, mult * y1)[:]

		frameNum += 1

# Make the animation
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize = (7, 17))
animation = FuncAnimation(fig, ellipseAnimationFrame, frames = len(allFrameThetas), interval = 5, repeat = True, fargs = (ax1, ax2, ax3, a, b, t, allFrameThetas, points, lFrames, dldtFrames))
# animation.save("fullAnimation.gif", writer = "pillow", progress_callback = lambda i, n: print(f'Saving frame {i}/{n}'))
plt.show()