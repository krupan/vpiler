`timescale 1ns/1ns

module counter (
  input clk, reset,
  output logic [7:0] count
);
  always @(posedge clk)
    if (reset) begin
      count <= '0 ;
    end
    else begin
      count <= count + 1;
    end
endmodule

module counter_tb;
  localparam CLOCK_PERIOD = 10ns;
  bit clk;
  bit reset;
  bit[7:0] count;

  counter dut(.clk(clk),
              .reset(reset),
              .count(count));

  task run_clock;
    for(int i = 0; i < 10; i++) begin
      clk <= 0;
      #(CLOCK_PERIOD / 2ns);
      clk <= 1;
      #(CLOCK_PERIOD / 2ns);
    end
  endtask

  initial begin
    fork
      run_clock;
      begin
        localparam EXPECTED_COUNT = 5;

        // hold reset high for a few clocks
        reset <= 1;
        #(CLOCK_PERIOD * 3ns);
        reset <= 0;

        // do some counting
        #(CLOCK_PERIOD * EXPECTED_COUNT);

        // check results
        if(count == EXPECTED_COUNT) begin
          $display("Counter test passed");
        end
        else begin
          $display("Counter test FAILED!");
        end
      end
    join
  end
endmodule
