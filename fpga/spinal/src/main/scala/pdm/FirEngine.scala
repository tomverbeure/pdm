
package pdm

import scala.collection.mutable.ArrayBuffer

import spinal.core._
import spinal.lib._

case class FirFilterInfo( 
        name                : String, 
        dataBufSize         : Int, 
        isHalfBand          : Boolean,
        coefs               : Array[Int]
    )
{
}

case class FirEngineInfoHW() extends Bundle {


}

case class FirEngineConfig(
          filters       : Array[FirFilterInfo],
          nrDataBits    : Int,
          nrCoefBits    : Int
    )
{
    // Coefficients are tightly packed one after the other in RAM,
    // so simply add length of each coefficient array together.
    def totalNrCoefs    = filters.foldLeft(0){_ + _.coefs.length}
    def maxDataBufAddr  = dataBufStopAddrs.foldLeft(0)((m,f) => ( if (f > m) f else m ))

    def coefBufStartAddrs    = filters.scanLeft(0){ _ + _.coefs.length }
    def dataBufStartAddrs    = filters.scanLeft(0){ _ + _.dataBufSize }
    def dataBufStopAddrs     = filters.scanLeft(filters(0).dataBufSize){ _ + _.dataBufSize}

/*
    FIXME: these 2 don't work due to some conflict between Scala and SpinalHDL
    //def maxDataAddr  = filters.foldLeft(0){_.max(_.dataBufStopAddr)}
    def maxDataAddr : Int = {
        val maxAddr : Int = 0
        filters.foreach{
            maxAddr.scala.runtime.RichInt.max(Int(_.dataBufStopAddr)) 
        }

        maxAddr
    }
    */

    def nrMemDataBits = nrDataBits.max(nrCoefBits)
    def nrMemAddrs    = maxDataBufAddr + 1 + totalNrCoefs

    def allCoefs = filters.foldLeft(ArrayBuffer[Int](0)){ _ ++ _.coefs }

    def memInit : Array[SInt] = {
        val l = ArrayBuffer[SInt]()

        allCoefs.foreach({ l.append(_) }) 
        (0 to maxDataBufAddr).foreach({ _ => l.append(0) })
        l.toArray
   }

   def toFirEngingINfoHW : FirEngineInfoHW = {
      
      val feiHW = FirEngineInfoHW()

      feiHW
   }
}

class FirEngine(conf: FirEngineConfig) extends Component
{
    val io = new Bundle {
        val data_in           = slave(Stream(SInt(conf.nrDataBits bits)))
        val data_out          = master(Stream(SInt(conf.nrDataBits bits)))
    }

    printf("totalNrCoefs: %d\n", conf.totalNrCoefs)
    printf("maxDataBufAddr: %d\n",  conf.maxDataBufAddr)
    printf("nrMemAddrs: %d\n",  conf.nrMemAddrs)

    val memSize = conf.maxDataBufAddr + 1 + conf.totalNrCoefs

    val u_mem = Mem(SInt(conf.nrMemDataBits bits), conf.memInit)

    io.data_out.payload  := u_mem.readSync(io.data_in.payload.asUInt.resize(log2Up(conf.nrMemAddrs))).resize(conf.nrDataBits)

}
