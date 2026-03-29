import numpy as np
import sys


RELATIVE_LAUNCH_POINT = np.array([18.0, 17.75, 0.865])
# Drag coefficient per tick.
DRAG = np.float32(0.99) # This comes to be 0.9900000095367432 
d = DRAG
GRAVITY = 0.03  # Gravity per tick.
g = GRAVITY
X, Y, Z = 0, 1, 2  # Indexes to improve readability when accessing np arrays
# Base launch vectors for the four cardinal directions.
DIRECTIONS = {
    "north":   {"name": "north", "vector":      np.array([0.15889793171230157, 0, -0.8773928676974515]), "bit": 1},
    "south":   {"name": "south", "vector":      np.array([0.2577611051239664, 0, 0.8405252517166506]), "bit": 0},
    "west":    {"name": "west", "vector":       np.array([-0.7990852942457304, 0, -0.3995426547435254]), "bit": 1},
    "east":    {"name": "east", "vector":       np.array([0.8022091152196946, 0, -0.39323978471691357]), "bit": 0},
    "initial": {"name": "initial", "vector":    np.array([-0.2651525076935224, -0.45633449169280826,-0.21949711207872816])},
}


def calculate_necessary_tnts(canon_origin, target_position):
    origin = np.array(canon_origin) + RELATIVE_LAUNCH_POINT
    target = np.array(target_position)

    # Horizontal displacement from cannon to target.
    displacement = target - origin

    t = ticks_until_fall(displacement[Y])
    v0 = velocity_given_displacement(displacement, t)
    tnts, dir_x, dir_z, reached_v = v_to_tnts(v0)

    return tnts, dir_x, dir_z, t, reached_v


def velocity_given_displacement(displacement, t):
    """
    Compute the initial horizontal velocity needed to travel a given displacement
    in t ticks.

    In ThrowableProjectile.tick(), Minecraft applies:
        1. gravity
        2. drag
        3. movement

    Horizontally there is no gravity, so each tick the projectile moves by the
    updated velocity:
        v_1 = d*v_0
        v_2 = d^2*v_0
        ...
        v_t = d^t*v_0

    Therefore the total displacement after t ticks is:
        x(t) = v_0 * (d + d^2 + ... + d^t)
             = v_0 * d * (1 - d^t) / (1 - d)

    Solving for v_0 gives the formula below.
    """
    return displacement * (1 - d) / (d * (1 - d**t))


def displacement_given_velocity(v, t):
    """
    Compute the displacement after t ticks given an initial horizontal velocity.

    In ThrowableProjectile.tick(), Minecraft applies drag before movement, so
    the projectile moves by:
        d*v_0, d^2*v_0, ..., d^t*v_0

    Summing that geometric series gives:
        x(t) = v_0 * d * (1 - d^t) / (1 - d)
    """
    return v * d * (1 - d**t) / (1 - d)


def cross2(a, b):
    return a[0] * b[1] - a[1] * b[0]


def v_to_tnts(v):
    """
    Decompose a desired 3D velocity vector into TNT counts using the cannon's
    non-orthogonal horizontal basis vectors, which represent the motion applied
    by TNT from each direction.

    Since the available direction vectors are not perfectly axis-aligned or
    symmetric, the sign of the target velocity alone is not sufficient to
    determine which basis to use. Instead, all valid pairs of cardinal
    directions are tested.

    For each candidate pair:
        1. A 2x2 basis matrix is built from their XZ components.
        2. The linear system B * w = v_xz is solved to obtain TNT amounts.
        3. The amounts are rounded to integers (no half-TNTs).
        4. Negative solutions are discarded (no pulling-TNTs).
        5. The resulting velocity is compared to the target.

    The valid solution with the smallest reconstruction error is selected.

    Parameters
    ----------
    v : np.ndarray
        A 3D velocity vector [vx, vy, vz].

    Returns
    -------
    tnt_counts : np.ndarray
        Integer TNT counts for the two selected directions.
    dir_x : dict
        Direction dictionary for the first basis vector.
    dir_z : dict
        Direction dictionary for the second basis vector.

    Raises
    ------
    ValueError
        If no valid nonnegative TNT combination can be found.
    """

    # We only care about the horizontal velocity, so keep the XZ components.
    h_v = v[[X, Z]]

    initial = DIRECTIONS["initial"]["vector"][[X, Z]]
    east = DIRECTIONS["east"]["vector"][[X, Z]]
    south = DIRECTIONS["south"]["vector"][[X, Z]]
    west = DIRECTIONS["west"]["vector"][[X, Z]]
    north = DIRECTIONS["north"]["vector"][[X, Z]]

    # Determine which direction vectors to use.
    # Specifically, we are trying to get between
    # what vectors it is by using the cross product.
    # If its angle is between east and south, take east and south
    if cross2(east, h_v) >= 0 and cross2(h_v, south) >= 0:
        dir_x = DIRECTIONS["east"]
        dir_z = DIRECTIONS["south"]

    elif cross2(south, h_v) >= 0 and cross2(h_v, west) >= 0:
        dir_x = DIRECTIONS["west"]
        dir_z = DIRECTIONS["south"]

    elif cross2(west, h_v) >= 0 and cross2(h_v, north) >= 0:
        dir_x = DIRECTIONS["west"]
        dir_z = DIRECTIONS["north"]

    elif cross2(north, h_v) >= 0 and cross2(h_v, east) >= 0:
        dir_x = DIRECTIONS["east"]
        dir_z = DIRECTIONS["north"]

    else:
        raise ValueError("Velocity does not lie in any expected cone")

    # Build the 2x2 basis matrix from the XZ components of the chosen
    # direction vectors.
    basis_matrix = np.column_stack((
        dir_x["vector"][[X, Z]],
        dir_z["vector"][[X, Z]],
    ))

    # Solve basis_matrix * coeffs = horizontal_velocity
    # to get the TNT amounts in this basis and then round
    raw_coeffs = np.linalg.solve(basis_matrix, h_v-initial)
    tnt_counts = np.rint(raw_coeffs).astype(int)
    reached_v = basis_matrix @ tnt_counts+initial

    return tnt_counts, dir_x, dir_z, reached_v


def ticks_until_fall(dy):
    # We want the smallest integer t such that y_at_tick(t) <= dy.
    # Since y_at_tick(t) is monotonically decreasing, binary search is
    # simpler and more practical here than using the exact closed-form
    # inverse involving Lambert W.
    if dy > 0:
        raise ValueError("dy must be <= 0, since falling is negative Y displacement")

    lo = 0
    hi = 1

    # Find an upper bound where we have already fallen far enough.
    while y_at_tick(hi) > dy:
        lo = hi
        hi *= 2

    # Binary search for the last tick where y_at_tick(t) > dy.
    while lo + 1 < hi:
        mid = (lo + hi) // 2  # Integer division because we want an integer amount of ticks
        if y_at_tick(mid) > dy:
            lo = mid
        else:
            hi = mid

    return lo


def y_at_tick(t):
    """
    Compute vertical displacement after t ticks for ThrowableProjectile motion.

    Minecraft applies:
        1. gravity
        2. drag
        3. movement

    So the vertical recurrence is:
        v_{t+1} = d*v_t - d*g
        y_{t+1} = y_t + v_{t+1}

    with initial conditions:
        v_0 = v_0y
        y_0 = 0

    This can be simplified to the following formula.
    """
    v_0y = DIRECTIONS["initial"]["vector"][Y]
    return (v_0y + d * g / (1 - d)) * (d * (1 - d**t) / (1 - d)) - (d * g / (1 - d)) * t


def tnt_to_binary(tnt_vector, dir_x, dir_z):
    # The machine expects
    # (direction_bit & x_10 & 1_9 & x_50)
    # where & represents concatenation,
    # x_10 will be multiplied by 10,
    # 1_9 is an amount between 1 and 9
    # x_50 will be multiplied by 50

    if tnt_vector[0] > 3199 or tnt_vector[1] > 3199:
        raise ValueError(f"You need too many tnts: {tnt_vector} for the memory of max 3199.")

    # As a constraint of the cannon, at least some direction signal has to be sent.
    # If a TNT count is 0, force the corresponding direction bit to 1 by selecting
    # a harmless fallback direction that should not otherwise affect the result.
    if tnt_vector[0] == 0:
        dir_x = DIRECTIONS["west"]
    if tnt_vector[1] == 0:
        dir_z = DIRECTIONS["north"]

    binary_x = str(dir_x["bit"])
    binary_x += " " + format((tnt_vector[0] % 50//10), "03b")
    binary_x += " " + format(tnt_vector[0] % 10, "04b")[::-1]
    binary_x += " " + format(tnt_vector[0]//50, "06b")

    binary_z = str(dir_z["bit"])
    binary_z += " " + format((tnt_vector[1] % 50//10), "03b")
    binary_z += " " + format(tnt_vector[1] % 10, "04b")[::-1]
    binary_z += " " + format(tnt_vector[1]//50, "06b")

    return binary_x, binary_z


def target_to_binary(cannon: tuple[int, int, int], target: tuple[int, int, int]):
    tnts, dir_x, dir_z, _, _ = calculate_necessary_tnts(cannon, target)
    return tnt_to_binary(tnts, dir_x, dir_z)


if __name__ == "__main__":
    if len(sys.argv) >= 7:
        canon_x, canon_y, canon_z, target_x, target_y, target_z = map(float, sys.argv[1:7])
        tnts, dir_x, dir_z, t, reached_v = calculate_necessary_tnts((canon_x, canon_y, canon_z), (target_x, target_y, target_z))
        b_x, b_z = tnt_to_binary(tnts, dir_x, dir_z)

        print("")
        print(f"Achieved velocity: {reached_v}")
        print(f"Only Z: {dir_z["vector"]*tnts[1]}")
        print(f"Only X: {dir_x["vector"]*tnts[0]}")
        print(f"You'll arrive at {displacement_given_velocity(reached_v, t)+np.array((canon_x, canon_z))}")

        print(f"\nWe need")
        print(f"{tnts[1]} tnts in the z direction.")
        print(f"{tnts[0]} tnts in the x direction and")
        print(f"For the directions {dir_x['name']} and {dir_z['name']}, respectively.")
        print(f"\nBinary string Z ( up ): {b_z}")
        print(f"Binary string X (down): {b_x}\n")

        print(f"time in ticks is {t}\n")

    else:
        print(
            "Expected 2 arguments: the coords for the cannon origin "
            "(where you placed the schematic) and the coords for the target.\n"
            "Usage: python script.py x0 y0 z0 xt yt zt\n"
            "Example: python script.py 0 64 0 10 70 -5\n"
        )
