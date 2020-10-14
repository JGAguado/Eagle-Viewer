from pyeagle import pyeagle

schematic = pyeagle.open("./Test_Board/Test_board.sch")

for part in schematic:
    print(part)
