// decompiled by Cuckoo Decompiler
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/evp.h>

int _init(EVP_PKEY_CTX *ctx) {
  int iVar1;

  iVar1 = 0;
  if (PTR___gmon_start___00403ff8 != (undefined *)0x0) {
    iVar1 = (*(code *)PTR___gmon_start___00403ff8)();
  }
  return iVar1;
}

void FUN_00401020(void) {
  (*(code *)PTR_00404010)();
  return;
}

void processEntry _start(undefined8 param_1,undefined8 param_2) {
  undefined1 auStack_8 [8];

  (*(code *)PTR___libc_start_main_00403ff0)(main,param_2,&stack0x00000008,0,0,param_1,auStack_8);
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

void _dl_relocate_static_pie(void) {
  return;
}

void deregister_tm_clones(void) {
  return;
}

void register_tm_clones(void) {
  return;
}

int main(void) {
  int local_1c;
  uint local_18;
  uint local_14;
  int local_10;
  int local_c;

  local_c = 0;
  for (local_10 = 0; local_10 < 0x20; local_10 = local_10 + 1) {
    local_c = local_c + -0x61c88647;
  }
  local_14 = 0xf27aedbf;
  local_18 = 0xed00b66c;
  for (local_1c = 0; local_1c < 0x20; local_1c = local_1c + 1) {
    local_18 = local_18 -
               ((local_14 >> 5) + 0x76543210 ^ local_14 * 0x10 + 0xfedcba98 ^ local_14 + local_c);
    local_c = local_c + 0x61c88647;
    local_14 = local_14 -
               (local_18 + local_c ^ (local_18 >> 5) + 0x89abcdef ^ local_18 * 0x10 + 0x1234567);
  }
  printf("%u %u\n",(ulong)local_14,(ulong)local_18);
  return 0;
}

void _fini(void) {
  return;
}
