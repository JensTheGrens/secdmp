/* Copyright (C) 2017 Embecosm Limited and University of Bristol

   Contributor Graham Markall <graham.markall@embecosm.com>

   This file is part of Embench and was formerly part of the Bristol/Embecosm
   Embedded Benchmark Suite.

   SPDX-License-Identifier: GPL-3.0-or-later */

#include <stdio.h>
#include <support.h>
#include "performance.h"

uint64_t begin;

void
initialise_board ()
{
  __asm__ volatile ("li a0, 0" : : : "memory");
}

void __attribute__ ((noinline)) __attribute__ ((externally_visible))
start_trigger ()
{
  begin = rdcycle();
}

void __attribute__ ((noinline)) __attribute__ ((externally_visible))
stop_trigger ()
{
  uint64_t end = rdcycle();
  uint64_t diff = end - begin;
  printf("Clock cycles: %llu\n", diff);
}
