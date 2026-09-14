/* MIT License
 *
 * Copyright (c) 2016-2020 INRIA, CMU and Microsoft Corporation
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */


#include "Hacl_HMAC.h"
#include "../macros.h"

#include "Hacl_Hash_SHA2.h"

/**
Write the HMAC-SHA-2-256 MAC of a message (`data`) by using a key (`key`) into `dst`.

The key can be any length and will be hashed if it is longer and padded if it is shorter than 64 bytes.
`dst` must point to 32 bytes of memory.
*/
void
Hacl_HMAC_compute_sha2_256(
  uint8_t *dst,
  uint8_t *key,
  uint32_t key_len,
  uint8_t *data,
  uint32_t data_len
)
{
  uint32_t l = (uint32_t)64U;
  confidential static uint8_t key_block[64U];
  memset(key_block, 0U, l * sizeof (uint8_t));
  uint32_t i0;
  if (key_len <= (uint32_t)64U)
  {
    i0 = key_len;
  }
  else
  {
    i0 = (uint32_t)32U;
  }
  uint8_t *nkey = key_block;
  if (key_len <= (uint32_t)64U)
  {
    memcpy(nkey, key, key_len * sizeof (uint8_t));
  }
  else
  {
    Hacl_Hash_SHA2_hash_256(key, key_len, nkey);
  }
  confidential static uint8_t ipad[64U];
  memset(ipad, (uint8_t)0x36U, l * sizeof (uint8_t));
  for (uint32_t i = (uint32_t)0U; i < l; i++)
  {
    confidential static uint8_t xi;
    xi = ipad[i];
    confidential static uint8_t yi;
    yi = key_block[i];
    ipad[i] = xi ^ yi;
  }
  confidential static uint8_t opad[64U];
  memset(opad, (uint8_t)0x5cU, l * sizeof (uint8_t));
  for (uint32_t i = (uint32_t)0U; i < l; i++)
  {
    confidential static uint8_t xi;
    xi = opad[i];
    confidential static uint8_t yi;
    yi = key_block[i];
    opad[i] = xi ^ yi;
  }
  confidential static uint32_t scrut0[8U];
  scrut0[0] = (uint32_t)0x6a09e667U;
  scrut0[1] = (uint32_t)0xbb67ae85U;
  scrut0[2] = (uint32_t)0x3c6ef372U;
  scrut0[3] = (uint32_t)0xa54ff53aU;
  scrut0[4] = (uint32_t)0x510e527fU;
  scrut0[5] = (uint32_t)0x9b05688cU;
  scrut0[6] = (uint32_t)0x1f83d9abU;
  scrut0[7] = (uint32_t)0x5be0cd19U;
  uint32_t *s = scrut0;
  uint8_t *dst1 = ipad;
  Hacl_Hash_Core_SHA2_init_256(s);
  if (data_len == (uint32_t)0U)
  {
    Hacl_Hash_SHA2_update_last_256(s, (uint64_t)0U, ipad, (uint32_t)64U);
  }
  else
  {
    Hacl_Hash_SHA2_update_multi_256(s, ipad, (uint32_t)1U);
    uint32_t block_len = (uint32_t)64U;
    uint32_t n_blocks0 = data_len / block_len;
    uint32_t rem = data_len % block_len;
    K___uint32_t_uint32_t scrut;
    if (n_blocks0 > (uint32_t)0U && rem == (uint32_t)0U)
    {
      uint32_t n_blocks_ = n_blocks0 - (uint32_t)1U;
      scrut = ((K___uint32_t_uint32_t){ .fst = n_blocks_, .snd = data_len - n_blocks_ * block_len });
    }
    else
    {
      scrut = ((K___uint32_t_uint32_t){ .fst = n_blocks0, .snd = rem });
    }
    uint32_t n_blocks = scrut.fst;
    uint32_t rem_len = scrut.snd;
    uint32_t full_blocks_len = n_blocks * block_len;
    uint8_t *full_blocks = data;
    Hacl_Hash_SHA2_update_multi_256(s, full_blocks, n_blocks);
    uint8_t *rem0 = data + full_blocks_len;
    Hacl_Hash_SHA2_update_last_256(s,
      (uint64_t)(uint32_t)64U + (uint64_t)full_blocks_len,
      rem0,
      rem_len);
  }
  Hacl_Hash_Core_SHA2_finish_256(s, dst1);
  uint8_t *hash1 = ipad;
  Hacl_Hash_Core_SHA2_init_256(s);
  Hacl_Hash_SHA2_update_multi_256(s, opad, (uint32_t)1U);
  uint32_t block_len = (uint32_t)64U;
  uint32_t n_blocks0 = (uint32_t)32U / block_len;
  uint32_t rem = (uint32_t)32U % block_len;
  K___uint32_t_uint32_t scrut;
  if (n_blocks0 > (uint32_t)0U && rem == (uint32_t)0U)
  {
    uint32_t n_blocks_ = n_blocks0 - (uint32_t)1U;
    scrut =
      ((K___uint32_t_uint32_t){ .fst = n_blocks_, .snd = (uint32_t)32U - n_blocks_ * block_len });
  }
  else
  {
    scrut = ((K___uint32_t_uint32_t){ .fst = n_blocks0, .snd = rem });
  }
  uint32_t n_blocks = scrut.fst;
  uint32_t rem_len = scrut.snd;
  uint32_t full_blocks_len = n_blocks * block_len;
  uint8_t *full_blocks = hash1;
  Hacl_Hash_SHA2_update_multi_256(s, full_blocks, n_blocks);
  uint8_t *rem0 = hash1 + full_blocks_len;
  Hacl_Hash_SHA2_update_last_256(s,
    (uint64_t)(uint32_t)64U + (uint64_t)full_blocks_len,
    rem0,
    rem_len);
  Hacl_Hash_Core_SHA2_finish_256(s, dst);
}

