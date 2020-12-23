
package pdm

import spinal.core._
import spinal.lib._

case class FirFilterInfo( 
        isHalfBand          : Boolean,
        nrCoefs             : Int, 
        dataBufStartAddr    : Int, 
        dataBufStopAddr     : Int, 
        coefBufStartAddr    : Int 
    )
{
}

case class FirEngineConfig(
          filters       : Array[FirFilterInfo],
          nrDataBits    : Int,
          nrCoefBits    : Int
    )
{
}

class FirEngine(conf: FirEngineConfig) extends Component
{
    val io = new Bundle {
        val data_in           = slave(Stream(SInt(conf.nrDataBits bits)))
    }
}
