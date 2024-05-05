import numpy as np
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
import sympy as sy

def lFunc(t, a, b, x1, y1):
	"""
	Return l(t) for the specified values of a, b, x1, y1
	"""
	return np.sqrt((a * np.cos(t) - x1) ** 2 + (b * np.sin(t) - y1) ** 2)

def dldtFunc(x, a, b, x1, y1):
	"""
	Return derivative of squared distance function (which is the top line of the derivative of the normal distance function), to use when solving numerically. We use x instead of t since that's what scipy.optimize.fsolve requires.
	"""
	return (a * (x1 - a * np.cos(x)) * np.sin(x) - b * (y1 - b * np.sin(x)) * np.cos(x))

xSym = sy.symbols("x", real = True, domain = sy.Interval(0, 2 * sy.pi))
aSym, bSym = sy.symbols("a, b", nonzero = True)
x1Sym, y1Sym = sy.symbols("x1, y1", real = True)
l = sy.sqrt((x1Sym - aSym * sy.cos(xSym)) ** 2 + (y1Sym - bSym * sy.sin(xSym))**2)
dldtFullFunc = sy.lambdify((xSym, aSym, bSym, x1Sym, y1Sym), sy.diff(l, xSym), "numpy")
"""
The analytical first derivative of l w.r.t. t, made using sympy. Used in the animation.
"""

def findAngles(a, b, x1, y1):
	"""
	Numerically find the azimuthal angles of the points on the ellipse such that the normal passing through that point also passes through (`x1`, `y1`)
	Returns four solutions within the interval [0,2*pi).
	"""
	sol = fsolve(dldtFunc, [0, np.pi / 2, np.pi, np.pi * 3 / 2], (a, b, x1, y1))
	return sol % (2 * np.pi)

def plotNormals(thetas, a, b, x1, y1, ax):
	"""
	Plot all the lines which go between (`x1`, `y1`) and each of the points on the ellipse with azimuthal angle in `thetas`, on axes `ax`
	"""
	# Set up plotting
	t = np.linspace(0, 2 * np.pi, 1000)
	x, y = a * np.cos(t), b * np.sin(t)

	# Plot the ellipse, point and lines
	ax.plot(x, y)
	ax.plot(x1, y1, "o")
	for theta in thetas:
		ax.plot([x1, a * np.cos(theta)], [y1, b * np.sin(theta)])
		ax.plot(a * np.cos(theta), b * np.sin(theta), "x")

	# Restrict the axes to be equal and within a sensible range
	# plt.axes("equal")
	ax.set_xlim(-a * 1.6, a * 1.6)
	ax.set_ylim(-a * 1.6, a * 1.6)

def ellipseAnimationFrame(iframe, ax1, ax2, ax3, a, b, t, allFrameThetas, points, lFrames, dldtFrames):
	"""
	Function to be passed to FuncAnimation which handles drawing individual frames.
	"""
	ax1.cla()
	plotNormals(allFrameThetas[iframe], a, b, points[iframe, 0], points[iframe, 1], ax1)

	# For setting limits
	lMin, lMax = np.min(lFrames), np.max(lFrames)
	dldtMin, dldtMax = np.min(dldtFrames), np.max(dldtFrames)

	ax2.cla()
	ax2.plot(t, lFrames[iframe])
	ax2.grid(visible = True)
	ax2.vlines(allFrameThetas[iframe], lMin - 5, lMax + 5, "r")
	ax2.set_xlim(np.min(t) - 0.1, np.max(t) + 0.1)
	ax2.set_ylim(lMin * 1.1, lMax * 1.1)

	ax3.cla()
	ax3.plot(t, dldtFrames[iframe])
	ax3.grid(visible = True)
	ax3.vlines(allFrameThetas[iframe], dldtMin - 5, dldtMax + 5, "r")
	ax3.hlines(0, -1, 10, "k")
	ax3.set_xlim(np.min(t) - 0.1, np.max(t) + 0.1)
	ax3.set_ylim(dldtMin * 1.1, dldtMax * 1.1)

	# Labels
	ax1.set_xlabel("$x(t)$")
	ax1.set_ylabel("$y(t)$")
	ax2.set_xlabel("$t$")
	ax2.set_ylabel("$l(t)$")
	ax3.set_xlabel("$t$")
	ax3.set_ylabel(r"$\dfrac{dl}{dt}$")

def showBig(numSols, x1Len = 10000, y1Len = 10000, deltax1 = 0.00022002200220022004, deltay1 =0.0005000500050005, a = 2, b = 1, showEllipse = True, showEvolute = True, showIm = True, saveIm = False, dpi = 400):
	"""
	Given the first quadrant of the number of normals image, make the full image. Default numerical values correspond to the images in the report.
	"""
	for i in range(numSols.shape[2]):
		plt.clf()

		# Make all four quadrants
		precIm = numSols[:, :, i]
		fullIm = np.zeros([y1Len * 2 - 1, x1Len * 2 - 1])
		topLeft = np.flip(np.flip(precIm, 1), 0)
		topRight = np.flip(precIm, 0)
		bottomLeft = np.flip(precIm, 1)
		fullIm[0:topLeft.shape[0], 0:topLeft.shape[1]] = topLeft[:, :]
		fullIm[0:topRight.shape[0], (topLeft.shape[1] - 1):(topLeft.shape[1] + topRight.shape[1] + 1)] = topRight[:, :]
		fullIm[(topLeft.shape[0] - 1):(topLeft.shape[0] + bottomLeft.shape[0] + 1), 0:bottomLeft.shape[1]] = bottomLeft[:, :]
		fullIm[(topRight.shape[0] - 1):(topRight.shape[0] + precIm.shape[0] + 1), (bottomLeft.shape[1] - 1):(bottomLeft.shape[1] + precIm.shape[1] + 1)] = precIm[:, :]

		plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
		plt.tick_params(axis='y', which='both', left=False, right=False, labelleft=False)

		plt.imshow(fullIm)
		plt.colorbar()

		# Plot the ellipse
		if showEllipse:
			t = np.linspace(0, 2 * np.pi, 10000, "r")
			plt.plot(a / deltax1 * np.cos(t) + fullIm.shape[1] / 2, b / deltay1 * np.sin(t) + fullIm.shape[0] / 2)

		# Plot the evolute
		if showEvolute:
			t = np.linspace(0, 2 * np.pi, 10000, "g")
			x, y = a * np.cos(t), b * np.sin(t)
			dxdt, dydt = -a * np.sin(t), b * np.cos(t)
			d2xdt2, d2ydt2 = -a * np.cos(t), -b * np.sin(t)
			X = x - (dydt * (dxdt ** 2 + dydt **2 )) / (dxdt * d2ydt2 - d2xdt2 * dydt)
			Y = y + (dxdt * (dxdt ** 2 + dydt ** 2)) / (dxdt * d2ydt2 - d2xdt2 * dydt)
			plt.plot(X / deltax1 + fullIm.shape[1] / 2, Y / deltay1 + fullIm.shape[0] / 2)

		# Save the image
		if saveIm:
			ellipseTxt = "ellipse" if showEllipse else ""
			evoluteTxt = "evolute" if showEvolute else ""
			plt.savefig(f"bigIm{i}-{ellipseTxt}-{evoluteTxt}.png", dpi = dpi, bbox_inches = "tight")

		# Show the image
		if showIm:
			plt.show()
