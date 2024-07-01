#include <os> // IncludeOS
#include <unistd.h>
#include <stdlib.h>
#include <string>
#include <sstream>
#include <chrono>
#include <iomanip>
extern "C" {
#include <solo5.h>
}

void func(std::string_view &input, std::stringstream &output) {
	output<<"--- Begin on input ---"<<std::endl;
	output<<input<<std::endl;
	output<<"--- End of input ---"<<std::endl;
}
