# "queue.pl" uses qsub.  The options to it are
# options to qsub.  If you have GridEngine installed,
# change this to a queue you have access to.
# Otherwise, use "run.pl", which will run jobs locally
# (make sure your --num-jobs options are no more than
# the number of cpus on your machine.

#c) run it locally...
export train_cmd=utils/run.pl
export decode_cmd=utils/run.pl
export cuda_cmd=utils/run.pl
export mkgraph_cmd=utils/run.pl

