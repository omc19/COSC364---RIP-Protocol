"""
    COSC364 Assignment 2
    Written by:
    Bradley Jackson: 69599455
    Oscar McLaren: 86998334
    Date: 27/05/2019
"""

import subprocess
import time

# Globals
x = 0
y = 0
z = 0
n = 2 # number of paths for splittable flow

def minimize():
    # First three line of the LP file
    lp_string = "Minimize\n  r\nSubject to\n"
    return lp_string


def demand_volume():
    # The demand volume from source i to destination j through j
    lp_string = ""

    for i in range(1, x+1):
        for j in range(1, z+1):
            for k in range(1, y+1):
                if k == 1:
                    lp_string += "  DemandVolume{0}{2}: x{0}{1}{2}".format(i, k, j)
                else:
                    lp_string += " + x{0}{1}{2}".format(i, k, j)

            h = 2 * i + j
            lp_string += " = {}\n".format(h)

    return lp_string


def demand_flow():
    # Load balancing
    lp_string = ""

    for i in range(1, x+1):
        for j in range(1, z+1):
            for k in range(1, y+1):
                h = 2 * i + j
                lp_string += "  DemandFlow{0}{1}{2}: {4} x{0}{1}{2} - {3} u{0}{1}{2} = 0\n".format(i, k, j, h, n)

    return lp_string


def source_capacity():
    # Capacity of source-transit link
    lp_string = ""

    for i in range(1, x+1):
        for k in range(1, y + 1):
            for j in range(1, z+1):

                if j == 1:
                    lp_string += "  SourceCapacity{0}{1}: x{0}{1}{2}".format(i, k, j)
                elif j == z:
                    lp_string += " + x{0}{1}{2} - c{0}{1} <= 0\n".format(i, k, j)
                else:
                    lp_string += " + x{0}{1}{2}".format(i, k, j)

    return lp_string


def destination_capacity():
    # Capacity of transit-destination link
    lp_string = ""

    for k in range(1, y+1):
        for j in range(1, z+1):
            for i in range(1, x+1):

                if i == 1:
                    lp_string += "  DestinationCapacity{1}{2}: x{0}{1}{2}".format(i, k, j)
                elif i == x:
                    lp_string += " + x{0}{1}{2} - d{1}{2} <= 0\n".format(i, k, j)
                else:
                    lp_string += " + x{0}{1}{2}".format(i, k, j)

    return lp_string


def transit_capacity():
    # Capacity of the transit node itself from all sources EDIT: actually the load on the transit node
    lp_string = ""

    for k in range(1, y+1):
        for j in range(1, z+1):
            for i in range(1, x+1):

                if i == 1 and j == 1:
                    lp_string += "  TransitCapacity{1}: x{0}{1}{2}".format(i, k, j)
                elif i == x and j == z:
                    lp_string += " + x{0}{1}{2} - r <= 0\n".format(i, k, j)
                else:
                    lp_string += " + x{0}{1}{2}".format(i, k, j)

    return lp_string


def binary_variable():
    # Binary variable for load balancing
    lp_string = ""

    for i in range(1, x+1):
        for j in range(1, z+1):
            for k in range(1, y+1):
                if k == 1:
                    lp_string += "  BinaryVariable{0}{2}: u{0}{1}{2}".format(i, k, j)
                else:
                    lp_string += " + u{0}{1}{2}".format(i, k, j)
            lp_string += " = {}\n".format(n)

    return lp_string


def bounds():
    # Bounds for r and all x, c and d variables
    lp_string = "Bounds\n"
    lp_string += "  0 =< r\n"

    for i in range(1, x+1):
        for k in range(1, y+1):
            for j in range(1, z+1):
                lp_string += "  0 <= x{0}{1}{2}\n".format(i, k, j)
    # non-negativity constraint for every capacity from source to transit
    for i in range(1, x+1):
        for k in range(1, y+1):
            lp_string += "  0 <= c{0}{1}\n".format(i, k)
    # non-negativity constraint for every capacity from transit to destination
    for k in range(1, y+1):
        for j in range(1, z+1):
            lp_string += "  0 <= d{0}{1}\n".format(k, j)

    return lp_string


def binaries():

    lp_string = "Binaries\n"

    for i in range(1, x+1):
        for k in range(1, y+1):
            for j in range(1, z+1):
                lp_string += "  u{0}{1}{2}\n".format(i, k, j)

    return lp_string


def build_lp_file():
    # Build the LP string and writes it to a file
    lp_file = minimize()
    lp_file += demand_volume()
    lp_file += binary_variable()
    lp_file += demand_flow()
    lp_file += source_capacity()
    lp_file += destination_capacity()
    lp_file += transit_capacity()
    lp_file += bounds()
    lp_file += binaries()
    lp_file += "End"

    f = open("tm.lp", "w+")
    f.write(lp_file)
    f.close()


def collect_inputs():
    # Collects the number of nodes
    global x
    global y
    global z
    x = int(input("Number of Source Nodes: "))
    y = int(input("Number of Transit Nodes: "))
    z = int(input("Number of Destination Nodes: "))


def cplex():
    # Executes CPLEX for the LP file
    subprocess.call(["cplex", "-c", "read tm.lp", "optimize", "display solution variables -"])


def main():

    collect_inputs()
    build_lp_file()
    start = time.time()
    cplex()
    stop = time.time()
    print("exit")
    print(stop-start)

main()