`timescale 1ns / 1ps

module ac1d_float (
    input aclk,
    input aresetn,
    AXI4SR.s                 axis_in,
    AXI4SR.m                 axis_out 
    );

localparam int N = 32768;

wire conv_in_tvalid;
wire [31:0] conv_in_tdata;
wire conv_in_tlast;
wire fft1_tready;
     
axis_dwidth_converter_64_4_c0_1 conv_in (
  .aclk(aclk),                    // input wire aclk
  .aresetn(aresetn),              // input wire aresetn
  .s_axis_tvalid(axis_in.tvalid),  // input wire s_axis_tvalid
  .s_axis_tready(axis_in.tready),  // output wire s_axis_tready
  .s_axis_tdata(axis_in.tdata),    // input wire [511 : 0] s_axis_tdata
  .s_axis_tlast(axis_in.tlast),
  .m_axis_tvalid(conv_in_tvalid),  // output wire m_axis_tvalid
  .m_axis_tready(fft1_tready),  // input wire m_axis_tready
  .m_axis_tdata(conv_in_tdata),    // output wire 
  .m_axis_tlast(conv_in_tlast)
);

reg [31:0] s_axis_config_tdata;
assign s_axis_config_tdata[4:0] = $clog2(N);
assign s_axis_config_tdata[7:5] = 0;
assign s_axis_config_tdata[8] = 1'b1;
assign s_axis_config_tdata[15:9] = 0;
assign s_axis_config_tdata[31:16] = 0; //why??
reg s_axis_config_tvalid;
reg init;

always @(posedge aclk) begin
    if(~aresetn) begin
        s_axis_config_tvalid <= 1'b0;
        init <= 1'b1;
    end else begin
        if(init) begin
            init <= 1'b0;
            s_axis_config_tvalid <= 1'b1;
        end
        if(s_axis_config_tvalid && s_axis_config_tready) begin
            s_axis_config_tvalid <= 1'b0;
        end
    end
end
        
wire fft1_tvalid;
wire [63:0] fft1_tdata;
wire fifo1_full;

xfft_1_c0_1 fft1_ip (
  .aclk(aclk),                                                // input wire aclk
  .aresetn(aresetn),
  .s_axis_config_tdata(s_axis_config_tdata),                  // input wire [15 : 0] s_axis_config_tdata
  .s_axis_config_tvalid(s_axis_config_tvalid),                // input wire s_axis_config_tvalid
  .s_axis_config_tready(s_axis_config_tready),                // output wire s_axis_config_tready
  .s_axis_data_tdata({32'd0, conv_in_tdata}),                      // input wire [63 : 0] s_axis_data_tdata
  .s_axis_data_tvalid(conv_in_tvalid),                    // input wire s_axis_data_tvalid
  .s_axis_data_tready(fft1_tready),                    // output wire s_axis_data_tready
  .s_axis_data_tlast(conv_in_tlast),                      // input wire s_axis_data_tlast
  .m_axis_data_tdata(fft1_tdata),
  .m_axis_data_tvalid(fft1_tvalid),                    // output wire m_axis_data_tvalid
  .m_axis_data_tready(~fifo1_full),                    // input wire m_axis_data_tready
  //.m_axis_data_tlast(fft1_tlast),                      // output wire m_axis_data_tlast
  .event_frame_started(event_frame_started),                  // output wire event_frame_started
  .event_tlast_unexpected(event_tlast_unexpected),            // output wire event_tlast_unexpected
  .event_tlast_missing(event_tlast_missing),                  // output wire event_tlast_missing
  .event_status_channel_halt(event_status_channel_halt),      // output wire event_status_channel_halt
  .event_data_in_channel_halt(event_data_in_channel_halt),    // output wire event_data_in_channel_halt
  .event_data_out_channel_halt(event_data_out_channel_halt)  // output wire event_data_out_channel_halt
);

wire fp_re_tvalid;
wire [31:0] fp_re_tdata;
wire fp_im_tvalid;
wire [31:0] fp_im_tdata;

wire fp_add_tready;

floating_point_mul_c0_1 fp_mul_re (
  .aclk(aclk),                                  // input wire aclk
  .aresetn(aresetn),
  .s_axis_a_tvalid(fft1_tvalid),            // input wire s_axis_a_tvalid
  .s_axis_a_tdata(fft1_tdata[31:0]),              // input wire [31 : 0] s_axis_a_tdata
  .s_axis_b_tvalid(fft1_tvalid),            // input wire s_axis_b_tvalid
  .s_axis_b_tdata(fft1_tdata[31:0]),              // input wire [31 : 0] s_axis_b_tdata
  .m_axis_result_tvalid(fp_re_tvalid),  // output wire m_axis_result_tvalid
  .m_axis_result_tdata(fp_re_tdata)    // output wire [31 : 0] m_axis_result_tdata
);

floating_point_mul_c0_1 fp_mul_im (
  .aclk(aclk),                                  // input wire aclk
  .aresetn(aresetn),
  .s_axis_a_tvalid(fft1_tvalid),            // input wire s_axis_a_tvalid
  .s_axis_a_tdata(fft1_tdata[63:32]),              // input wire [31 : 0] s_axis_a_tdata
  .s_axis_b_tvalid(fft1_tvalid),            // input wire s_axis_b_tvalid
  .s_axis_b_tdata(fft1_tdata[63:32]),              // input wire [31 : 0] s_axis_b_tdata
  .m_axis_result_tvalid(fp_im_tvalid),  // output wire m_axis_result_tvalid
  .m_axis_result_tdata(fp_im_tdata)    // output wire [31 : 0] m_axis_result_tdata
);

wire fft2_ready;
wire fp_add_tvalid;
wire [31:0] fp_add_tdata;

floating_point_add_c0_1 fp_add (
  .aclk(aclk),                                  // input wire aclk
  .aresetn(aresetn),
  .s_axis_a_tvalid(fp_re_tvalid),            // input wire s_axis_a_tvalid
  .s_axis_a_tdata(fp_re_tdata),              // input wire [31 : 0] s_axis_a_tdata
  .s_axis_b_tvalid(fp_im_tvalid),            // input wire s_axis_b_tvalid
  .s_axis_b_tdata(fp_im_tdata),              // input wire [31 : 0] s_axis_b_tdata
  .m_axis_result_tvalid(fp_add_tvalid),  // output wire m_axis_result_tvalid
  .m_axis_result_tdata(fp_add_tdata)    // output wire [31 : 0] m_axis_result_tdata
);


wire fifo_tvalid;
wire [31:0] fifo_tdata;

axis_data_fifo_0_c0_1 fifo_ip (
  .s_axis_aresetn(aresetn),          // input wire s_axis_aresetn
  .s_axis_aclk(aclk),                // input wire s_axis_aclk
  .s_axis_tvalid(fp_add_tvalid),            // input wire s_axis_tvalid
  //.s_axis_tready(s_axis_tready),            // output wire s_axis_tready
  .s_axis_tdata(fp_add_tdata),              // input wire [31 : 0] s_axis_tdata
  .m_axis_tvalid(fifo_tvalid),            // output wire m_axis_tvalid
  .m_axis_tready(fft2_ready),            // input wire m_axis_tready
  .m_axis_tdata(fifo_tdata),              // output wire [31 : 0] m_axis_tdata
  .axis_wr_data_count(axis_wr_data_count),  // output wire [31 : 0] axis_wr_data_count
  .axis_rd_data_count(axis_rd_data_count),  // output wire [31 : 0] axis_rd_data_count
  .prog_full(fifo1_full)                    // output wire prog_full
);


wire fft2_m_axis_data_tvalid;
wire [63:0] fft2_m_axis_data_tdata;
wire fifo2_full;

xfft_1_c0_1 fft2_ip (
  .aclk(aclk),                                                // input wire aclk
  .aresetn(aresetn),
  .s_axis_config_tdata(s_axis_config_tdata),                  // input wire [15 : 0] s_axis_config_tdata
  .s_axis_config_tvalid(s_axis_config_tvalid),                // input wire s_axis_config_tvalid
  //.s_axis_config_tready(s_axis_config_tready),                // output wire s_axis_config_tready
  .s_axis_data_tdata({fifo_tdata, 32'd0}),                      // input wire [63 : 0] s_axis_data_tdata
  .s_axis_data_tvalid(fifo_tvalid),                    // input wire s_axis_data_tvalid
  .s_axis_data_tready(fft2_ready),                    // output wire s_axis_data_tready
  .s_axis_data_tlast(1'b0 /*mul_last*/),                      // input wire s_axis_data_tlast
  .m_axis_data_tdata(fft2_m_axis_data_tdata),                      // 
  .m_axis_data_tvalid(fft2_m_axis_data_tvalid),                    // output wire m_axis_data_tvalid
  .m_axis_data_tready(~fifo2_full),                    // input wire m_axis_data_tready
  //.m_axis_data_tlast(fft2_m_axis_data_tlast),                      // output wire m_axis_data_tlast
  .event_frame_started(event_frame_started2),                  // output wire event_frame_started
  .event_tlast_unexpected(event_tlast_unexpected2),            // output wire event_tlast_unexpected
  .event_tlast_missing(event_tlast_missing2),                  // output wire event_tlast_missing
  .event_status_channel_halt(event_status_channel_halt2),      // output wire event_status_channel_halt
  .event_data_in_channel_halt(event_data_in_channel_halt2),    // output wire event_data_in_channel_halt
  .event_data_out_channel_halt(event_data_out_channel_halt2)  // output wire event_data_out_channel_halt
);

reg [31:0] fpdiv_divisor = $shortrealtobits(1.0 / shortreal'(N));
wire fpdiv_tvalid;
wire [31:0] fpdiv_tdata;

floating_point_mul_c0_1 fp_div (
  .aclk(aclk),                                  // input wire aclk
  .aresetn(aresetn),                            // input wire aresetn
  .s_axis_a_tvalid(fft2_m_axis_data_tvalid),            // input wire s_axis_a_tvalid
  .s_axis_a_tdata(fft2_m_axis_data_tdata[63:32]),              // input wire [31 : 0] s_axis_a_tdata
  .s_axis_b_tvalid(fft2_m_axis_data_tvalid),            // input wire s_axis_b_tvalid
  .s_axis_b_tdata(fpdiv_divisor),              // input wire [31 : 0] s_axis_b_tdata
  .m_axis_result_tvalid(fpdiv_tvalid),  // output wire m_axis_result_tvalid
  .m_axis_result_tdata(fpdiv_tdata)    // output wire [31 : 0] m_axis_result_tdata
);

wire cout_tready;
wire fifo2_tvalid;
wire [31:0] fifo2_tdata;

axis_data_fifo_0_c0_1 fifo2 (
  .s_axis_aresetn(aresetn),          // input wire s_axis_aresetn
  .s_axis_aclk(aclk),                // input wire s_axis_aclk
  .s_axis_tvalid(fpdiv_tvalid),            // input wire s_axis_tvalid
  //.s_axis_tready(s_axis_tready),            // output wire s_axis_tready
  .s_axis_tdata(fpdiv_tdata),              // input wire [31 : 0] s_axis_tdata
  .m_axis_tvalid(fifo2_tvalid),            // output wire m_axis_tvalid
  .m_axis_tready(cout_tready),            // input wire m_axis_tready
  .m_axis_tdata(fifo2_tdata),              // output wire [31 : 0] m_axis_tdata
  .axis_wr_data_count(axis_wr_data_count2),  // output wire [31 : 0] axis_wr_data_count
  .axis_rd_data_count(axis_rd_data_count2),  // output wire [31 : 0] axis_rd_data_count
  .prog_full(fifo2_full)                    // output wire prog_full
);

axis_dwidth_converter_4_64_c0_1 conv_out (
  .aclk(aclk),                    // input wire aclk
  .aresetn(aresetn),              // input wire aresetn
  .s_axis_tvalid(fifo2_tvalid),  // input wire s_axis_tvalid
  .s_axis_tready(cout_tready),  // output wire s_axis_tready
  .s_axis_tdata(fifo2_tdata),    // input wire [31 : 0] s_axis_tdata
  //.s_axis_tkeep(4'b1111),    // input wire [7 : 0] s_axis_tkeep
  .s_axis_tlast(1'b0),    // input wire s_axis_tlast
  .m_axis_tvalid(axis_out.tvalid),  // output wire m_axis_tvalid
  .m_axis_tready(axis_out.tready),  // input wire m_axis_tready
  .m_axis_tdata(axis_out.tdata)    // output wire [511 : 0] m_axis_tdata
  //.m_axis_tkeep(axis_out.tkeep),    // output wire [63 : 0] m_axis_tkeep
  //.m_axis_tlast(axis_out.tlast)    // output wire m_axis_tlast
);

assign axis_out.tlast = 1'b0;
assign axis_out.tkeep = 64'hffffffffffffffff;
assign axis_out.tid = 0;

initial begin
    $monitor($time, " fft1: valid=%d, high=%f, low=%f ", fft1_tvalid, $bitstoshortreal(fft1_tdata[63:32]), $bitstoshortreal(fft1_tdata[31:0]));
    $monitor($time, " fft_add: valid=%d, data=%f ", fp_add_tvalid, $bitstoshortreal(fp_add_tdata));
end


endmodule
