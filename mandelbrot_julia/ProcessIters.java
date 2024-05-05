public class ProcessIters extends Thread {
	private int iterations;
	private int startReIndex;
	private int endReIndex;
	private float[][] realIter;
	private float[][] imagIter;
	private int[][] numIters;

	// Only used when generating Mandelbrot set
	private float[] reRange;
	private float[] imRange;

	// Only used when generating Julia set
	private float reC;
	private float imC;

	// Tells run to generate the corret set
	private boolean mandelbrot;

	// Constructor for generating Mandelbrot set
	public ProcessIters(int iterations, int startReIndex, int endReIndex, float[] reRange, float[] imRange, float[][] realIter, float[][] imagIter, int[][] numIters) {
        super();
        
        this.iterations = iterations;
        this.startReIndex = startReIndex;
        this.endReIndex = endReIndex;
        this.reRange = reRange;
        this.imRange = imRange;
        this.realIter = realIter;
        this.imagIter = imagIter;
        this.numIters = numIters;
        this.mandelbrot = true;
    }

	// Constructor for generating Julia set
    public ProcessIters(int iterations, int startReIndex, int endReIndex, float[][] realIter, float[][] imagIter, float reC, float imC, int[][] numIters) {
        super();
        
        this.iterations = iterations;
        this.startReIndex = startReIndex;
        this.endReIndex = endReIndex;
        this.realIter = realIter;
        this.imagIter = imagIter;
        this.reC = reC;
        this.imC = imC;
        this.numIters = numIters;
        this.mandelbrot = false;
    }
    
    // Process all iterations for a subset of the plane
    public void run() {
		if (mandelbrot) mandelbrotRun();
		else juliaRun();
    }
    
    private void mandelbrotRun() {
        float[] iterRes = new float[2];
        for (int i = 0; i < iterations; i++) {
            for (int reIndex = startReIndex; reIndex < endReIndex; reIndex++) {
                // Real part of c
                float reC = reRange[reIndex];

                for (int imIndex = 0; imIndex < imRange.length; imIndex++) {
                    // If modulus of the current iteration is bigger than 2, ignore it
                    if (Math.sqrt(realIter[imIndex][reIndex] * realIter[imIndex][reIndex] + imagIter[imIndex][reIndex] * imagIter[imIndex][reIndex]) > 2) continue;
        
                    // Imaginary part of c
                    float imC = imRange[imIndex];

                    // Calculate z^2+c for z being the result of the previous iteration and c being the current point
                    iterRes = f(realIter[imIndex][reIndex], imagIter[imIndex][reIndex], reC, imC);
                    realIter[imIndex][reIndex] = iterRes[0];
                    imagIter[imIndex][reIndex] = iterRes[1];
                    numIters[imIndex][reIndex]++;
                }
            }
        }
    }
    
    private void juliaRun() {
        float[] iterRes = new float[2];
        for (int i = 0; i < iterations; i++) {
            for (int reIndex = startReIndex; reIndex < endReIndex; reIndex++) {
                for (int imIndex = 0; imIndex < realIter.length; imIndex++) {
                    // If modulus of the current iteration is bigger than 2, ignore it
                    if (Math.sqrt(realIter[imIndex][reIndex] * realIter[imIndex][reIndex] + imagIter[imIndex][reIndex] * imagIter[imIndex][reIndex]) > 2) continue;
                    
                    // Calculate z^2+c for z being the result of the previous iteration and c being the pre-defined constant
                    iterRes = f(realIter[imIndex][reIndex], imagIter[imIndex][reIndex], reC, imC);
                    realIter[imIndex][reIndex] = iterRes[0];
                    imagIter[imIndex][reIndex] = iterRes[1];
                    numIters[imIndex][reIndex]++;
                }
            }
        }
    }
    
    private float[] f(float reZ, float imZ, float reC, float imC) {
    	return new float[] {reZ * reZ - imZ * imZ + reC, 2 * reZ * imZ + imC};
	}
}
