from tkinter import *

def main():
    root = Tk()
    padding = 10
    frame = Frame(root)
    frame.pack()

    message = Label(frame, text="Enter your cube stickers below, then click Solve.")
    message.pack(padx=100, pady=padding)

    entry = Entry(root, width=100)
    entry.pack(padx=20, pady=padding)

    button = Button(root, text="Solve")
    button.pack(pady=padding)

    solve_label = Label(root, relief=SUNKEN, width=50)
    solve_label.pack(pady=padding)

    root.mainloop()


main()
