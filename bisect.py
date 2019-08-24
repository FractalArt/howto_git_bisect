import sys
import subprocess

def bisect():
    # First compile the program named 'test_program'
    cmd = ['g++', '-o', 'test_program', 'test_program.cpp']
    p = subprocess.run(cmd)
    # Then run the program and check whether it works correctly. If an error
    # occurs, a non-zero value is returned and 'subprocess.check_call' raises
    # an exception. If we catch this exception, we return its error code to the
    # system which lets git bisect know that an error occurred. If the exception
    # is not raised we just return 0 to the system.
    try:
        subprocess.check_call('./test_program')
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)

if __name__ == "__main__":
    bisect()
