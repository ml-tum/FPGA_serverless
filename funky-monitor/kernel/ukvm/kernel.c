/* 
 * Copyright (c) 2015-2017 Contributors as noted in the AUTHORS file
 *
 * This file is part of Solo5, a unikernel base layer.
 *
 * Permission to use, copy, modify, and/or distribute this software
 * for any purpose with or without fee is hereby granted, provided
 * that the above copyright notice and this permission notice appear
 * in all copies.
 *
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
 * WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
 * AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR
 * CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
 * OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
 * NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
 * CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 */

#include "kernel.h"

void _start(void *arg)
{
    static struct solo5_start_info si;

    console_init();
    cpu_init();
    platform_init(arg);
    si.cmdline = cmdline_parse(platform_cmdline());

    /* disable printing logs for evaluation */
    log_set_level(ERROR);

    log(INFO, "            |      ___|\n");
    log(INFO, "  __|  _ \\  |  _ \\ __ \\\n");
    log(INFO, "\\__ \\ (   | | (   |  ) |\n");
    log(INFO, "____/\\___/ _|\\___/____/\n");

    mem_init();
    time_init(arg);
    net_init();

    mem_lock_heap(&si.heap_start, &si.heap_size);
    solo5_exit(solo5_app_main(&si));
}
