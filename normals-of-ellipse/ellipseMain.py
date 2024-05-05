from ellipseLib import *
import time
import threading

def threadFn(a, b, i, startJ, endJ, x1s, y1, precs):
	"""
	Function which is executed on a single thread. Each thread evaluates an equal amount of a row of the image.
	"""
	for j in range(startJ, endJ):
		sol = findAngles(a, b, x1s[j], y1)

		# Assume that any solutions which are the same to certain number of d.p. are the same
		for k in range(len(precs)):
			numSols[i, j, k] = len(np.unique(np.round(sol, precs[k])))

choice = int(input("Enter option:\nGenerate new (0)\nContinue previous (1)\nShow complete (2): "))

a, b = 2, 1

# Generate a grid of points on which to solve (we only consider the first quadrant, the rest is symmetric)
x1s = np.linspace(0, a * 1.1, 10000)
y1s = np.linspace(0, b * 5, 10000)

if choice == 0:
	# Make a new image
	numThreads = int(input("Number of threads: "))
	startTime = time.time()

	# List of number of decimal places to consider solutions the same
	precs = [3, 5, 7, 9]

	# Array to store the number of solutions for the point (x1s[i], y1s[j])
	numSols = np.zeros([len(y1s), len(x1s), len(precs)])

	filename = input("Enter filename (_ to not save): ")
	saveFreq = int(input("How often should the file be saved? "))

	# Find the number of solutions for every point on the grid
	for i, y1 in enumerate(y1s):
		print(i, y1)

		# Split the work among the threads
		numPerThread = int(len(x1s) / numThreads)
		threads = []
		for j in range(numThreads):
			threads.append(threading.Thread(target = threadFn, args = (a, b, i, j * numPerThread, (j + 1) * numPerThread, x1s, y1, precs)))
			threads[j].start()

		for t in threads:
			t.join()

		if i % saveFreq == 0:
			if filename != "_": np.save(f"{filename}.npy", numSols)
			print(f"File saved to {filename}.npy")

	endTime = time.time()
	print(f"{x1s.size * y1s.size} points took {endTime - startTime}s")

	# Save the points
	if filename != "_": np.save(f"{filename}.npy", numSols)
	print(f"File saved to {filename}.npy")
elif choice == 1:
	# Continue from a given file
	numThreads = int(input("Number of threads: "))

	# List of number of decimal places to consider solutions the same
	precs = [3, 5, 7, 9]

	# Get the file
	filename = int(input("Enter filename (with extension): "))
	numSols = np.load(filename)
	saveFreq = int(input("How often should the file be saved? "))

	# Find where we left off
	i1 = np.min(np.where(numSols == 0)[0])

	# Find the number of solutions for every point on the grid
	for i, y1 in enumerate(y1s):
		# Skip to where we left off
		if i < i1:
			print(f"Skipping {i}")
			continue

		print(i, y1)

		# Split the work among the threads
		numPerThread = int(len(x1s) / numThreads)
		threads = []
		for j in range(numThreads):
			threads.append(threading.Thread(target = threadFn, args = (a, b, i, j * numPerThread, (j + 1) * numPerThread, x1s, y1, precs)))
			threads[j].start()

		for t in threads:
			t.join()

		if i % saveFreq == 0:
			if filename != "_": np.save(f"{filename}.npy", numSols)
			print(f"File saved to {filename}.npy")

	# Save the points
	np.save(f"{filename}.npy", numSols)
	print(f"File saved to {filename}.npy")
elif choice == 2:
	# Show a complete image, from a given file
	filename = input("Enter filename (with extension): ")
	showEllipse = True if input("Show ellipse? ")[0].lower() == "y" else False
	showEvolute = True if input("Show evolute? ")[0].lower() == "y" else False
	showImages = True if input("Show images? ")[0].lower() == "y" else False
	saveImages = True if input("Save images? ")[0].lower() == "y" else False
	dpi = input("Enter dpi (_ for default): ")
	numSols = np.load(filename)

	# Generate the full image(s)
	if dpi == "_":
		showBig(numSols, x1s.shape[0], y1s.shape[0], x1s[1] - x1s[0], y1s[1] - y1s[0], a, b, showEllipse = showEllipse, showEvolute = showEvolute, showIm = showImages, saveIm = saveImages)
	else:
		showBig(numSols, x1s.shape[0], y1s.shape[0], x1s[1] - x1s[0], y1s[1] - y1s[0], a, b, showEllipse = showEllipse, showEvolute = showEvolute, dpi = int(dpi), showIm = showImages, saveIm = saveImages)