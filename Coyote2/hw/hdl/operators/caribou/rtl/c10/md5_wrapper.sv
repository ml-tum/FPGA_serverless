`timescale 1ns / 1ps


module md5_wrapper(
    input aclk,
    input aresetn,
    
    AXI4SR.s                 axis_in,
    AXI4SR.m                 axis_out
    );


assign axis_in.tready = aresetn;

assign axis_out.tlast = 1'b1;
assign axis_out.tkeep = 64'hffffffffffffffff;
assign axis_out.tid = 0;


wire start = axis_in.tvalid && axis_in.tready;
wire [127:0] find_hash = axis_in.tdata[127:0];

wire stop;
wire [63:0] result;

always @(posedge aclk) begin
    if (~aresetn) begin
        axis_out.tvalid <= 0;
        axis_out.tdata[511:0] <= 0;
    end else begin
        if (stop) begin
            axis_out.tvalid <= 1;
            axis_out.tdata[511:64] <= 0;
            axis_out.tdata[63:0] <= result;
        end

        if(axis_out.tvalid && axis_out.tready) begin
            axis_out.tvalid <= 0;
            axis_out.tdata[511:0] <= 0;
        end
    end
end

md5_brute mb (
    .aclk(aclk),
    .aresetn(aresetn),
    .start(start),
    .find_hash(find_hash),
    .result(result),
    .stop(stop)
);

endmodule
