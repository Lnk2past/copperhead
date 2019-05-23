import os
import copperhead as cpp


this_dir = os.path.dirname(__file__)
source_file = os.path.join(this_dir, 'file_imports', 'hello_world.cpp')
hello_world = cpp.generate('hello_world', 'void()', block_file=source_file)
hello_world()
