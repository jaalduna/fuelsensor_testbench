from Bootloader import Bootloader
import sys
if len(sys.argv) == 4:
    b = Bootloader(str(sys.argv[1]), int(sys.argv[2]))
else:
    b = Bootloader()
b.read_version()
b.connect()
if len(sys.argv) > 3:
    b.program_file(str(sys.argv[3]))
else:
    b.program_file('./firmware/aiko1.X.production.hex')
    
b.close_socket()
b.connect()
b.jump_to_app()
b.close_socket()
