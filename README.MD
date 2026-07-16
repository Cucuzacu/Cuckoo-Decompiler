# Cuckoo-Decompiler



The best decompiler in the world!!!



Did you ever want to decompile something and gave up? Now you won't give up anymore! Cuckoo will use Ghidra to produce C pseudocode and then invokes Qwen-coder to fix that for you. AND it runs directly on you computer, meaning you don't need to purchase the pro plan for 1000$ per month to get 5x more messages! You still need a lot of VRAM for the smartest model tho :/



## Usage



Just do python3 run.py and follow the instructions...



Here's an estimation for each model:

1.5B (Fast) \~1.5 gb VRAM, Should run on any basic GPU(including integrated ones).

7B (Standard) \~5.5 gb VRAM, Should run on NVIDIA GTX 1060 / 1660,RTX 3050 (6GB) and some powerful integrated GPUs.

14B (Heavy) \~10 gb VRAM, Should run on NVIDIA RTX 3060 (12GB),RTX 4060 Ti (16GB). It is not recommennded to run this on an integrated GPU.

32B (NASA Supercomputer) \~22 gb VRAM, Should run on NVIDIA RTX 3090 / 4090. Very slow but very powerful. Don't even think of running this on an integrated GPU.





Note: you need to have ollama running and you should pull the model before using it.





decompiled_source.c is the decompiler's output after feeding it the calc_token binary. It was done using the Fast model, and it works just fine without any human interactions!
