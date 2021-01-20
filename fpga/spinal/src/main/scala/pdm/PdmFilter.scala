
package pdm

import spinal.core._
import spinal.lib._

class PdmFilter(nrStages: Int = 4, nrBits: Int = 30, decimation: Int = 12) extends Component 
{
    val io = new Bundle {
        val pdm_dat         = in(Bool)
        val pcm_vld         = out(Bool)
        val pcm             = out(UInt(nrBits bits))
    }

    // A Beginner's Guide To Cascaded Integrator-Comb (CIC) Filters
    // https://www.dsprelated.com/showarticle/1337.php
    //
    // Implements a straightforward CIC filter to bring a 2.4MHz PDM signals down to 48kHz.
    // There is no compensating half-band filter.

    // Differential delay is fixed to 1 (or equal to the decimation rate, before decimation)
    // required nubmer of bits = inputNrBits (=1) + roundUp(nrStages * log2(decimation))
    // 2.4MHz PDM -> 48kHz = 50x decimation
    // 5 stages 
    // nrBits = 1 + (5 * log2Up(50)) = 1 + roundUp(5 * 5.64) = 1 + 29 = 30

    //============================================================
    // CIC Integrators
    //============================================================

    val integrators_output = Reg(UInt(nrBits bits)) init(0)

    val integrators = new Area {
        var input     = UInt(nrBits bits)

        input := (False ## io.pdm_dat).resize(nrBits).asUInt
    
        val stages = for(stageNr <- 0 to nrStages-1) yield new Area {

            val output    = Reg(UInt(nrBits bits)) init(0)
            output        := input + output
            input         = UInt(nrBits bits)
            input         := output

            if (stageNr == nrStages-1)
                integrators_output  := output
        }
    }


/*

By jijingg: 

class IIRCell(dw: Int) extends Component{
  val io = new Bundle{
    val din = in UInt(dw bits)
    val dout = out UInt(dw bits)
  }

  val dinDly = RegNext(io.din) init 0
  io.dout := io.din + dinDly

  def ->(that: IIRCell): IIRCell = {
    that.io.din := this.io.dout
    that
  }
}

class CIC3Stage(diw: Int, dow: Int) extends Component{
  val io  = new Bundle{
    val x = in UInt(diw bits)
    val y = out UInt(dow bits)
  }
  val u0, u1 , u2 = new  IIRCell(dow)

  u0.io.din := io.x.resize(dow)

  u0 -> u1 -> u2

  io.y := u2.io.dout
}

SpinalVerilog(new CIC3Stage(12, 21))


Also: 

class CIC(diw: Int, dow: Int, size: Int) extends Component{
  val io  = new Bundle{
    val x = in UInt(diw bits)
    val y = out UInt(dow bits)
  }
  val uCells = List.fill(size)(new IIRCell(dow))

  uCells.head.io.din := io.x.resize(dow)

  uCells.reduceLeft(_ -> _)

  io.y := uCells.last.io.dout
}

SpinalVerilog(new CIC(12, 21, size = 16))



*/

    //============================================================
    // Decimator
    //============================================================

    val decimator = new Area {
        val decim_cntr = Reg(UInt(log2Up(decimation) bits)) init(0)
        val sample_vld = Bool
    
        when(decim_cntr === 0){
            decim_cntr    := decimation-1
            sample_vld    := True
        }
        .otherwise{
            decim_cntr    := decim_cntr-1
            sample_vld    := False
        }
    }

    //============================================================
    // CIC Combs 
    //============================================================

    val combs_output_vld = Reg(Bool) init(False)
    val combs_output     = Reg(UInt(nrBits bits)) init(0)

    val combs = new Area {

        var input_vld = Bool
        var input     = UInt(nrBits bits)

        input_vld := decimator.sample_vld
        input     := integrators_output

        val stages = for(stageNr <- 0 to nrStages-1) yield new Area {
            var input_dly   = Reg(UInt(nrBits bits)) init(0)
            var output_vld  = Reg(Bool) init(False)
            var output      = Reg(UInt(nrBits bits)) init(0)

            output_vld      := input_vld
            when(input_vld){
                output      := input - input_dly
                input_dly   := input
            }

            input_vld   = Bool
            input       = UInt(nrBits bits)

            input_vld   := output_vld
            input       := output

            if (stageNr == nrStages-1){
                combs_output_vld := output_vld
                combs_output     := output
            }
        }
    }

    io.pcm_vld  := combs_output_vld
    io.pcm      := combs_output

}

