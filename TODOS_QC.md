# Eyra TODOS for Quality Control

[QC] - Quality Control.

## High priority

## Medium priority

## Low priority

* **Write QC module for vad? [QC]**
    * This module could use compute-vad from Kaldi. - Robert
* **Write QC module for loudness? [QC]**
* **Decrease level of spaghetti on the training side [QC]**
* **Trim down Kaldi -> Koldi [QC]**
    * We don't need the world, just a few binaries, and the few scripts needed to train a simple system. Could just replace the Makefile...
    * Create a patch that changes the Makefile. Simon already did this for the tools/ directory (with sed though). We also don't really want to compile with debugging symbols (-g) and we want to compile optimized binaries (-O2 or -O3). OpenBLAS should also be an APT dependency, not compiled straight from Github. - Robert
* **Change min processing time/sleep time for celery tasks to less than a second? (celery_config.py) [QC]**
* **Create python extension for kaldi stuff [QC]**
    * By using Cython.
* **Change CleanupGenGraphs.py to simply get the tokens from mysql db directly [QC]**
    * Instead of getting it from text file in db/src and thenverifying with the db... (tunnelvision I had)
* **Make Cleanup put recId instead of tokenId in the returned report [QC]**
    * Should take 2 secs to change..