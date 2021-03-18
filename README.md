<h1> Long Term Memory </h1>

<h2 align="center">Persistent meta-data storage for Hyperactive.</h2>

<br>

This package is an extension of the memory module in Hyperactive. It enables Hyperactive to "remember" previous evaluations, which can save significant computation time. The effect is, that every position in the search-space that has been evaluated once never needs to be evaluated again. The previous calculated score has been stored and can just be looked up instead of recalculating it. Long Term Memory stores this search data and loades it if another optimization run is started.
Long Term Memory also enables persistent storage of python-functions in the search-data. This means, that information about the objective-function and python-functions in the search-space can be saved and read via the dill-package.

