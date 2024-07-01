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

#ifndef __MEMORY_H
#define __MEMORY_H

#include <memory>
#include <vector>
#include <map>
#include <stdexcept>

#include "object.h"
#include "refcount.h"
#include "device.h"
#include "context.h"


namespace funkycl {

class memory : public _cl_mem, public refcount
{
public:
  memory(context* cxt, cl_mem_flags flags);
  virtual ~memory();

  unsigned int
  get_id() const
  {
    return m_id;
  }

  const cl_mem_flags
  get_flags() const
  {
    return m_flags;
  }

  void
  add_flags(cl_mem_flags flags)
  {
    m_flags |= flags;
  }

  /**
   * Record that this buffer is used as argument to kernel at argidx
   *
   * @return
   *   true if the {kernel,argidx} was not previously recorded,
   *   false otherwise
   */
  bool
  set_kernel_argidx(const kernel* kernel, unsigned int argidx);

  context*
  get_context() const
  {
    // return m_context;
    return m_context.get();
  }

  bool
  is_sub_buffer() const
  {
    return false;
  }

  bool
  is_device_memory_only() const
  {
    return m_flags & CL_MEM_HOST_NO_ACCESS;
  }

  // Derived classes accessors
  // May be structured differently when _xcl_mem is eliminated
  virtual size_t
  get_size() const
  {
    throw std::runtime_error("get_size on bad object");
  }

  virtual const device*
  get_device() const
  {
    return m_context->get_device();
  }

  virtual cl_mem_object_type
  get_type() const = 0;

  virtual void*
  get_host_ptr() const
  {
    throw std::runtime_error("get_host_ptr called on bad object");
  }

  virtual memory*
  get_sub_buffer_parent() const
  {
    //throw std::runtime_error("get_sub_buffer_parent called on bad object");
    return nullptr;
  }

  virtual size_t
  get_sub_buffer_offset() const
  {
    throw std::runtime_error("get_sub_buffer_offset called on bad object");
  }

  virtual cl_image_format
  get_image_format()
  {
    throw std::runtime_error("get_image_format called on bad object");
  }

  virtual size_t
  get_image_data_offset() const
  {
    throw std::runtime_error("get_image_offset called on bad object");
  }

  virtual size_t
  get_image_width() const
  {
    throw std::runtime_error("get_image_width called on bad object");
  }

  virtual size_t
  get_image_height() const
  {
    throw std::runtime_error("get_image_height called on bad object");
  }

  virtual size_t
  get_image_depth() const
  {
    throw std::runtime_error("get_image_depth called on bad object");
  }

  virtual size_t
  get_image_bytes_per_pixel() const
  {
    throw std::runtime_error("get_bytes_per_pixel called on bad object");
  }

  virtual size_t
  get_image_row_pitch() const
  {
    throw std::runtime_error("get_image_row_pitch called on bad object");
  }

  virtual size_t
  get_image_slice_pitch() const
  {
    throw std::runtime_error("get_image_slice_pitch called on bad object");
  }

  virtual void
  set_image_row_pitch(size_t pitch)
  {
    throw std::runtime_error("set_image_row_pitch called on bad object");
  }

  virtual void
  set_image_slice_pitch(size_t pitch)
  {
    throw std::runtime_error("set_image_slice_pitch called on bad object");
  }

  virtual cl_uint
  get_pipe_packet_size() const
  {
    throw std::runtime_error("get_pipe_packet_size called on bad object");
  }

  virtual cl_uint
  get_pipe_max_packets() const
  {
    throw std::runtime_error("get_pipe_max_packets called on bad object");
  }

  virtual funky_msg::mem_info* 
  get_meminfo()
  {
    throw std::runtime_error("get_meminfo called on bad object");
  }

  virtual void* 
  map_buffer(size_t& size)
  {
    throw std::runtime_error("map_buffer called on bad object");
  }

  virtual bool 
  unmap_buffer()
  {
    throw std::runtime_error("unmap_buffer called on bad object");
  }


private:
  const uint32_t m_test = 0xBEEF;
  unsigned int m_id = 0;
  // context* m_context;
  ptr<context> m_context;

  cl_mem_flags m_flags {0};

  // Record that this buffer is used as argument to kernel,argidx
  std::vector<std::pair<const kernel*,unsigned int>> m_karg;
};

class buffer : public memory
{
public:
  buffer(context* ctx,cl_mem_flags flags, size_t sz, void* host_ptr)
    : memory(ctx,flags) ,m_size(sz), m_host_ptr(host_ptr), m_meminfo(get_id(), funky_msg::BUFFER, flags, host_ptr, sz), m_hostmem(nullptr)
  {
    // TODO: check memory alignment?

    // if (flags & (CL_MEM_COPY_HOST_PTR | CL_MEM_ALLOC_HOST_PTR))
    //   // allocate sufficiently aligned memory and reassign m_host_ptr
    //   if (xrt_core::posix_memalign(&m_host_ptr,alignment,sz))
    //     throw error(CL_MEM_OBJECT_ALLOCATION_FAILURE,"Could not allocate host ptr");
    if (flags & CL_MEM_COPY_HOST_PTR && host_ptr)
    {
      // TODO: send a request to backend?
      // std::memcpy(m_host_ptr,host_ptr,sz);
    }
  }

  ~buffer()
  {
    // DEBUG_STREAM("destroy buffer obj");
    // if(m_hostmem != nullptr)
    //   free(m_hostmem);

    // DEBUG_STREAM("destroy buffer obj");
  }

  // Customized buffer allocation for 4K boundary alignment
  template <typename T>
  struct aligned_allocator {
    using value_type = T;
    T* allocate(std::size_t num) {
      void* ptr = nullptr;
      if (posix_memalign(&ptr, 4096, num * sizeof(T))) throw std::bad_alloc();
      return reinterpret_cast<T*>(ptr);
    }
    void deallocate(T* p, std::size_t num) { free(p); }
  };


  virtual cl_mem_object_type
  get_type() const
  {
    return CL_MEM_OBJECT_BUFFER;
  }

  virtual void*
  get_host_ptr() const
  {
    return m_host_ptr;
  }

  virtual size_t
  get_size() const
  {
    return m_size;
  }

  virtual void
  set_extra_sync()
  {
    m_extra_sync = true;
  }

  virtual bool
  need_extra_sync() const
  {
    return m_extra_sync;
  }

  funky_msg::mem_info* 
  get_meminfo() override
  {
    return &m_meminfo;
  }

  // for clEnqueueMapBuffer()
  void* 
  map_buffer(size_t& size) override
  {
    /* the mapped memory should be aligned to memory page size */
    if (posix_memalign(&m_hostmem, 4096, size))
      throw std::runtime_error("Could not allocate host ptr");

    m_host_ptr = m_hostmem;
    m_meminfo.src = m_host_ptr;
    m_meminfo.size = size;

    return m_host_ptr;
  }
  
  // for clEnqueueUnmapMemObject()
  bool 
  unmap_buffer() override
  {
    m_host_ptr = nullptr;
    m_meminfo.src = nullptr;
    m_meminfo.size = 0;
    free(m_hostmem);

    return true;
  }

private:
  bool m_extra_sync = false;
  size_t m_size = 0;
  void* m_host_ptr = nullptr;

  funky_msg::mem_info m_meminfo;
  void* m_hostmem;
};

class sub_buffer : public buffer
{
public:
  sub_buffer(memory* parent,cl_mem_flags flags,size_t offset, size_t sz)
  : buffer(parent->get_context(),flags,sz,
           parent->get_host_ptr()
           ? static_cast<char*>(parent->get_host_ptr())+offset
           : nullptr)
  , m_parent(parent),m_offset(offset)
  {}

  virtual size_t
  get_sub_buffer_offset() const
  {
    return m_offset;
  }

  virtual memory*
  get_sub_buffer_parent() const
  {
    return m_parent.get();
  }

  virtual const device*
  get_device() const
  {
    return m_parent->get_device();
  }

private:
  // memory* m_parent;
  ptr<memory> m_parent;
  size_t m_offset;
};

class image : public buffer
{
  struct image_info {
    cl_image_format fmt;
    cl_image_desc desc;
  };

public:
  image(context* ctx,cl_mem_flags flags, size_t sz,
        size_t w, size_t h, size_t d,
        size_t row_pitch, size_t slice_pitch,
        uint32_t bpp, cl_mem_object_type type,
        cl_image_format fmt, void* host_ptr)
    : buffer(ctx,flags,sz+sizeof(image_info), host_ptr)
    , m_width(w), m_height(h), m_depth(d)
    , m_row_pitch(row_pitch), m_slice_pitch(slice_pitch)
    , m_bpp(bpp), m_image_type(type), m_format(fmt)
  {
  }

  virtual cl_mem_object_type
  get_type() const
  {
    return m_image_type;
  }

  virtual cl_image_format
  get_image_format()
  {
    return m_format;
  }

  virtual size_t
  get_image_data_offset() const
  {
    return sizeof(image_info);
  }

  virtual size_t
  get_image_width() const
  {
    return m_width;
  }

  virtual size_t
  get_image_height() const
  {
    return m_height;
  }

  virtual size_t
  get_image_depth() const
  {
    return m_depth;
  }

  virtual size_t
  get_image_bytes_per_pixel() const
  {
    return m_bpp;
  }

  virtual size_t
  get_image_row_pitch() const
  {
    return m_row_pitch;
  }

  virtual size_t
  get_image_slice_pitch() const
  {
    return m_slice_pitch;
  }

  virtual void
  set_image_row_pitch(size_t pitch)
  {
    m_row_pitch = pitch;
  }

  virtual void
  set_image_slice_pitch(size_t pitch)
  {
    m_slice_pitch = pitch;
  }

private:

  void populate_image_info(image_info& info) {
    memset(&info, 0, sizeof(image_info));
    info.fmt = m_format;
    info.desc.image_type=m_image_type;
    info.desc.image_width=m_width;
    info.desc.image_height=m_height;
    info.desc.image_depth=m_depth;
    info.desc.image_array_size=0;
    info.desc.image_row_pitch=m_row_pitch;
    info.desc.image_slice_pitch=m_slice_pitch;
    info.desc.num_mip_levels=0;
    info.desc.num_samples=0;
  }

private:
  size_t m_width;
  size_t m_height;
  size_t m_depth;
  size_t m_row_pitch;
  size_t m_slice_pitch;
  uint32_t m_bpp; //bytes per pixel
  cl_mem_object_type m_image_type;
  cl_image_format m_format;
};

/**
 * Pipes are not accessible from host code.
 */
class pipe : public memory
{
public:
  pipe(context* ctx,cl_mem_flags flags, cl_uint packet_size, cl_uint max_packets)
    : memory(ctx,flags), m_packet_size(packet_size), m_max_packets(max_packets)
  {}

  void
  set_pipe_host_ptr(void* p)
  {
    m_host_ptr = p;
  }

  virtual cl_mem_object_type
  get_type() const
  {
    return CL_MEM_OBJECT_PIPE;
  }

  virtual cl_uint
  get_pipe_packet_size() const
  {
    return m_packet_size;
  }

  virtual cl_uint
  get_pipe_max_packets() const
  {
    return m_max_packets;
  }

private:
  cl_uint m_packet_size = 0;
  cl_uint m_max_packets = 0;
  void* m_host_ptr = nullptr;
};

} // funkycl

#endif // __MEMORY_H;


