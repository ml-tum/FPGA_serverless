#include <os>
#include <net/inet>
#include <net/http/request.hpp>
#include <net/http/response.hpp>
#include <sys/time.h>
#include <kernel/events.hpp>

#define LISTEN_PORT	8080
#define TCP_MSS 1000

std::map<std::string,std::stringstream> chunked_data;

extern void func(std::string_view &input, std::stringstream &output);

long long int getNanos() {
  timespec ts;
  long long int nanos;
  clock_gettime(CLOCK_REALTIME, &ts);
  nanos = ts.tv_sec*1e9 + ts.tv_nsec;
  return nanos;
}

http::Response handle_request(const http::Request& req)
{
  http::Response res;
  auto& header = res.header();

  //printf("@Request:\nvvv\n%s\n^^^\n", req.body().data());
  

  if (req.method() == http::GET && req.uri().to_string() == "/_/health")
  {
    res.set_status_code(http::OK);
  }
  else if((req.method() == http::GET || req.method() == http::POST) && req.uri().to_string() == "/")
  {
    std::string_view input = req.body();
    std::stringstream output;

    printf("@Call Func\n");
    long long int timer = getNanos();
    func(input, output);
    timer = getNanos()-timer;

    res.set_status_code(http::OK);
    if(req.header().has_field("X-no-output"))
	res.add_body("");
    else
	res.add_body(output.str());
    header.set_field("X-computation-time", std::to_string(timer) + " ns");
  }
  else
  {
    res.set_status_code(http::Not_Found);
  }

  //header.set_field(http::header::Date, "Wed, 15 May 2023 17:06:33 GMT");
  header.set_field(http::header::Content_Type, "text/plain; charset=utf-8");
  header.set_field(http::header::Content_Length, std::to_string(res.body().size()));
  header.set_field(http::header::Server, "IncludeOS");
  header.set_field(http::header::Connection, "close");

  return res;
}

void write_response(const net::tcp::Connection_ptr &conn, http::Response &resp) {
  printf("@ Responding with %u %s.\n",resp.status_code(), http::code_description(resp.status_code()).data());
  //printf("@ Response:\nvvv\n%s\n^^^\n", resp.to_string().c_str());
  std::string str = resp.to_string();
  for(size_t i=0; i<(str.size()+TCP_MSS-1)/TCP_MSS; i++) {
    conn->write(str.substr(i*TCP_MSS, TCP_MSS));
  }
  conn->close();
  chunked_data.erase(conn->remote().to_string());
}

void handle_read(const net::tcp::Connection_ptr &conn, net::tcp::buffer_t buf) {
    
  const std::string client = conn->remote().to_string();

  //printf("@receive %lu bytes, chunked=%ld, from=%s \n", buf->size(), chunked_data.count(client), conn->remote().to_string().c_str());

  try
  {
    //const std::string data2((const char*) buf->data(), buf->size());
    //printf("@data\n~~~~~\n%s~~~~~\n", data2.c_str());

    if(!chunked_data.count(client)) {
      printf("@Parse1\n");
      const std::string data((const char*) buf->data(), buf->size());
      http::Request req{data};
      if(req.header().has_field("Transfer-Encoding") && req.header().value("Transfer-Encoding")=="chunked") {
        chunked_data[client];
        printf("@ Chunked request\n");
      } else {
        auto res = handle_request(req);
        write_response(conn, res);
      }
    }
    if(chunked_data.count(client)) {
      //printf("@ Add chunk \n");
      const std::string data((const char*) buf->data(), buf->size());
      chunked_data[client]<<data;
//      if(data.size() >= 5 && data.substr(data.size()-5)=="0\r\n\r\n") { // <-- this is very problematic!
      if(data.size() == 5 && data.substr(data.size()-5)=="0\r\n\r\n"
         || data.size() >= 7 && data.substr(data.size()-7)=="\r\n0\r\n\r\n") { // <-- this is very problematic!
        printf("@ Parse2\n");
        http::Request req(chunked_data[client].str());
        auto res = handle_request(req);
        write_response(conn, res);
      }
    }
  }
  catch(const std::exception& e)
  {
    printf("@ Unable to parse request:\n%s\n", e.what());
  }
}


int Service::start(const std::string& cmd)
{
  (void)cmd;
  
  // Get the first IP stack
  // It should have configuration from config.json
  auto& inet = net::Super_stack::get(0);
  auto& server = inet.tcp().listen(LISTEN_PORT);

  // Add a TCP connection handler - here a hardcoded HTTP-service
  server.on_connect(
  [] (net::tcp::Connection_ptr conn) {

    printf("@on_connect: Connection %s successfully established.\n", conn->remote().to_string().c_str());

    conn->on_read(32*1024, [conn] (auto buf) { 
      handle_read(conn, buf);
    });

    conn->on_write([](size_t written) {
      /*timespec ts;
      clock_gettime(CLOCK_REALTIME, &ts);
      long long int millis = ts.tv_sec*1000LL + ts.tv_nsec/1000LL/1000LL;
      printf("@on_write: %lu bytes written. Time=%lld \n", written, millis);*/
    });
    
    conn->on_close([conn]() {
      const std::string client = conn->remote().to_string();
      chunked_data.erase(client);
    });
  });

  printf("*** A watchdog implementation for OpenFaas ***\n");
  OS::event_loop();
  
  return 0;
}
