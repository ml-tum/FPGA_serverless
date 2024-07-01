#include "cmd_queue.h"

namespace funkycl
{

cmd_queue::cmd_queue(context* context, device* device, cl_command_queue_properties props) 
  : m_context(context), m_device(device), m_props(props)
{
  static unsigned int id_count = 0; 
  m_id = id_count++;

  DEBUG_STREAM("create cmd_queue obj [" << m_id << "]");
}

cmd_queue::~cmd_queue()
{
  DEBUG_STREAM("destroy cmd_queue obj [" << m_id << "]");
}

device*
cmd_queue::get_device()
{
  return m_device.get();
}

context*
cmd_queue::get_context()
{
  // return m_context;
  return m_context.get();
}

funky_msg::event_info* 
cmd_queue::create_event_info(int event_id, cl_uint num_deps, const cl_event* deps)
{
  std::vector<int> wait_eids;
  for (unsigned int i=0; i<num_deps; i++)
  {
    auto event = cl_to_funkycl(deps[i]);
    wait_eids.emplace_back(event->get_id());
    DEBUG_STREAM("wait_event addr: " << deps[i] << ", id[" << i << "]: " << wait_eids.back());
  }
  event_ids_list.emplace_back(std::make_unique<std::vector<int>>(wait_eids));

  auto reserved_list = event_ids_list.back().get();

  // event_info_list.emplace_back(std::make_unique<funky_msg::event_info>(event_id, num_deps, &wait_eids[0]));
  event_info_list.emplace_back(std::make_unique<funky_msg::event_info>(event_id, num_deps, &(reserved_list->front()) ));
  return event_info_list.back().get();
}

bool 
cmd_queue::vfpga_send_memory_request()
{
  DEBUG_STREAM("check the status of Memobjs in the backend...");

  auto context = m_context.get();
  auto device  = m_device.get();

  if(!context->is_meminfo_list_updated())
  {
    DEBUG_STREAM("Memobjs are already the latest version.");
    return false;
  }

  funky_msg::request memory_req(funky_msg::MEMORY, context->get_all_meminfo_size(), context->load_all_meminfo_addr());
  device->vfpga_send_request(memory_req);

  return true;
}

bool 
cmd_queue::vfpga_send_transfer_request(cl_uint cmdq_id, cl_uint num_mem_objects, const cl_mem* mem_objects, cl_mem_migration_flags flags, funky_msg::event_info* einfo)
{
  /* identify memory objects to be transferred */
  std::vector<int> memids;
  for (cl_uint i=0; i<num_mem_objects; i++)
  {
    auto mem = cl_to_funkycl(mem_objects[i]);
    memids.emplace_back(mem->get_id());
    DEBUG_STREAM("mem addr: " << mem_objects[i] << ", memid[" << i << "]: " << memids.back());
  }
  trans_memids_list.emplace_back(std::make_unique<std::vector<int>>(memids));

  /* create request info */
  auto trans_memids = trans_memids_list.back().get();
  DEBUG_STREAM("trans_memids addr: " << &(trans_memids->back()));

  trans_info_list.emplace_back(std::make_unique<funky_msg::transfer_info>(funky_msg::MIGRATE, &(trans_memids->front()), trans_memids->size(), flags));
  auto trans_info = trans_info_list.back().get();
  DEBUG_STREAM("Create a new transfer request info. addr: " << trans_info->ids << ", num: " << trans_info->num << ", flags: " << trans_info->flags);

  /* send a TRANSFER request */
  funky_msg::request transfer_req(funky_msg::TRANSFER, (void *)(trans_info), cmdq_id, einfo);
  auto device  = m_device.get();
  device->vfpga_send_request(transfer_req);

  return true;
}

bool 
cmd_queue::vfpga_send_transfer_request(cl_uint cmdq_id, cl_uint num_mem_objects, const cl_mem* mem_objects, 
    cl_bool blocking, size_t offset, size_t size, const void *ptr, bool is_write, funky_msg::event_info* einfo)
{
  if(num_mem_objects != 1)
  {
    std::cout << __func__ << " Error: num_mem_objects must be 1 for clEnqueueWriteBuffer(), clEnqueueReadBuffer()." << std::endl;
    return -1;
  }

  /* identify memory objects to be transferred */
  std::vector<int> memids;
  for (cl_uint i=0; i<num_mem_objects; i++)
  {
    auto mem = cl_to_funkycl(mem_objects[i]);
    memids.emplace_back(mem->get_id());
    DEBUG_STREAM("mem addr: " << mem_objects[i] << ", memid[" << i << "]: " << memids.back());
  }
  trans_memids_list.emplace_back(std::make_unique<std::vector<int>>(memids));

  /* create request info */
  auto trans_memids = trans_memids_list.back().get();
  DEBUG_STREAM("trans_memids addr: " << &(trans_memids->back()));

  funky_msg::TransType trans_type = (is_write)?  funky_msg::WRITE: funky_msg::READ;
  trans_info_list.emplace_back(std::make_unique<funky_msg::transfer_info>(trans_type, &(trans_memids->front()), trans_memids->size(), (uint64_t)blocking, offset, size, ptr));
  auto trans_info = trans_info_list.back().get();
  DEBUG_STREAM("Create a new transfer request info. addr: " << trans_info->ids << ", num: " << trans_info->num << ", flags: " << trans_info->flags);

  /* send a TRANSFER request */
  funky_msg::request transfer_req(funky_msg::TRANSFER, (void *)(trans_info), cmdq_id, einfo);
  auto device  = m_device.get();
  device->vfpga_send_request(transfer_req);

  return true;
}


bool 
cmd_queue::vfpga_send_exec_request(cl_uint cmdq_id, cl_kernel kernel, const size_t* ndrange, funky_msg::event_info* einfo)
{
  /* create args_info for exec request */
  exec_args_info_type  args_info;
  auto f_kernel = cl_to_funkycl(kernel);
  auto num_args = f_kernel->get_argnum();

  for (int idx=0; idx < num_args; idx++)
  {
    auto arg = f_kernel->get_argument(idx);
    auto arg_type = arg->get_argtype();

    if(arg_type == kernel::argtype::CLMEM)
    {
      auto mem = (memory*) arg->get_value();
      auto mem_id = (int) mem->get_id();

      funky_msg::arg_info ainfo(idx, mem_id);
      args_info.emplace_back(ainfo);
    }
    else if(arg_type == kernel::argtype::SCALAR)
    {
      funky_msg::arg_info ainfo(idx, -1, const_cast<void*>(arg->get_value()), arg->get_size());
      args_info.emplace_back(ainfo);
    }
      
    DEBUG_STREAM("arg[" << idx << "], mem_id: " << (args_info.back()).mem_id << ", size: " << arg->get_size() );
  }

  /* save the args_info and keep it until the request has been handled */
  exec_args_list.emplace_back(std::make_unique<exec_args_info_type>(args_info));
  auto exec_args_info = exec_args_list.back().get();


  DEBUG_STREAM("offset=" << ndrange[0] << ", global=" << ndrange[1] << ", local=" << ndrange[2]);

  /* send an EXECUTE request */
  auto kernel_name = f_kernel->get_name();
  funky_msg::request exec_req(funky_msg::EXECUTE, kernel_name->c_str(), kernel_name->length(), num_args, (void *)(&(exec_args_info->front())), cmdq_id, ndrange, einfo);
  auto device  = m_device.get();
  device->vfpga_send_request(exec_req);

  return true;
}

} // funkycl


