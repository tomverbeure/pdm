
module tb;

    reg clk, reset;
    reg io_data_in_valid;
    reg [15:0] io_data_in_payload;
    wire io_data_in_ready;

    initial begin
        reset   <= 1'b1;
        clk     <= 1'b0;

        repeat(10) #10 clk <= !clk;

        reset   <= 1'b0;

        repeat(10000) #10 clk <= !clk;
    end

    initial begin
        $dumpfile("tb_v.vcd");
        $dumpvars(0);
    end

    initial begin
        io_data_in_valid            <= 1'b0;
        io_data_in_payload          <= 0;

        repeat(100)
            @(posedge clk);

        forever begin

            repeat(42) @(posedge clk) begin
                if (io_data_in_ready) begin
                    io_data_in_valid        <= 1'b0;
                    io_data_in_payload      <= 0;
                end
            end

            io_data_in_valid        <= 1'b1;
            io_data_in_payload      <= 4096;

        end
    end

    FirEngine u_fe(
        .clk(clk),
        .reset(reset),
        .io_data_in_valid(io_data_in_valid),
        .io_data_in_payload(io_data_in_payload),
        .io_data_in_ready(io_data_in_ready)
    );

endmodule
