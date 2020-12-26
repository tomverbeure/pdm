
package max10

import spinal.core._

class pll() extends BlackBox{

    val io = new Bundle {
    	val inclk0            = in(Bool)
    	val c0                = out(Bool)
    	val c1                = out(Bool)
    	val c2                = out(Bool)
    	val c3                = out(Bool)
    }

    noIoPrefix()
    setDefinitionName("pll")
}



