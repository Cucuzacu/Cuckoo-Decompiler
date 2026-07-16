// decompiled by Cuckoo Decompiler
#include <stdio.h>

int main(void) {
    int seed = 0;
    unsigned int a = 0xf27aedbf;
    unsigned int b = 0xed00b66c;

    for (int i = 0; i < 32; i++) {
        seed += -0x61c88647;
        b -= ((a >> 5) + 0x76543210 ^ a * 0x10 + 0xfedcba98 ^ a + seed);
        seed += 0x61c88647;
        a -= (b + seed ^ (b >> 5) + 0x89abcdef ^ b * 0x10 + 0x1234567);
    }

    printf("%u %u\n", a, b);
    return 0;
}
