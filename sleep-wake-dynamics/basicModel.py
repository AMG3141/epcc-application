import numpy as np
from scipy.integrate import solve_ivp

Dbar = 0.77
DA = 0.42
Q_max = 100 * 3600
theta = 10
sigma = 3
vmaQ = 1
vvm = -1.9 / 3600
vmv = -1.9 / 3600
vvc = -6.3          #coupling strength between sleep neurons
vvh = 0.19             #drive to sleep
chi = 10.8            #charachteristic timescale to the homeostatic drive
mu = 0.001
tau_m = 10 / 3600
tau_v = 10 / 3600
omega = 2*np.pi / 24

def Dt(t, omega):
	return DA * np.cos(omega * t) + Dbar

def Q(V, Q_max, theta, sigma):
	return Q_max / (1 + np.exp(-1 * (V - theta) / sigma))

def DiffEq(t, V, Dt, Q_max, sigma, theta, omega, mu):
	V_v, V_m, H = V
	V_vDot = (vvm * Q(V_m, Q_max, theta, sigma) + Dt(t, omega) - V_v) / tau_v
	V_mDot = (vmaQ + vmv * Q(V_v, Q_max, theta, sigma) - V_m) / tau_m
	Hdot = (mu * Q(V_m, Q_max, theta, sigma) - H) / chi
	return [V_vDot, V_mDot, Hdot]

# Solve
def solveEq():
	t = np.linspace(0, 72, 1000)
	tSpan = [np.min(t), np.max(t)]
	V_0 = [0.1, -6.1, 10] # Initial values for V_v, V_m, H
	# V_0 = [-6.1, 0.1, 10]
	res = solve_ivp(DiffEq, tSpan, V_0, args = (Dt, Q_max, sigma, theta, omega, mu), rtol = 1e-8, atol = 1e-8, dense_output = True)
	V = res.sol(t)
	return t, V, Dt(t, omega) # Third return value just to line up with the others