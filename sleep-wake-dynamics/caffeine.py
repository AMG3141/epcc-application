import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

Q_max = {"m": 100 * 3600, "v": 100 * 3600}
theta = 10
sigma = 3
A = 1.3
A_0 = 1.3
vvm = -2.1 / 3600
vmv = -1.8 / 3600
vvc = -2.9        #coupling strength between sleep neurons
vvh = 1            #drive to sleep
vvh_0 = 1
chi = 45           #charachteristic timescale to the homeostatic drive
mu = 4.4 /3600
tau = 10 / 3600
omega = 2*np.pi / 24
c0 = 4.5
c1 = 0.23
c2 = 2.33

ka = 1e-3 * 3600
ke = 4.5e-5 * 3600
kappa = 200
bw = 60
gammaC = kappa / bw # in mg / kg
t0 = 1
zetaA = 0.1#0.023
zetaH = 0.1#0.005
#zetaA = 0.01

def C(t, c0, omega):
	return (c0 + np.cos(omega * t))

def Q(V, Q_max, theta, sigma, mOrV):
	return Q_max[mOrV] / (1 + np.exp(-1 * (V - theta) / sigma))

def Zc(t, gammaC, ke, ka, t0):
	return gammaC * (np.exp(-ke * (t - t0)) - np.exp(-ka * (t - t0)))

def DiffEq(t, V, C, Q_max, sigma, theta, omega, mu, c0, gammaC, ke, ka, t0, zetaA, zetaH, vvh, A):
	V_v, V_m, H = V
	if t >= t0:
		vvh = vvh_0 * (1 - zetaH * Zc(t, gammaC, ke, ka, t0))
		A = A_0 + (zetaA * Zc(t, gammaC, ke, ka, t0))

	D = vvc * C(t, c0, omega) + vvh * H
	V_vDot = (vvm * Q(V_m, Q_max, theta, sigma, "m") + D - V_v) / tau
	V_mDot = (A + vmv * Q(V_v, Q_max, theta, sigma, "v") - V_m) / tau
	Hdot = (mu * Q(V_m, Q_max, theta, sigma, "m") - H) / chi
	return [V_vDot, V_mDot, Hdot]

# Solve
def solveEq(gammaC = gammaC, ka = ka, ke = ke):
	t = np.linspace(0, 24, 1000)
	tSpan = [np.min(t), np.max(t)]
	V_0 = [-12, 0, 14] # Initial values for V_v, V_m, H
	res = solve_ivp(DiffEq, tSpan, V_0, args = (C, Q_max, sigma, theta, omega, mu, c0, gammaC, ke, ka, t0, zetaA, zetaH, vvh, A), dense_output = True)
	V = res.sol(t)
	D = vvc * C(t, c0, omega) + vvh * V[2]

	# S= c1*D + c2
	# plt.cla()
	# plt.plot(t,S)
	# plt.savefig("sleepy.png")

	return t, V, D