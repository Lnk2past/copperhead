import os
import copperhead as cpp


this_dir = os.path.dirname(__file__)
source_file = os.path.join(this_dir, 'hello_world.cpp')
hello_world = cpp.generate('hello_world', 'void()')
hello_world()
