import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import math

# Constants
m = 22.5  # estimated mass (kg)
t = 3.6   # estimated burn time (s)
g = 9.8   # gravitational acceleration (m/s^2)
cd = 0.4  # drag coefficient
D = 11    # max rocket diameter (cm)
md = 17.5 # estimated rocket mass without grains (kg)

# Drag influence table
N_values = [0.0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
Fz_values = [1.0, 0.82, 0.7, 0.62, 0.56, 0.52, 0.48, 0.44, 0.4, 0.38, 0.38]

# Linear interpolation function
itp = interp1d(N_values, Fz_values, kind='linear', fill_value='extrapolate')

def interpolate_Fz(N):
    return float(itp(N))  # Convert numpy scalar to float

# Altitude at burnout
def burnout(F, m, g, t):
    z1 = 0.5 * ((F / m) - g) * t**2
    return z1

# Maximum altitude (apogee)
def apogee(F, z1, m, g):
    z2 = (F * z1) / (m * g)
    return z2

# Main simulation function
def thrust_generator():
    N_plots = []
    Fz_plots = []

    for F in range(0, 3501, 25):
        z1 = burnout(F, m, g, t)
        z2 = apogee(F, z1, m, g)
        try:
            v1 = math.sqrt(((2 * z1) / m) * (F - m * g))
        except ValueError:
            v1 = 0  # Avoid sqrt of negative in early iterations

        N = (cd * D**2 * v1**2) / (1000 * md)
        Fz = interpolate_Fz(N)
        z2_actual = Fz * z2

        print(f"Iteration {F//25}")
        print(f"Thrust: {F} N")
        print(f"Altitude at burnout: {z1:.2f} m")
        print(f"Maximum altitude (apogee): {z2_actual:.2f} m")
        print(f"Velocity at burnout v1: {v1:.2f} m/s")
        print(f"Drag influence number N: {N:.2f}")
        print("\n")

        N_plots.append(N)
        Fz_plots.append(Fz)

    # Plot N vs Fz
    plt.plot(N_plots, Fz_plots, marker='o')
    plt.xlabel("Drag Influence Number (N)")
    plt.ylabel("Drag Loss Factor (Fz)")
    plt.title("Drag Correction vs Drag Influence Number")
    plt.grid(True)
    plt.show()

# Run the simulation
thrust_generator()
