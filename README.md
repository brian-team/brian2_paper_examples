Examples for Brian 2 paper
--------------------------

This repository contains interactive examples in the form of [Jupyter notebooks]() that demonstrate
the use of the [Brian simulator](http://briansimulator.org) for neural modeling.

Running these examples needs an installation of Brian 2 (see documentation at 
[brian2.readthedocs.io](https://brian2.readthedocs.io)), together with libraries
for plotting of the results ([plotly](https://plot.ly/) and [matplotlib](https://matplotlib.org/)).

You can install all necessary dependencies by creating a [conda](https://conda.io) environment from the provided environment file:

```shell
$ conda env create -f environment.yml
```

To run the notebooks in the [binder](https://mybinder.org/) environment, without requiring any installation on your local computer, use the following link: 
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/brian-team/brian2_paper_examples/master?filepath=index.ipynb)
