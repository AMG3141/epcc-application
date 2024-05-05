import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp

varyKappa = True # This variable is used to control whether we perform parametric analysis on kappa or the elimination/absorption rates

# Get the solution for the chosen equation
choice = input("Basic/advanced/caffeine: ")
if choice.lower() == "basic" or choice.lower() == "b":
    choice = "b"
    from basicModel import *
    dir = "/basicModel/"
elif choice.lower() == "advanced" or choice.lower() == "a":
    choice = "a"
    from advancedModel import *
    dir = "/4eqModel/"
elif choice.lower() == "caffeine" or choice.lower() == "c":
    oldStartTime = 6.846846846846847 # This is the first bed-time for the advanced model
    oldStartTimes = {1: 8.624624624624625, 6: 10.73873873873874} # These are the first bed-times for the normal caffeine parameters
    if varyKappa:  data = {"kappa": [], "startSleep": [], "endSleep": []}
    else: data = {"mult": [], "startSleep": [], "endSleep": []}

    choice = "c"

    from caffeine import *

    fig, axs = plt.subplots(3, 1, figsize = (10, 15))
    if varyKappa: values = [0, 50, 100, 150, 200, 250, 300, 350, 400]
    else: values = [1.2, 1.1, 1, 0.9, 0.8]
    for val in values:
        if not varyKappa: kaVary, keVary = val * ka, val * ke

        # Solve the equation for the various values
        if varyKappa: t, V, D = solveEq(val / bw)
        else: t, V, D = solveEq(ka = kaVary, ke = keVary)

        V_v, V_m, H = V

        # Model variables vs time
        if varyKappa:
            axs[0].plot(t, V_v, label = f"$\kappa={val}\ mg$")
            axs[1].plot(t, V_m, label = f"$\kappa={val}\ mg$")
            axs[2].plot(t, H, label = f"$\kappa={val}\ mg$")
        else:
            axs[0].plot(t, V_v, label = f"$k_a={round(kaVary / 3600, 4)} " + "\ s^{-1}" + f",\ k_e={round(keVary / 3600, 9)} ".replace("e-05", r"\times10^{-5}") + "\ s^{-1}$")
            axs[1].plot(t, V_m, label = f"$k_a={round(kaVary / 3600, 4)} " + "\ s^{-1}" + f",\ k_e={round(keVary / 3600, 9)} ".replace("e-05", r"\times10^{-5}") + "\ s^{-1}$")
            axs[2].plot(t, H, label = f"$k_a={round(kaVary / 3600, 4)} " + "\ s^{-1}" + f",\ k_e={round(keVary / 3600, 9)} ".replace("e-05", r"\times10^{-5}") + "\ s^{-1}$")

        # Find the start and end sleep times
        if varyKappa:
            data["kappa"].append(val)
        else:
            data["mult"].append(kaVary / ka)

        data["startSleep"].append(t[V_v > V_m][0])
        data["endSleep"].append(t[np.where(V_v > V_m)[0][-1] + 1])

    # Configure plots
    axs[0].axvline(oldStartTimes[t0], color = "k", linestyle =  "--", label = "Old bedtime")
    axs[0].set_xlabel("Time (hr)")
    axs[0].set_ylabel("$V_v\ (mV)$")

    axs[1].axvline(oldStartTimes[t0], color = "k", linestyle =  "--", label = "Old bedtime")
    axs[1].set_xlabel("Time (hr)")
    axs[1].set_ylabel("$V_m\ (mV)$")
    axs[1].legend()

    axs[2].axvline(oldStartTimes[t0], color = "k", linestyle =  "--", label = "Old bedtime")
    axs[2].set_xlabel("Time (hr)")
    axs[2].set_ylabel("$H\ (nM) $")

    if varyKappa: dir = "/caffeine/" + "t0-6_varyKappa"
    else: dir = "/caffeine/" + "t0-1_varyKaKe"
    plt.savefig(f"images{dir}V_t.png", dpi = 400, bbox_inches = "tight")

    # Plot difference in start time and length of sleep against varied parameter
    plt.clf()
    fig, ax = plt.subplots(2, 1, figsize = (5, 10))
    if varyKappa:
        ax[0].plot(data["kappa"], np.array(data["startSleep"]) - oldStartTime, "o-")
        ax[1].plot(data["kappa"], np.array(data["endSleep"]) - np.array(data["startSleep"]), "-o")
    else:
        ax[0].plot(data["mult"], np.array(data["startSleep"]) - oldStartTimes[t0], "o-")
        ax[1].plot(data["mult"], np.array(data["endSleep"]) - np.array(data["startSleep"]), "-o")

    if varyKappa:
        ax[0].set_xlabel("$\kappa\ (mg)$")
    else:
        ax[0].set_xlabel("Multiplier")
        ax[0].set_ylabel("Difference in start time of sleep (hours)")

    if varyKappa:
        ax[1].set_xlabel("$\kappa\ (mg)$")
    else:
        ax[1].set_xlabel("Multiplier")
        ax[1].set_ylabel("Length of sleep (hours)")

    fig.savefig(f"images{dir}_timesAndLengths.png", dpi = 400, bbox_inches = "tight")

    dir = "/caffeine/" + "t0-1_kappa200_bw60"
else:
    exit()

# Plot
t, V, D = solveEq()
V_v, V_m, H = V

# Model variables vs time
plt.figure(figsize = (10, 15))
plt.subplot(311)
plt.plot(t, V_v)
plt.fill_between(t, min(V_v), max(V_v), where = V_v > V_m, label = "Sleep", alpha = 0.3)
plt.fill_between(t, min(V_v), max(V_v), where = V_v < V_m, label = "Awake", alpha = 0.3)
if choice == "c": plt.axvline(6.846846846846847, color = "k", linestyle = "--", label = "Old bedtime")
plt.xlabel("Time (hr)")
plt.ylabel("$V_v\ (mV)$")
plt.legend()

plt.subplot(312)
plt.plot(t, V_m)
plt.fill_between(t, min(V_m), max(V_m), where = V_v > V_m, label = "Sleep", alpha = 0.3)
plt.fill_between(t, min(V_m), max(V_m), where = V_v < V_m, label = "Awake", alpha = 0.3)
if choice == "c": plt.axvline(6.846846846846847, color = "k", linestyle = "--", label = "Old bedtime")
plt.xlabel("Time (hr)")
plt.ylabel("$V_m\ (mV)$")
plt.legend()

plt.subplot(313)
plt.plot(t, H)
plt.fill_between(t, min(H), max(H), where = V_v > V_m, label = "Sleep", alpha = 0.3)
plt.fill_between(t, min(H), max(H), where = V_v < V_m, label = "Awake", alpha = 0.3)
if choice == "c": plt.axvline(6.846846846846847, color = "k", linestyle = "--", label = "Old bedtime")
plt.xlabel("Time (hr)")
plt.ylabel("$H\ (nM) $")
plt.legend()

plt.savefig(f"images{dir}V_t.png", dpi = 400, bbox_inches = "tight")

# V's against D
plt.figure(figsize = (8, 8))
plt.plot(D, V_v, ">--", label = "$V_v$", markevery = np.arange(0, len(D), 100))
plt.plot(D, V_m, ">--", label = "$V_m$", markevery = np.arange(0, len(D), 100))
if choice.lower() == "a":
    plt.text(-1, -3, "wake")
    plt.text(1.9, -3, "bistable", horizontalalignment = "center")
    plt.text(3, -3, "sleep")
plt.legend()
plt.xlabel("$D\ (mV) $")
plt.ylabel("$V\ (mV) $")
plt.savefig(f"images{dir}V_D.png", dpi = 400, bbox_inches = "tight")

if choice.lower() == "c":
    plt.cla()
    plt.figure(figsize = (10, 5))

    Z = Zc(t, gammaC, ke, ka, t0)
    Z[t < t0] = 0

    plt.plot(t, Z)
    plt.xlabel("Time (hr)")
    plt.ylabel("$Z_c(t)\ mg/kg$")
    plt.savefig("images/caffeine/z.png", bbox_inches = "tight")

# Get sleep and wake times
x = V_v > V_m
times = []
for i in range(len(x)):
    if i == len(x) - 1:
        continue
    if x[i] != x[i + 1]:
        times.append(t[i])
print(times)