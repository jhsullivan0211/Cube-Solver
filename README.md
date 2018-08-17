# Cube-Solver
A 2x2x2 Rubik's Cube solver, which solves the cube in the shortest number of moves possible.  

This project was intended to practice Python, as well as to try solving an interesting problem.  

### Getting Started

Running this program requires at least Python 3.3 or higher.  Additionally, it requires the graphics library Panda3D, which can be downloaded at https://www.panda3d.org/download.php?runtime, or by using the pip command: 
*$ pip install panda3d*.  After installing Panda3D, download the two modules in this repository and 
run user_interface.py.  

### Instructions

After following the above instructions, a window should pop up with a blank cube.  Select a color from the selection on the left,
then click a sticker to change it to that color.  To rotate the cube, simply left-click anywhere not on the cube and drag the 
mouse.  Color all of the stickers of the cube until it is completely colored, then click "Solve".  The cube will orient itself 
in the way that you should hold it to solve it, and the solution will be shown at the bottom of the window.  Note, the letters
correspond to the faces of the cube, which will be labeled after you click solve.  Uppercase letters indicate a clockwise turn,
while lowercase letters indicate a counter-clockwise turn of the face indicated by the letter.  For example, a solution "F, L, u"
means that you should rotate the Front face clockwise, then the Left face clockwise, followed by the Up face counter-clockwise.
If the cube you have built is impossible to solve, the solution will indicate that as well.  If this occurs, try double-checking
the stickering, as it is easy to make a mistake when coloring the cube.


