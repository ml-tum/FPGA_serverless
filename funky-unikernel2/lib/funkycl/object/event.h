#ifndef __EVENT_H
#define __EVENT_H

#include <memory>
#include <vector>

#include "object.h"
#include "refcount.h"

#include "context.h"
#include "cmd_queue.h"

namespace funkycl {

class event : public _cl_event, public refcount
{
public:
  event(cmd_queue* cmd_queue, context* cntx, cl_command_type cmd);
  // event(cmd_queue* cmd_queue, context* cntx, cl_command_type cmd, cl_uint num_deps, const cl_event* deps);
  virtual ~event();

  int
  get_id() const
  {
    return m_id;
  }

  context*
  get_context() const
  {
    // return m_context;
    return m_context.get();
  }

  // void set_param_in_eventinfo(cl_uint param_name, void* param_value)
  // {
  //   m_einfo.param_name = param_name;
  //   m_einfo.param = param_value;
  // }

  // void set_waiting_list_in_eventinfo(cl_uint num_events, const cl_event* event_list);

  // funky_msg::event_info* 
  // get_eventinfo() 
  // {
  //   return &m_einfo;
  // }


private:
  int m_id = 0;
  // context* m_context;
  ptr<cmd_queue> m_cmd_queue;
  ptr<context> m_context;
  cl_command_type m_cmd_type = 0;
  // cl_uint m_num_deps = 0;
  // cl_event* m_deps = nullptr;

  // std::vector<unsigned int> wait_eids;
  // funky_msg::event_info m_einfo;
};


} // funkycl

#endif // __EVENT_H


