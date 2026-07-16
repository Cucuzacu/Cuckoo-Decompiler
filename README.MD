# Cuckoo-Decompiler



The best decompiler in the world!!!



Did you ever want to decompile something and gave up? Now you won't give up anymore! Cuckoo will use Ghidra to produce C pseudocode and then invokes Qwen-coder to fix that for you. AND it runs directly on you computer, meaning you don't need to purchase the pro plan for 1000$ per month to get 5x more messages! You still need a lot of VRAM for the smartest model tho :/



## Usage



Just do python3 run.py and follow the instructions...





Note: you need to have ollama running and you should pull the model before using it.





decompiled_source.c is the decompiler's output after feeding it the calc_token binary. It was done using the 7B model, and it works just fine without any human interactions!
