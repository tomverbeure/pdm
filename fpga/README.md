
# Architecture

Clocks:
    * PDM clock -> 2.304MHz
    * Main clock: 
        * PDM clock * 40 -> 92.16MHz
        * alternative: different multiplier or whatever clock with separate PLL
* CIC filter: straightforward implementation. Use FFs, adders etc.
    * 16-bit result gets stored into a FIFO
* Fir filters: 
    * all done with the same sequencer
    * Coefficient RAM
        * 18-bit wide
        * has coefficients for all FIR filters
        * 50% of the coefficients: all filters are symmetric
        * HB: 
            * x taps -> x/2 +1 non-zero taps -> (x/2+1)/2+1 coefficients
            * split 0.5 center coefficient into 2 0.25 coefficients?
        * HB1: 11 taps ->  7 nz taps ->  4 coefficients
        * HB2: 19 taps -> 10 nz taps ->  6 coefficients
        * FIR: 51 taps               -> 26 coefficients
        * total: 36 coefficients
        * 18 bits per coefficient   
    * Data RAM
        * HB1: 11 taps
        * HB2: 19 taps
        * FIR: 51 taps
        * Total: 81 taps
        * 16 bits per coefficient?
    
FPGA ECP5:
* DSP: 
    * 18x18 signed num
    * 36 accum
* BRAM: 
    * 1024x18 
    * 512x36   -> could be used for 2 channels at a time

All FIRs:

    * Parameters per FIR:
        Fixed:
        * data_buf_start
        * data_buf_stop
        * coef_buf_start

        Variable:
        * data_buf_wr_cur_ptr
        * data_buf_rd_start_ptr
        * data_buf_rd_cur_ptr
        * coef_buf_cur_ptr
        * data_buf_next_wr_cur_ptr

    * Cycle -1:
        Only for first filter:
        * Wait for data in FIFO
        * Read from FIFO, write to Write Pointer
        * Pop CIC FIFO
        * WritePointer = (Write Pointer+1)%buf_size

    * Cycle 0:
        Only for first filter:
        * Wait for data in FIFO
        * Read from FIFO, write to Write Pointer
        * Pop CIC FIFO
        * WritePointer = (Write Pointer+1)%buf_size

        For all filters:
        * Read from Read Pointer
        * Read Pointer = (Read Pointer+HB?2:1)%buf_size
        * Read Coef Pointer
        * Coef Pointer += 1
    * Cycle 1-(n-2):
        * Read from Read Pointer
        * Read Pointer = (Read Pointer+HB?2:1)%buf_size
        * Read Coef Pointer
        * Coef Pointer += 1
    * Cycle n-1:
        * Read from Read Pointer
        * Read Pointer = Start of Read Pointer
        * Start of Read Pointer
        * Read Coef Pointer
        * Coef Pointer = 0
    * Cycle n:
        * Wait cycle to allow DSP to update
    * Cycle n+1:
        * Write DSP accum to out data_buf_next_wr_cur_ptr
        * data_buf_next_wr_cur_ptr

