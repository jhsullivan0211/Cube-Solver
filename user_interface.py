from tkinter import *
from cube_logic import *


def main():
    root = Tk()
    padding = 10
    frame = Frame(root)
    frame.pack()

    entry = Entry(root, width=60)
    solve_label = Label(root, relief=SUNKEN, width=50)
    button = Button(root, text="Solve", command=lambda: solve(entry.get(), solve_label))

    entry.pack(padx=20, pady=padding)
    button.pack(pady=padding)
    solve_label.pack(pady=padding)

    root.mainloop()


def solve(colors, label):
    print(colors)
    cube = CubeBuilder.get_cube_from_colors(colors)
    solution = Solver.get_solution(cube, Cube.new_cube())
    label['text'] = solution


main()

