## Add a new library in IncludeOS

IncludeOS is a library operating system and as a result every component is a
different library. In order to add a new feature we have to create a new
library and add it in the build system of IncludeOS. At first we need to define
the type of our new library. Looking at the cmake file of the applications we
can see that drivers, platform and plugins are selected from the user to be
linked with the application. On the contrary standard libraries and OS
components will be selected by the linker if and only if the application needs
any of these libraries. The process of adding any new component seems to be the
same, even if we add a new driver, plugin or library. The main difference is
that when we build the unikernel. As we said before if we add a new driver or
plugin we have to select it in the cmake file of our application. Otherwise
linker will decide if our library is needed.

### A hello world library

To get familiar with the build system and the structure of IncludeOS we will add
a new library which supports one and only function `add_hello`. This function
will print a hello message and will return the result of adding the two arguments. 

The code is pretty simple, without any dependencies.

```
int add_hello(int a, int b)
{
	std::cout << "Hello from hello lib\n";
	return a + b;
|
```
At first we will add this library as a OS component, which means that it will be
included in the `libos.a` library. This library is always linked with the
application, when we build the unikernel.

#### Step 1: Adding the source code

At first we need to create a new directory which will contain the source code of
the new library. We will add it as an "internal" library, like any other OS
component and standard library. In the src directory of IncludeOS we will add a
new directory, where we will place the source code of our simple function. 

#### Step 2: Notifying IncludeOS about the new library

In the `CMakeLists.txt` We should add the source code of our library to the OS
objects. 

```
...............
  # Hello lib
  hello_lib/hello.cpp

)
...............
```

#### Step 3: Adding header files

The header file of our library should be installed in the 
`$INCLUDEOS_PREFIX/includeos/include` directory. IncludeOS keeps all the header
files of "internal" libraries under the api directory in its repo. In that
context we will create one more directory under api, where we will store our
header files.

```
cd api
mkdir hello_lib
echo "int add_hello(int a, int b);" > hello_lib/hello.hpp
```

#### Step 4: Rebuild IncludeOS

Finally we need to build IncludeOS with our new library. In the build directory
we can just run

```
make && make install
```

We can see in the output that our library has been installed.

#### Step 5: Using the library

The only thing we need to do to use our library is to include the header file and
call the function. 

```
#include <iostream>
#include <hello_lib/hello.hpp>

int main()
{
	int res;

	std::cout << "I will call our new function add_hello \n";
	res = add_hello(1, 2);
	std::cout << "Result of addition is " << res << std::endl;

	return 0;
}
```
### An external hello world library

It is also possible to build the library as "external". In that way the library
will not be part of IncludeOS' OS components and standard libraries.
Subsequently when we build the application we have to specify that we will need
that library, the same way as we do with drivers. `microLB`, `LiveUpdate` and
`uplink` are examples of such libraries. These libraries reside under the `lib`
directory of the IncludeOS repo.

The steps to add an "external" library are similar except of the way we notify
IncludeOS build system about our library. We will add a slightly different
library which instead of addition it calculates the subtraction of the 2
arguments.

```
#include <iostream>

int sub_bye(int a, int b)
{
	std::cout << "Bye from bye lib\n";
	return a - b;
|
```

#### Step 1: Adding the source code

As we pointed earlier "external" libraries reside on the lib directory. This is
the place for our new library under the directory `bye_lib`. Following the other
libraries we will have a similar directory tree.

```
bye_lib
|-src/
|-inlcude/bye_lib/
```

In our case we have only one source code and we will have one header file.

```
$ cat include/bye_lib/bye.hpp
int sub_bye(int a, int b);
$
```

#### Step 2: Notifying IncludeOS about the new library

In contrast with "internal" libraries, we have to specify our own
`CMakeLists.txt` file. We can use the cmake files of other libraries as a base.
Comments below give a small explanation about some parts of this file.

```
cmake_minimum_required(VERSION 2.8.9)

add_definitions(-DARCH_${ARCH})
add_definitions(-DARCH="${ARCH}")

#dependencies. We specify all other IncludeOS' components and standard
#libraries. In case that we have more depedencies like other external libraries
#we have to specify the library here.
include_directories(${INCLUDEOS_ROOT}/api/posix)
include_directories(${LIBCXX_INCLUDE_DIR})
include_directories(${MUSL_INCLUDE_DIR})
include_directories(${INCLUDEOS_ROOT}/src/include)
include_directories(${INCLUDEOS_ROOT}/api)

set(LIBRARY_NAME "bye_lib")

set(SOURCES
  src/bye.cpp
  )

add_library(${LIBRARY_NAME} STATIC ${SOURCES})
#We need to specify any build time depedencies. Maybe an another library we need
#has to be built first.
add_dependencies(${LIBRARY_NAME} PrecompiledLibraries)

install(TARGETS ${LIBRARY_NAME} DESTINATION includeos/${ARCH}/lib)
install(DIRECTORY include/bye_lib DESTINATION includeos/include)
```

Moreover we need to add this subdirectory in the main cmake file of IncludeOS.

```
................
option(libbyelib "A test library" ON)
if(libbyelib)
  add_subdirectory(lib/bye_lib)
endif()
................
```

#### Step 3: Building our library

Finally we need to follow the same procedure to build IncludeOS so our new
library gets included too. IncludeOS with our new library.
In the build directory we can just run

```
cmake .. -DCMAKE_INSTALL_PREFIX=${INCLUDEOS_PREFIX}
make PrecompiledLibraries
make 
make install
```

We can see in the output that our library has been installed.

#### Step 4: Using the library

In case of "external" library we have to specify in the cmake file of our
application the library that is needed. In our case we have to add the following
lines.

```
set(LIBRARIES
	libbye_lib.a
  )
```

Finally we need to run `cmake` again and then build our unikernel.
```
#include <iostream>
#include <hello_lib/hello.hpp>
#include <bye_lib/bye.hpp>

int main()
{
	int res;

	std::cout << "I will call our new function add_hello \n";
	res = add_hello(1, 2);
	std::cout << "Result of addition is " << res << std::endl;

	std::cout << "I will call our new function sub_bye \n";
	res = sub_bye(res, 2);
	std::cout << "Result of subtraction is " << res << std::endl;

	return 0;
}
```



