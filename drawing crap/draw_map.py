from graphics import Point, Line, GraphWin, Text
from math import sin, cos, radians

def vect(point, theta):
    length = .00005
    x = point.x + (length * cos(theta))
    y = point.y + (length * sin(theta))

    return Point(x, y)

def main():
    win = GraphWin("map", 1000, 800)
    win.setCoords(-88.357, 41.786, -88.355, 41.788)

    with open("2016-08-04_20-20-41.000.txt", "r") as log:
        lines = log.readlines()
        for n in range(0, len(lines) - 1, 3):
            line = lines[n].split(", ")
            if len(line) == 6:
                p = Point(float(line[2]), float(line[1]))
                p.setFill('red')
                Line(p, vect(p, radians(-(float(line[3]) + 270)))).draw(win)
                p.draw(win)

            else:
                Text(Point(float(lines[n+1].split(", ")[2]) + .00005, float(lines[n+1].split(", ")[1]) + .00005), line[0]).draw(win)
                print(line)

main()
