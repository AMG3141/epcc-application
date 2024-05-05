import numpy as np
from scipy.integrate import solve_ivp

Q_max = 100 * 3600
theta = 10
sigma = 3
A = 1.3
vvm = -2.1 / 3600
vmv = -1.8 / 3600
vvc = -2.9        #coupling strength between sleep neurons
vvh = 1            #drive to sleep
chi = 45           #charachteristic timescale to the homeostatic drive
mu = 4.4 /3600
tau = 10 / 3600
omega = 2*np.pi / 24
c0 = 4.5

def C(t, c0, omega):
	return (c0 + np.cos(omega * t))

def Q(V, Q_max, theta, sigma):
	return Q_max / (1 + np.exp(-1 * (V - theta) / sigma))

def DiffEq(t, V, C, Q_max, sigma, theta, omega, mu, c0):
	V_v, V_m, H = V
	D = vvc * C(t, c0, omega) + vvh * H
	V_vDot = (vvm * Q(V_m, Q_max, theta, sigma) + D - V_v) / tau
	V_mDot = (A + vmv * Q(V_v, Q_max, theta, sigma) - V_m) / tau
	Hdot = (mu * Q(V_m, Q_max, theta, sigma) - H) / chi
	return [V_vDot, V_mDot, Hdot]

# Solve
def solveEq():
	t = np.linspace(0, 72, 1000)
	tSpan = [np.min(t), np.max(t)]
	V_0 = [-12, 0, 14] # Initial values for V_v, V_m, H
	res = solve_ivp(DiffEq, tSpan, V_0, args = (C, Q_max, sigma, theta, omega, mu, c0), dense_output = True)
	V = res.sol(t)
	D = vvc * C(t, c0, omega) + vvh * V[2]
	return t, V, D