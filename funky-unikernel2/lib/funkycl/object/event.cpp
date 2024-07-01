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

#include "device.h"
#include "kernel.h"
#include "context.h"
#include "event.h"

#include <iostream>

namespace funkycl {

event::
event(cmd_queue* cmd_queue, context* cntx, cl_command_type cmd)
  : m_cmd_queue(cmd_queue), m_context(cntx), m_cmd_type(cmd)
{
  static int id_count = 0;
  m_id = id_count++;
  DEBUG_STREAM("create event obj [" << m_id << "]");
}

// event::
// event(cmd_queue* cmd_queue, context* cntx, cl_command_type cmd, cl_uint num_deps, const cl_event* deps)
//   : event(cmd_queue, cntx, cmd), m_num_deps(num_deps), wait_eids(num_deps), m_einfo(m_id, num_deps, nullptr)
// {
//   /* obtain event object ids in a waiting list */
//   if(deps == nullptr)
//     return;
// 
//   for (int i=0; i<num_deps; i++)
//   {
//     auto event = cl_to_funkycl(deps[i]);
//     // wait_eids.emplace_back(event->get_id());
//     wait_eids[i] = event->get_id();
//     DEBUG_STREAM("mem addr: " << wait_eids[i] << ", event_id[" << i << "]: " << wait_eids.back());
//   }
//   m_einfo.wait_event_ids = &wait_eids[0];
// 
//   DEBUG_STREAM("Event obj [" << m_id << "] has a waiting list. event num: " << num_deps);
// }

event::
~event()
{
  DEBUG_STREAM("destroy event obj [" << m_id << "]");
}

// void set_waiting_list_in_eventinfo(cl_uint num_events, const cl_event* event_list)
// {
//   m_einfo.wait_event_num = num_events;
// }


} // funkycl
