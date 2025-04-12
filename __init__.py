# I created this file to convert my project into a proper Python package structure and run your tests cleanly using unittest discover
# The __init__.py files are required to make Python treat directories containing the file as packages (unless using a namespace package,
# a relatively advanced feature). This prevents directories with a common name, such as string, from unintentionally hiding valid 
# modules that occur later on the module search path. In the simplest case, __init__.py can just be an empty file, but it can also 
# execute initialization code for the package or set the __all__ variable, described later.
#Reference: https://docs.python.org/3/tutorial/modules.html#packages

#I wanted to make my project more Pythonic and robust long-term. By using this __init__py file, I can run tests using 'python -m unittest discover tests' from the root directory (instead of calling the test file directly).
