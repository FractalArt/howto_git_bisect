How To Git Bisect
=================

In this repository I store a simple example on how to use git bisect
to find a commit introducing a bug by making use of a python script.

***

The Python script
------------------

Let us first take a look at the python script that the *git bisect* command
will be running on a series of commits to find the first commit for which the
script returns a non-zero value, indicating that an error has occurred. This
way the commit introducing faulty behavior can be identified.  
The code of the script is as such:

```python
import sys
import subprocess

def bisect():
    # First compile the program named 'test_program'
    cmd = ['g++', '-o', 'test_program', 'test_program.cpp']
    subprocess.run(cmd)
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
```

The content of the script should be clear from the comments. The function
*bisect* is defined which, when called, first compiles our program and then
runs it. If the program does not return 0, i.e. an error occurred, its error
code is propagated to the system, else 0 is returned to the system.

The C++ test program
--------------------

Now it is time to write our first version of the program `test_program` which
is saved in *test_program.cpp*:

```C++
int main() {
    return 0;
}
```

This is very minimal. We can now run the python script and see that nothing
happens.

```
$ python bisect.py
```

Nothing seems to happen for this code. But if we run

```
$ echo $?
0
```

we see '0', the expected return value. To be more confident, just change the
return value in *test_program.cpp* from 0 to 7 and rerun:

```
$ python bisect.py
$ echo  $?
7
```

From now on, we will make a few changes to the code and commit them. At some
point we will deliberately change the return value from 0 to a non-zero value
and use *git bisect* to find the commit in which this happens. So let's
change the return value back to zero and add the first version to the repo.

```
$ git add test_program.cpp
$ git commit -m "Version 1 of the test program."
```

Next, we add some output to the program:

```C++
#include <iostream>
using namespace std;

int main() {
    cout << "\nA nice test program\n" << endl;
    return 0;
}
```

and commit it

```
$ git commit test_program.cpp -m "Add some output."
```

Next we add a variable containing the error code which will be returned:

```C++
#include <iostream>
using namespace std;

int main() {
    cout << "\nA nice test program\n" << endl;
    int error_code = 0;
    return error_code;
}
```

and commit the changes

```
$ git commit test_program.cpp -m "Added error_code variable."
```

Now we deliberately change the error code to 7 and commit. This will be the
commit that later needs to be identified by *git bisect* as having introduced
the error.

```C++
#include <iostream>
using namespace std;

int main() {
    cout << "\nA nice test program\n" << endl;
    int error_code = 7;
    return error_code;
}
```

Let us commit this change and as well add this README.md and the .gitignore files
to the repository.

```
$ git commit test_program.cpp -m "BUGGY COMMIT"
$ git add README.md
$ git commit -m "Added README.md"
$ git add .gitignore
$ git commit -m "Added .gitignore"
```

Using Git Bisect
----------------

In this section we use the *git bisect* command together with our python script
to find the faulty commit, which we know from the last section to be the
third-but-last one. First let us look at the log of our repository:

```
$ git log --pretty=oneline
9bba0b7924a1de313dc44bc52b8578c85669e78d Added .gitignore
031a1b7c55d30b1ff5fb155d2acd452268a801e2 Added README.md
2fae7187089d7940917dfa46cfa3f1f396d3b15d BUGGY COMMIT
ac0f77bb5e52efbe0b144d4e3d595dac67fe27d9 Added error_code variable.
c3fb9d482f7bec886378256fb326f4e18ece34c8 Add some output.
2a3716bd0f6ac2e43881809b9e85241d433e8ef9 Version 1 of the test program.
83c76f071fd00fa44458990902cd8187c9aae361 Added the bisect script.
```

Assume we do not know which commit introduced the bug. We only know that it
happened between the commit where we added the first version labeled by
*2a3716bd* and the last commit *HEAD*. This is where *git bisect* is useful,
since it allows to tell us that it happened in *BUGGY COMMIT*. To run it, just
type:

```
git bisect start HEAD 2a3716bd
git bisect run python bisect.py
```

After trying some commits which always print the output of the C++ program,
git bisect finally ends with:

```
2fae7187089d7940917dfa46cfa3f1f396d3b15d is the first bad commit
commit 2fae7187089d7940917dfa46cfa3f1f396d3b15d
Author:
Date:   Sat Mar 24 13:25:37 2018 +0100

    BUGGY COMMIT

:100644 100644 fc6abca981785eb2ae32c86df22bd69d98667e56 56eb0a9ab64e1ca4cfe1dab37c21d84496d4a614 M	test_program.cpp
bisect run success

```

It worked. Now get back to the master branch by running:

```
$ git bisect reset
```
