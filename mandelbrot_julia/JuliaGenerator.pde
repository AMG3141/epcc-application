class JuliaGenerator extends PApplet {
    // Original limits (where it is reset to when pressing 'f')
    float[] originalLimits;
    
    // Limits of the calculation (minRe, maxRe, minIm, maxIm)
    float[] limits;
    
    // Arrays to store the real and imaginary parts of the current iteration
    float[][] realIter;
    float[][] imagIter;
    
    // Array to hold the unmber of iterations until modulus is bigger than 2
    int[][] numIters;
    
    // The real and imaginary parts of the plane
    float[] reRange;
    float[] imRange;
    
    // For drawing to the screen
    int drawX;
    int drawY;
    int drawWidth;
    int drawHeight;
    float scaleFactor;
    
    // Value of c for which the current set is being generated
    float reC;
    float imC;
    
    // Number of threads
    int numThreads;
    
    // Path to save things to
    String path;
	
	JuliaGenerator(float[] originalLimits_, int numThreads_, String path_) {
        this.originalLimits = originalLimits_;
        limits = new float[this.originalLimits.length];
        arrayCopy(originalLimits, limits);
        this.numThreads = numThreads_;
        this.path = path_;
        
        PApplet.runSketch(new String[] {this.getClass().getName()}, this);
	}

    void settings() {
        size(1000, 1000);
    }
    
	void setup() {
		reC = 0;
		imC = 0;
		generateSet(true);
	}

	void draw() {
        noStroke();
        background(0);
    
        // Only draw the portion which can be seen on screen
        for (int i = 0; i < numIters.length; i++) {
            if ((i - drawY) * scaleFactor < 0 || (i - drawY) * scaleFactor > height) continue;
            for (int j = 0; j < numIters[i].length; j++) {
                if ((j - drawX) * scaleFactor < 0 || (j - drawX) * scaleFactor > width) continue;
            
                int x = numIters[i][j];
                if (0 <= x && x < iterations / 3) fill(0, 3 * x, 0);
                else if (iterations / 3 <= x && x < iterations * 2 / 3) fill(3 * x, 255, 0);
                else if (iterations * 2 / 3 <= x && x < iterations) fill(255, 255, 3 * x);
                else fill(0);
                                
                //fill(255 - x);
                
                rect((j - drawX) * scaleFactor, height - (i - drawY) * scaleFactor - 1, scaleFactor, scaleFactor);
            }
        } 
	}

    void keyPressed() {
        if (keyCode == UP) drawY += 10;
        if (keyCode == DOWN) drawY -= 10;
        if (keyCode == RIGHT) drawX += 10;
        if (keyCode == LEFT) drawX -= 10;
    
        if (key == '+' || key == '=') scaleFactor += 0.1;
        if (key == '-') scaleFactor -= 0.1;
        
        // Re*c*enter
        if (key == 'c') {
            drawX = 0;
            drawY = 0;
            scaleFactor = 1;
        }
        
        // *R*egenerate
        if (key == 'r') {
            // Regenerate the set for the visible portion of the screen (only works for zooming in)
            limits = new float[] {int(drawX), int(width / scaleFactor + drawX), int(drawY), int(height / scaleFactor + drawY)};
            
            // Make sure it won't break
            if (limits[0] < 0) limits[0] = reRange[0];
            else limits[0] = reRange[int(limits[0])];
            if (limits[1] >= reRange.length) limits[1] = reRange[reRange.length - 1];
            else limits[1] = reRange[int(limits[1])];
            
            if (limits[2] < 0) limits[2] = 0;
            else limits[2] = imRange[int(limits[2])];
            if (limits[3] >= imRange.length) limits[3] = imRange[imRange.length - 1];
            else limits[3] = imRange[int(limits[3])];
            generateSet(true);
        }
        
        // *F*ull image
        if (key == 'f') {
            limits = originalLimits;
            generateSet(true);
		}
        
        // *S*ave the current screen as an image, using the date, time, and c as the filename
        if (key == 's') {
            String filename = year() + "-" + month() + "-" + day() + "_" + hour() + ":" + minute() + ":" + second() + "_" + reC + "_" + imC + ".png";
            save(path + "/" + filename);
            println("Saved to " + path + "/" + filename);
        }
        
        println(drawX, drawY, scaleFactor);
    }
    
    void setC(float reC_, float imC_) {
		this.reC = reC_;
		this.imC = imC_;
		generateSet(false);
    }
    
    // Generates the julia set for the current value of c
    void generateSet(boolean resetView) {
        println("GENERATING JULIA");
    
        if (resetView) {
            drawX = 0;
            drawY = 0;
            scaleFactor = 1;
        }
    
        reRange = linspace(limits[0], limits[1], density);
        imRange = linspace(limits[2], limits[3], density);
        realIter = new float[density][density];
        imagIter = new float[density][density];
        numIters = new int[density][density];
    
        // Initalise realIter and imagIter with the corresponding complex number
        for (int i = 0; i < realIter.length; i++) {
            for (int j = 0; j < realIter[i].length; j++) {
                realIter[i][j] = reRange[j];
                imagIter[i][j] = imRange[i];
            }
        }
    
        ProcessIters[] threads = new ProcessIters[4];
        int numPerThread = int(density / threads.length);
        for (int i = 0; i < threads.length; i++) {
            threads[i] = new ProcessIters(iterations, i * numPerThread, (i + 1) * numPerThread, realIter, imagIter, reC, imC, numIters);
            threads[i].start();
        }
        
        for (ProcessIters pi: threads) {
            try {
                pi.join();
            } catch (InterruptedException e) {
                println("Something went wrong...");
            }
        }
    
        println("DONE");
    }
}
