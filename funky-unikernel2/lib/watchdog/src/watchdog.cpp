// This file is a part of the IncludeOS unikernel - www.includeos.org
//
// Copyright 2015 Oslo and Akershus University College of Applied Sciences
// and Alfred Bratterud
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <os>
#include <unistd.h>
#include <net/inet>
#include <net/http/request.hpp>
#include <net/http/response.hpp>

#define LISTEN_PORT	8080
#define ARGS_MAX	64

int margc = 0;
char* margv[ARGS_MAX];
std::vector<std::string> func_out;

extern int main(int argc, const char *argv[]);

http::Response handle_request(const http::Request& req)
{
  http::Response res;
  auto& header = res.header();

  printf("<Service> Request:\n%s\n", req.to_string().c_str());
  //header.set_field(http::header::Server, "IncludeOS/0.10");

  OS::add_stdout(
  [] (const char* data, size_t len) {
    std::string tmp_str (data, len);
    func_out.push_back(tmp_str);
  });
  // GET /
  if(req.method() == http::GET && req.uri().to_string() == "/")
  {
    main(margc, (const char **)margv);
    std::stringstream resp_body;
    for (std::string tmp_out: func_out) {
      resp_body << tmp_out;
    }
    // add HTML response
    res.add_body(resp_body.str());
    func_out.clear();

    // set Content type and length
    header.set_field(http::header::Content_Type, "text/plain; charset=utf-8");
    //header.set_field(http::header::Content_Length, std::to_string(res.body().size()));
  }
  else if (req.method() == http::GET && req.uri().to_string() == "/_/health")
  {
    res.add_body("OK");
    res.set_status_code(http::OK);
  }
  else
  {
    // Generate 404 response
    res.set_status_code(http::Not_Found);
  }
  OS::remove_stdout();
  /*
   * We might need to set the proper Date. However ctime and http::time hepers do
   * not seem to work
   */
  header.set_field(http::header::Date, "Wed, 15 May 2023 17:06:33 GMT");
  header.set_field(http::header::Content_Type, "text/plain; charset=utf-8");
  header.set_field(http::header::Content_Length, std::to_string(res.body().size()));

  header.set_field(http::header::Connection, "close");

  return res;
}

static void parse_cmdline(const std:: string& cmd)
{
  std::string argv0 = "Funky_unikernel";
  std::string st(cmd); // mangled copy

  // Setup first argument, which is supposed to be the name of the application/program
  // Since IncludeOS does not store this information, we specify Funky_unikernel
  // as the first argument
  margv[0] = (char *) new char[argv0.size() + 1];
  strcpy(margv[0], argv0.c_str());
  margc++;
  // Copy the whole command line in a dynamically allocated memory
  // and specify each argument by pointing to the start of each word
  margv[1] = (char *) new char[st.size() + 1];
  strcpy(margv[1], st.c_str());
  // Get pointers to null-terminated string
  char* word = (char*) margv[1];
  char* end  = word + st.size() + 1;
  bool new_word = false;

  for (char* ptr = word; ptr < end; ptr++) {

    // Replace all spaces with 0
    if(std::isspace(*ptr)) {
      *ptr = 0;
      new_word = true;
      continue;
    }

    // At the start of each word, or last byte, add previous pointer to array
    if (new_word or ptr == end - 1) {
      margv[margc++] = word;
      word = ptr; // next arg
      if (margc >= ARGS_MAX) break;
      new_word = false;
    }
  }
}

int Service::start(const std::string& cmd)
{
  // Get the first IP stack
  // It should have configuration from config.json
  auto& inet = net::Super_stack::get(0);

  // Set up a TCP server on LISTEN_PORT port
  auto& server = inet.tcp().listen(LISTEN_PORT);

  parse_cmdline(cmd);

  // Add a TCP connection handler - here a hardcoded HTTP-service
  server.on_connect(
  [] (net::tcp::Connection_ptr conn) {
    printf("<Service> @on_connect: Connection %s successfully established.\n",
      conn->remote().to_string().c_str());
    // read async with a buffer size of 1024 bytes
    // define what to do when data is read
    conn->on_read(1024,
    [conn] (auto buf)
    {
      printf("<Service> @on_read: %lu bytes received.\n", buf->size());
      try
      {
        const std::string data((const char*) buf->data(), buf->size());
        // try to parse the request
        http::Request req{data};

        // handle the request, getting a matching response
        auto res = handle_request(req);

        printf("<Service> Responding with %u %s.\n",
          res.status_code(), http::code_description(res.status_code()).data());

        conn->write(res);
      }
      catch(const std::exception& e)
      {
        printf("<Service> Unable to parse request:\n%s\n", e.what());
      }
    });
    conn->on_write([](size_t written) {
      printf("<Service> @on_write: %lu bytes written.\n", written);
    });
  });

  printf("*** A watchdog implementation for OpenFaas ***\n");
  OS::event_loop();
}
