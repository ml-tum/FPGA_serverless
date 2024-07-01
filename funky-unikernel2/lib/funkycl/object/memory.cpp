/**
 * Copyright (C) 2016-2017 Xilinx, Inc
 *
 * Licensed under the Apache License, Version 2.0 (the "License"). You may
 * not use this file except in compliance with the License. A copy of the
 * License is located at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */

#include "memory.h"
#include "device.h"
#include "kernel.h"
#include "context.h"

#include <iostream>

namespace funkycl {
memory::
memory(context* cxt, cl_mem_flags flags)
  : m_context(cxt), m_flags(flags)
{
  static unsigned int id_count = 0;
  m_id = id_count++;

  DEBUG_STREAM("create memory obj [" << m_id << "]");

  //appdebug::add_clmem(this);
}

memory::
~memory()
{
  DEBUG_STREAM("destroy memory obj [" << m_id << "]");

  // if(m_hostmem != nullptr)
  // {
  //   free(m_hostmem);
  // }
}

bool
memory::
set_kernel_argidx(const kernel* kernel, unsigned int argidx)
{
  // std::lock_guard<std::mutex> lk(m_boh_mutex);
  auto itr = std::find_if(m_karg.begin(),m_karg.end(),[kernel](auto& value) {return value.first==kernel;});
  // A buffer can be connected to multiple arguments of same kernel
  if (itr==m_karg.end() || (*itr).second!=argidx) {
    m_karg.push_back(std::make_pair(kernel,argidx));
    return true;
  }
  return false;
}

} // funkycl
