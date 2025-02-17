module hyperloglog_wrapper(
    AXI4L.s                     axi_ctrl,
    AXI4SR.s                    axis_host_0_sink,
    AXI4SR.m                    axis_host_0_src,
    input  wire                 aclk,
    input  wire[0:0]            aresetn
);

reg ul_resetn=0;

always @(posedge aclk) begin
    ul_resetn <= aresetn;
end

hyperloglog_c0_1 hyperloglog_inst (
    .s_axi_control_AWVALID(axi_ctrl.awvalid),
    .s_axi_control_AWREADY(axi_ctrl.awready),
    .s_axi_control_AWADDR(axi_ctrl.awaddr),
    .s_axi_control_WVALID(axi_ctrl.wvalid),
    .s_axi_control_WREADY(axi_ctrl.wready),
    .s_axi_control_WDATA(axi_ctrl.wdata),
    .s_axi_control_WSTRB(axi_ctrl.wstrb),
    .s_axi_control_ARVALID(axi_ctrl.arvalid),
    .s_axi_control_ARREADY(axi_ctrl.arready),
    .s_axi_control_ARADDR(axi_ctrl.araddr),
    .s_axi_control_RVALID(axi_ctrl.rvalid),
    .s_axi_control_RREADY(axi_ctrl.rready),
    .s_axi_control_RDATA(axi_ctrl.rdata),
    .s_axi_control_RRESP(axi_ctrl.rresp),
    .s_axi_control_BVALID(axi_ctrl.bvalid),
    .s_axi_control_BREADY(axi_ctrl.bready),
    .s_axi_control_BRESP(axi_ctrl.bresp),
    .s_axis_host_0_sink_TDATA(axis_host_0_sink.tdata),
    .s_axis_host_0_sink_TKEEP(axis_host_0_sink.tkeep),
    .s_axis_host_0_sink_TID(axis_host_0_sink.tid),
    .s_axis_host_0_sink_TLAST(axis_host_0_sink.tlast),
    .s_axis_host_0_sink_TVALID(axis_host_0_sink.tvalid),
    .s_axis_host_0_sink_TREADY(axis_host_0_sink.tready),
    .m_axis_host_0_src_TDATA(axis_host_0_src.tdata),
    .m_axis_host_0_src_TKEEP(axis_host_0_src.tkeep),
    .m_axis_host_0_src_TID(axis_host_0_src.tid),
    .m_axis_host_0_src_TLAST(axis_host_0_src.tlast),
    .m_axis_host_0_src_TVALID(axis_host_0_src.tvalid),
    .m_axis_host_0_src_TREADY(axis_host_0_src.tready),
    .ap_clk(aclk),
    .ap_rst_n(ul_resetn)
);

endmodule
