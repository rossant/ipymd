# # Test notebook

# This is a text notebook. Here *are* some **rich text**, `code`, $\pi\simeq 3.1415$ equations.

# Another equation:

# $$\sum_{i=1}^n x_i$$

# Python code:

# some code in python
def f(x):
    y = x * x
    return y

# Random code:

# ```javascript
# console.log("hello" + 3);
# ```

# Python code:

import IPython
print("Hello world!")

2*2

def decorator(f):
    return f

@decorator
def f(x):
    pass
3*3

# some text

print(4*4)

%%bash
echo 'hello'

# An image:

# ![Hello world](http://wristgeek.com/wp-content/uploads/2014/09/hello_world.png)

# ### Subtitle

# a list

# * One [small](http://www.google.fr) link!
# * Two
#   * 2.1
#   * 2.2
# * Three

# and

# 1. Un
# 2. Deux

import numpy as np
import matplotlib.pyplot as plt
%matplotlib inline

plt.imshow(np.random.rand(5,5,4), interpolation='none');

# > TIP (a block quote): That's all folks.
# > Last line.

# Last paragraph.
