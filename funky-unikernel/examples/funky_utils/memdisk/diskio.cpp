#include "diskio.h"

// fs::Disk disk;
static bool vfs_init_flag=false;

void init_vfs(void)
{
  auto& disk = fs::memdisk();

  disk.init_fs([] (fs::error_t err, auto&) {
      assert(!err);
      });

  vfs_init_flag = true;
  return;
}

std::vector<unsigned char> readfile_vfs(const std::string& file_name)
{
  if(!vfs_init_flag)
    init_vfs();

  // read bitstream file using memdisk
  auto& disk = fs::memdisk();
  auto file = disk.fs().read_file(file_name);
  std::vector<unsigned char> bs(file.data(), file.data() + file.size());

  return bs;
}


std::vector<char> readfile_vfs_char(const std::string& file_name)
{
  if(!vfs_init_flag)
    init_vfs();

  // read bitstream file using memdisk
  auto& disk = fs::memdisk();
  auto file = disk.fs().read_file(file_name);
  std::vector<char> bs(file.data(), file.data() + file.size());

  return bs;
}

