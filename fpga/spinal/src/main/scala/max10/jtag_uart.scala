

package max10

import spinal.core._

class jtag_uart() extends BlackBox{

    val clk_clk             = in(Bool)
    val reset_reset_n       = in(Bool)
    val avbus_chipselect    = in(Bool)
    val avbus_address       = in(Bits(32 bits))
    val avbus_read_n        = in(Bool)
    val avbus_readdata      = out(Bits(32 bits))
    val avbus_write_n       = in(Bool)
    val avbus_writedata     = in(Bits(32 bits))
    val avbus_waitrequest   = out(Bool)

    setDefinitionName("jtag_uart")
}



