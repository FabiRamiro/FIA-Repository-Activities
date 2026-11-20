import sys
import IPython
import notebook
import numpy as np
import matplotlib
import scipy
import sklearn

print("=" * 45)
print(f"Python: {sys.version.split()[0]}")
print(f"IPython: {IPython.__version__}")
print(f"Notebook: {notebook.__version__}")
print(f"NumPy: {np.__version__}")
print(f"Matplotlib: {matplotlib.__version__}")
print(f"SciPy: {scipy.__version__}")
print(f"Scikit-learn: {sklearn.__version__}")
print("=" * 45)
