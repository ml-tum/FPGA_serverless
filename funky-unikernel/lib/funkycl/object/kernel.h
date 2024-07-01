/**
 * Copyright (C) 2016-2020 Xilinx, Inc
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

#ifndef __KERNEL_H
#define __KERNEL_H

#include <memory>
#include <vector>
#include <map>
#include <stdexcept>
#include <limits>
#include <iostream>

#include "object.h"
#include "refcount.h"
#include "device.h"
#include "memory.h"
#include "program.h"
#include "context.h"

namespace funkycl {

// FIXME: compute_unit class is not necessary in guest?
// class compute_unit;

class kernel : public _cl_kernel, public refcount
{
public:
  enum argtype {CLMEM, SCALAR, NOTYPE};
  /**
   * class argument is a class hierarchy that represents a kernel
   * object argument constructed from meta data.
   */
  // TODO: develop functions to read metadata from xilinx bitstream? (xclbin)
  // They will be used to construct argument class?
  // Or class argument doesn't need to be instantiated in guest side?
  class argument
  {
  public:
    argument(kernel* kernel) : m_kernel(kernel) {}

    bool is_set() const
    { return m_set; }

    void set(unsigned long argidx, size_t size, const void* arg)
    {
      m_argidx = argidx;
      set(size, arg);
    }

    unsigned long get_argidx() const
    { return m_argidx; }

    virtual ~argument() {}

    /**
     * Set an argument (clSetKernelArg) to some value.
     */
    virtual void set(size_t sz, const void* arg) = 0;

    virtual size_t get_size() const
    { return 0; }

    virtual const void* get_value() const
    { return nullptr; }

    virtual argtype get_argtype() const
    { return NOTYPE; }

  protected:
    kernel* m_kernel = nullptr;
    unsigned long m_argidx = std::numeric_limits<unsigned long>::max();
    bool m_set = false;
  };

  /* argument classes for funkycl (real arg is instantiated by backend) */
  class clmem_argument : public argument
  {
  public:
    clmem_argument(kernel* kernel, unsigned long argidx)
      : argument(kernel)  {}

    virtual void set(size_t size, const void* arg);

    virtual size_t get_size() const 
    { return sizeof(memory*); }

    virtual const void* get_value() const 
    { return m_buffer.get(); }

    virtual argtype get_argtype() const 
    { return CLMEM; }

  private:
    // memory* m_buffer; // buffer class? shared_ptr?
    ptr<memory> m_buffer; // retain ownership
  };

  class scalar_argument : public argument
  {
  public:
    scalar_argument(kernel* kernel, unsigned long argidx)
      : argument(kernel) {}

    virtual void set(size_t size, const void* arg)
    {
      m_size  = size;
      m_value = const_cast<void*>(arg);
      m_set = true;
    }

    virtual size_t get_size() const 
    { return m_size; }

    virtual const void* get_value() const 
    { return m_value; }
    
    virtual argtype get_argtype() const 
    { return SCALAR; }

  private:
    size_t m_size;
    void* m_value;
    // std::vector<uint8_t> m_value;
  };

public:
  // only program constructs kernels, but private doesn't work as long
  // std::make_unique is used
  // friend class program; // only program constructs kernels
  kernel(program* prog, const std::string& name);
  virtual ~kernel();

  unsigned int get_id() const
  {
    return m_id;
  }

  program* get_program() const
  {
    return m_program.get();
  }

  std::string* get_name()
  {
    return m_name.get();
  }

  int get_argnum() const
  { 
    return m_args.size(); 
  }

  argument* get_argument(int idx) const
  { 
    return m_args.at(idx).get(); 
  }

  context* get_context() const;
  // void create_argument(unsigned long idx);
  void create_clmem_argument(unsigned long idx);
  void create_scalar_argument(unsigned long idx);
  void set_argument(unsigned long idx, size_t size, const void* arg);

private:
  unsigned int m_id = 0;
  // program* m_program;
  ptr<program> m_program;
  std::unique_ptr<std::string> m_name;
  // std::vector<std::unique_ptr<argument>> m_args;
  std::map<unsigned long, std::unique_ptr<argument>> m_args;
};

} // funkycl

#endif

