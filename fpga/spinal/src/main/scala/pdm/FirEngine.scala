
package pdm

import spinal.core._
import spinal.lib._

case class FirFilterInfo( 
        name                : String, 
        dataBufStartAddr    : Int, 
        dataBufStopAddr     : Int, 
        isHalfBand          : Boolean,
        coefs               : Array[Int]
    )
{
}

case class FirEngineConfig(
          filters       : Array[FirFilterInfo],
          nrDataBits    : Int,
          nrCoefBits    : Int
    )
{
    // Coefficients are tightly packed one after the other in RAM,
    // so simply add length of each coefficient array together.
    def totalNrCoefs = filters.foldLeft(0){_ + _.coefs.length}
/*
    //def maxDataAddr  = filters.foldLeft(0){_.max(_.dataBufStopAddr)}
    def maxDataAddr : Int = {
        val maxAddr = 0
        filters.foreach{
            maxAddr.max(Int(_.dataBufStopAddr)) 
        }

        maxAddr
    }
*/
}

class FirEngine(conf: FirEngineConfig) extends Component
{
    val io = new Bundle {
        val data_in           = slave(Stream(SInt(conf.nrDataBits bits)))
        val data_out          = master(Stream(SInt(conf.nrDataBits bits)))
    }

    printf("totalNrCoefs: %d\n", conf.totalNrCoefs)
//    printf("maxDataAddr: %d\n",  conf.maxDataAddr)

/*
    val memSize = 


    val u_mem = Mem(
*/

}
