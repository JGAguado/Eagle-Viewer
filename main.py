"""
Eagle Viewer
-----------------
Script for reading Eagle's .brd files and plotting it into 2D/3D graphics.




Created by J.G.Aguado
December 2017
"""

import numpy as np
import math
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import xmltodict
import win32com.client


class Board():
    def __init__(self, path):
        super().__init__()
        self.read_brd(path)
        self.plot()
        # self.CATIA()

    def read_brd(self, path):
        with open(path) as fd:
            self.brd = xmltodict.parse(fd.read())
            self.brd = self.brd['eagle']['drawing']


    def plot(self):
        color_layers = [['c', 0.5],['b', 0.2]]
        lx = float(self.brd['board']['plain']['wire'][1]['@x1'])
        ly = float(self.brd['board']['plain']['wire'][1]['@y2'])
        scale = 1/3
        fig = plt.figure(figsize=(lx*scale, ly*scale))
        # axes = fig.add_subplot(111, facecolor=color_layers[1][0])
        self.axes = fig.add_subplot(111)
        for color in color_layers:
            for signal in self.brd['board']['signals']['signal']:
                if 'wire' in signal:
                    print(signal['@name'])
                    points = []
                    for wire in signal['wire']:
                        print(wire['@x1'], wire['@y1'], wire['@x2'], wire['@y2'])
                        points.append([float(wire['@x1']), float(wire['@y1'])])
                        points.append([float(wire['@x2']), float(wire['@y2'])])

                        x1, x2, y1, y2 = float(wire['@x1']), float(wire['@x2']), float(wire['@y1']), float(wire['@y2'])

                        self.axes.set_xlim(0, lx)
                        self.axes.set_ylim(0, ly)

                        self.draw_wire(x1, y1, x2, y2, color[0], color[1])
                        # axes.plot(x1, y1, marker='.', markersize=color[1], color=color[0], linewidth=color[1])
                    # if color == color_layers[0]:
                    #     self.uni_wire(points)

        plt.show()

    def draw_wire(self, x1, y1, x2, y2, color, linewidth):

        length = np.sqrt(((x2-x1)**2)+ ((y2-y1)**2))
        degrees = math.degrees(math.atan2(y2-y1, x2-x1))
        fancybox = FancyBboxPatch([x1, y1], linewidth, length, boxstyle=mpatches.BoxStyle("Round"), mutation_scale=0.2,
                                  mutation_aspect=1, color=color)
        t = mpl.transforms.Affine2D().rotate_deg(degrees)
        fancybox.set_transform(t)
        self.axes.add_patch(fancybox)

    def uni_wire(self, points):
        print('------------')
        no_dupes = [x for n, x in enumerate(points) if x not in points[:n]]
        print(no_dupes)

        dupes = [x for n, x in enumerate(points) if x in points[:n]]

        uni_dupes = [x for n, x in enumerate(no_dupes) if x not in dupes]
        print(uni_dupes)
        ii = 0
        for _ in uni_dupes[1:]:
            ii += 1
            loc = points.index(uni_dupes[0])
            uni_points =[]
            uni_points.append(uni_dupes[0])
            if loc%2 == 0:
                uni_points.append(points[loc+1])
                par = True
            else:
                uni_points.append(points[loc-1])
                par = False


            while uni_points[-1] != uni_dupes[ii]:
                if par:
                    loc = no_dupes.index(uni_points[-1])
                    if loc == 0:
                        loc = points.index(uni_points[-1], 1)
                        uni_points.append(points[loc + 1])

                    else:
                        uni_points.append(no_dupes[loc + 1])
                else:
                    loc = no_dupes.index(uni_points[-1])
                    if loc == 0:
                        loc = points.index(uni_points[-1], 1)
                        uni_points.append(points[loc - 1])
                    else:
                        uni_points.append(no_dupes[loc - 1])

            print(uni_points)

    def CATIA(self):
        cat = win32com.client.Dispatch("CATIA.Application")
        part1 = cat.Documents.Add("Part").Part
        ad = cat.ActiveDocument

        part1 = ad.Part

        bod = part1.MainBody
        bod.Name = "PCB"

        skts = bod.Sketches
        xyPlane = part1.CreateReferenceFromGeometry(part1.OriginElements.PlaneXY)
        xzPlane = part1.CreateReferenceFromGeometry(part1.OriginElements.PlaneZX)

        shapeFact = part1.Shapefactory
        hybridFact = part1.HybridShapeFactory







        for signal in self.brd['board']['signals']['signal']:
            ii = 0
            if 'wire' in signal:
                print(signal['@name'])
                for wire in signal['wire']:
                    ii += 1
                    signal_name = "Signal " + signal['@name']
                    x1, x2, y1, y2 = float(wire['@x1']), float(wire['@x2']), float(wire['@y1']), float(wire['@y2'])

                    ms = skts.Add(xyPlane)

                    fact = ms.OpenEdition()
                    fact.CreateLine(x1, y1, x2, y2)
                    ms.CloseEdition()
                    signal_name = "Sketch." + str(ii)
                    sketch1 = skts.Item(signal_name)

                    reference1 = part1.CreateReferenceFromObject(sketch1)

                    hybridShapePointOnCurve1 = hybridFact.AddNewPointOnCurveFromDistance(reference1, 0, False)
                    reference2 = part1.CreateReferenceFromObject(hybridShapePointOnCurve1)

                    hybridShapeDirection1 = hybridFact.AddNewDirectionByCoord(0, 0, 1)
                    hybridShapeLinePtDir1 = hybridFact.AddNewLinePtDir(reference2, hybridShapeDirection1, 0, 0.1, False)
                    bod.InsertHybridShape(hybridShapeLinePtDir1)
                    part1.InWorkObject = hybridShapeLinePtDir1

                    # rib1 = shapeFact.AddNewRibFromRef(None, None)
                    # reference2 = part1.CreateReferenceFromObject(hybridShapeLinePtDir1)
                    # rib1.SetProfileElement(reference1)
                    # rib1.CenterCurveElement = reference2
                    # rib1.IsThin = True
                    # parameters1 = part1.Parameters
                    # item_thin = "Part1\PCB\Rib." + str(ii) + "\ThickThin1"
                    # length1 = parameters1.Item(item_thin)
                    # length1.Value = 0.5
                    part1.Update
if __name__ == '__main__':
    path = r'.\Test_Board\Test_board.brd'
    Test0 = Board(path)
