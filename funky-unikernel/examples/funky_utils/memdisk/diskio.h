#ifndef __DISKIO_H_
#define __DISKIO_H_

#include <os>
#include <memdisk> // for VFS
#include <fs/vfs.hpp>
#include <fstream>

std::vector<unsigned char> readfile_vfs(const std::string& file_name);
std::vector<char> readfile_vfs_char(const std::string& file_name);

#endif // __DISKIO_H_
