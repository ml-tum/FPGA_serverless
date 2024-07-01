`timescale 1ns / 1ps

module md5_brute(
    input logic aclk,
    input logic aresetn,
    input wire start,
    input wire [127:0] find_hash,
    output reg [63:0] result,
    output reg stop
    );
    
localparam D = 5; // digits
localparam MAX_VALUE = 1073741823; // = 64^5-1

reg [D*6:0] ctr;
reg running;

reg [511:0] md5_in;

genvar i;
for (i = 0; i < D; i++) begin: loop
    always_comb begin
        if(ctr[i*6+:6] <= 9)
            md5_in[(D-1-i)*8+:8] = 8'h30 + ctr[i*6+:6];
        else if (ctr[i*6+:6] <= 35)
            md5_in[(D-1-i)*8+:8] = 8'h41 + (ctr[i*6+:6]-10);
        else if (ctr[i*6+:6] <= 61)
            md5_in[(D-1-i)*8+:8] = 8'h61 + (ctr[i*6+:6]-36);
        else if (ctr[i*6+:6] == 62)
            md5_in[(D-1-i)*8+:8] = 8'h2d;
        else 
            md5_in[(D-1-i)*8+:8] = 8'h5f;
    end
end

always_comb begin
    md5_in[447:40] = 'b10000000;
    md5_in[511:448] = D*8;
end

wire [31:0] md5_a;
wire [31:0] md5_b;
wire [31:0] md5_c;
wire [31:0] md5_d;
wire [127:0] md5_out_hash = {md5_d + 32'h10325476, md5_c + 32'h98badcfe, md5_b + 32'hefcdab89, md5_a + 32'h67452301};
wire [127:0] md5_out_swap = {<<8{md5_out_hash}};


always @(posedge aclk) begin
    if (~aresetn) begin
        running <= 0;
    end else begin
        if (start) begin
            ctr <= 0;
            running <= 1;
        end
    end

    stop <= 0;

    if (running) begin
        if (md5_out_swap==find_hash) begin
            running <= 0;
            result <= ctr-64;
            stop <= 1;
        end else if (ctr==MAX_VALUE) begin
            running <= 0;
            result <= MAX_VALUE+1;
            stop <= 1;
        end else begin
            ctr <= ctr+1;
        end
    end
end
    
Md5Core m (
    .clk(aclk),
    .wb(md5_in),
    .a0('h67452301),
    .b0('hefcdab89),
    .c0('h98badcfe),
    .d0('h10325476),
    .a64(md5_a),
    .b64(md5_b),
    .c64(md5_c),
    .d64(md5_d)
);
    
endmodule
