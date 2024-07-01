`timescale 1ns / 1ps

module sha256_wrapper (
    input wire aclk,
    input wire aresetn,
    AXI4SR.s axis_in,
    AXI4SR.m axis_out
);

wire[511:0] tdata_in_rev;

wire [255:0] digest_o;
wire digest_valid_o;
reg await_result;

sha256_stream sha256_inst (
    .clk(aclk),
    .rst(~aresetn),
    .mode(1'b1),
    .s_tdata_i(tdata_in_rev),
    .s_tlast_i(axis_in.tlast),
    .s_tvalid_i(axis_in.tvalid),
    .s_tready_o(axis_in.tready),
    .digest_o(digest_o),
    .digest_valid_o(digest_valid_o)
);

genvar i;
generate
    for(i=0; i<64; i++) begin
        assign tdata_in_rev[i*8+:8] = axis_in.tdata[(63-i)*8+:8];
    end
endgenerate 

always_ff @(posedge aclk) begin
    if(~aresetn) begin
        await_result <= 0;
        axis_out.tvalid <= 1'b0;
        axis_out.tid <= 0;
        axis_out.tlast <= 1'b1;
        axis_out.tkeep <= 64'h00000000ffffffff;
    end else begin
        if(axis_in.tlast && axis_in.tvalid && axis_in.tready) begin
            await_result <= 1'b1;
            
        end else if(await_result && digest_valid_o) begin
            await_result <= 1'b0;
            axis_out.tvalid <= 1'b1;
            axis_out.tdata <= {digest_o, digest_o};
            
        end else if(axis_out.tready && axis_out.tvalid) begin
            axis_out.tvalid <= 1'b0;
        end
    end
end
   
endmodule
