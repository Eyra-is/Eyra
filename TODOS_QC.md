# Eyra TODOS for Quality Control

[QC] - Quality Control.

## High priority

* **seems to be some issue where celery/apache/wsgi can only handle about ~20 qc sessions at a time. After that, it doesn't process more at a time.. (looking at cpu/core usage) [QC]**  
* ~~**Fix bug where celery_handler doesn't find a report on a session timeout [QC]**~~
    * [2016-06-03 15:14:09,349: ERROR/MainProcess] Task celery.qcProcSessionMarosijoModule[8a030f1a-6bfa-483e-a2c7-fec9bf69c4a5] raised unexpected: AttributeError("'NoneType' object has no attribute 'decode'",)
    * there also seems to be something writing a lot to disk on / filling the disk up - matthias
    * possibly because MarosijoModule encounters an exception? e.g. [2016-06-03 22:21:55,088: ERROR/MainProcess] Task celery.qcProcSessionMarosijoModule[5367b691-ed8b-486e-812f-69b9adf4879f] raised unexpected: KeyError('40576',) KeyError: '40576'  
    would have to happen in the first 5 recordings though - matthias
    * the file disk thing is probably: http://askubuntu.com/questions/70879/partition-is-reported-to-be-full-but-i-cannot-see-any-culprit-files - matthias
    * think i figured it out: was because of the way the code is, each requery of a session, if the report has already been dumped and deleted, this error arises! - matthias
* ~~**Fix QC task processing time (no-ops) [QC]**~~

## Medium priority

* ~~**Fix bug with 1 token missing per .ark file [QC]**~~

## Low priority

* **Write QC module for vad? [QC]**
    * This module could use compute-vad from Kaldi. - Robert
* **Write QC module for loudness? [QC]**
* **Decrease level of spaghetti on the training side [QC]**
* **Trim down Kaldi -> Koldi [QC]**
    * We don't need the world, just a few binaries, and the few scripts needed to train a simple system. Could just replace the Makefile...
    * Create a patch that changes the Makefile. Simon already did this for the tools/ directory (with sed though). We also don't really want to compile with debugging symbols (-g) and we want to compile optimized binaries (-O2 or -O3). OpenBLAS should also be an APT dependency, not compiled straight from Github. - Robert
* **Change min processing time/sleep time for celery tasks to less than a second? (celery_config.py) [QC]**
* **QC reports should be saved in mysql db [QC]**
* **Create python extension for kaldi stuff [QC]**
    * By using Cython.
* **Change CleanupGenGraphs.py to simply get the tokens from mysql db directly [QC]**
    * Instead of getting it from text file in db/src and thenverifying with the db... (tunnelvision I had)
* **Make Cleanup put recId instead of tokenId in the returned report [QC]**
    * Should take 2 secs to change..
* **Handle corrupt/missing/empty wav files on filesystem. [QC]**