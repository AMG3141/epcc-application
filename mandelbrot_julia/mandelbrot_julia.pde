int density = 1000;
int iterations = 255;

MandelbrotGenerator man;
JuliaGenerator jul;

void setup() {
	man = new MandelbrotGenerator(new float[] {-2, 1, -1.5, 1.5}, 4, sketchPath());
	jul = new JuliaGenerator(new float[] {-2, 2, -2, 2}, 4, sketchPath());
}

float[] linspace(float min, float max, int num) {
    float[] res = new float[num];
    float delta = (max - min) / num;
    for (int i = 0; i < num; i++)
        res[i] = min + i * delta;
    return res;
}

float[] f(float reZ, float imZ, float reC, float imC) {
    return new float[] {reZ * reZ - imZ * imZ + reC, 2 * reZ * imZ + imC};
}
