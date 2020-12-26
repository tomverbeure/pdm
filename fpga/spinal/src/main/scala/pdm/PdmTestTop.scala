
package pdm

import scala.collection.mutable.ArrayBuffer

import spinal.core._
import spinal.lib._
import spinal.lib.io._
import spinal.lib.bus.misc._
import spinal.lib.bus.amba3.apb._
import spinal.lib.com.uart._
import spinal.lib.com.i2c._

import max10._

class PdmTestTop() extends Component 
{
    val io = new Bundle {

        val osc_clk_in      = in(Bool)

        val pdm_clk         = out(Bool)
        val pdm_sel         = out(Bool)
        val pdm_dat         = in(Bool)

        val led0            = out(Bool)
        val led1            = out(Bool)
        val led2            = out(Bool)
        val led3            = out(Bool)
        val led4            = out(Bool)

    }

    io.pdm_sel    := False
    io.led3       := True

    noIoPrefix()

    val clk_pdm       = Bool
    val clk_cpu       = Bool
    val clk_calc      = Bool
    val clk_spdif     = Bool

    val u_pll = new pll()
    u_pll.inclk0          <> io.osc_clk_in
    u_pll.c0              <> clk_pdm    
    u_pll.c1              <> clk_cpu    
    u_pll.c2              <> clk_calc    
    u_pll.c3              <> clk_spdif    

    //============================================================
    // Create clk pdm 
    //============================================================
    
    val clkPdmRawDomain = ClockDomain(
        clock       = clk_pdm,
        frequency   = FixedFrequency(2.4 MHz),
        config      = ClockDomainConfig(
            resetKind = BOOT
        )
    )

    val clk_pdm_reset_  = Bool

    val clk_pdm_reset_gen = new ClockingArea(clkPdmRawDomain) {
        val reset_unbuffered_ = True

        val reset_cntr = Reg(UInt(5 bits)) init(0)
        when(reset_cntr =/= U(reset_cntr.range -> true)){
            reset_cntr := reset_cntr + 1
            reset_unbuffered_ := False
        }

        clk_pdm_reset_ := RegNext(reset_unbuffered_)
    }


    val clkPdmDomain = ClockDomain(
        clock       = clk_pdm,
        reset       = clk_pdm_reset_,
        frequency   = FixedFrequency(2.4 MHz),
        config      = ClockDomainConfig(
            resetKind = SYNC,
            resetActiveLevel = LOW
        )
    )

    //============================================================
    // Create clk cpu 
    //============================================================
    
    val clkCpuRawDomain = ClockDomain(
        clock       = clk_cpu,
        frequency   = FixedFrequency(2.4 MHz),
        config      = ClockDomainConfig(
            resetKind = BOOT
        )
    )

    val clk_cpu_reset_  = Bool

    val clk_cpu_reset_gen = new ClockingArea(clkCpuRawDomain) {
        val reset_unbuffered_ = True

        val reset_cntr = Reg(UInt(5 bits)) init(0)
        when(reset_cntr =/= U(reset_cntr.range -> true)){
            reset_cntr := reset_cntr + 1
            reset_unbuffered_ := False
        }

        clk_cpu_reset_ := RegNext(reset_unbuffered_)
    }


    val clkCpuDomain = ClockDomain(
        clock       = clk_cpu,
        reset       = clk_cpu_reset_,
        frequency   = FixedFrequency(50 MHz),
        config      = ClockDomainConfig(
            resetKind = SYNC,
            resetActiveLevel = LOW
        )
    )

    //============================================================
    // Create clk calc 
    //============================================================
    
    val clkCalcRawDomain = ClockDomain(
        clock       = clk_calc,
        frequency   = FixedFrequency(2.4 MHz),
        config      = ClockDomainConfig(
            resetKind = BOOT
        )
    )

    val clk_calc_reset_ = Bool

    val clk_calc_reset_gen = new ClockingArea(clkCalcRawDomain) {
        val reset_unbuffered_ = True

        val reset_cntr = Reg(UInt(5 bits)) init(0)
        when(reset_cntr =/= U(reset_cntr.range -> true)){
            reset_cntr := reset_cntr + 1
            reset_unbuffered_ := False
        }

        clk_calc_reset_ := RegNext(reset_unbuffered_)
    }


    val clkCalcDomain = ClockDomain(
        clock       = clk_calc,
        reset       = clk_calc_reset_,
        frequency   = FixedFrequency(2.4 MHz),
        config      = ClockDomainConfig(
            resetKind = SYNC,
            resetActiveLevel = LOW
        )
    )

    //============================================================
    // Create spdif clk
    //============================================================
    
    val clkSpdifRawDomain = ClockDomain(
        clock       = clk_spdif,
        frequency   = FixedFrequency(6.144 MHz),
        config      = ClockDomainConfig(
            resetKind = BOOT
        )
    )

    val clk_spdif_reset_ = Bool

    val clk_spdif_reset_gen = new ClockingArea(clkSpdifRawDomain) {
        val reset_unbuffered_ = True

        val reset_cntr = Reg(UInt(5 bits)) init(0)
        when(reset_cntr =/= U(reset_cntr.range -> true)){
            reset_cntr := reset_cntr + 1
            reset_unbuffered_ := False
        }

        clk_spdif_reset_ := RegNext(reset_unbuffered_)
    }


    val clkSpdifDomain = ClockDomain(
        clock       = clk_spdif,
        reset       = clk_spdif_reset_,
        frequency   = FixedFrequency(2.4 MHz),
        config      = ClockDomainConfig(
            resetKind = SYNC,
            resetActiveLevel = LOW
        )
    )

    //============================================================
    // CPU
    //============================================================

    val cpu = new ClockingArea(clkCpuDomain) {
        val u_cpu = new CpuTop()
        u_cpu.io.led_red        <> io.led0
        u_cpu.io.led_green      <> io.led1
        u_cpu.io.led_blue       <> io.led2
    }

    //============================================================
    // PDM
    //============================================================

    io.pdm_clk    := clk_pdm

    val pdm =new ClockingArea(clkPdmDomain) {

        val u_pdm_filter = new PdmFilter()
        u_pdm_filter.io.pdm_dat     <> io.pdm_dat

    }

    //============================================================
    // FirEngine
    //============================================================


    val fir = new ClockingArea(clkCpuDomain) {

        val firs = ArrayBuffer[FirFilterInfo]()

        firs += FirFilterInfo("HB1",    0,  63, true,  Array[Int](1,2,3,4,5,6,7,8,9)) 
        firs += FirFilterInfo("HB2",   64, 127, true,  Array[Int](1,2,3,4,5)) 
        firs += FirFilterInfo("FIR",  128, 192, false, Array[Int](1,2,3)) 

        val conf = FirEngineConfig(
            firs.toArray, 
            16,
            18
          )

        val u_fir_engine = new FirEngine(conf)
        u_fir_engine.io.data_in.valid     := False
        u_fir_engine.io.data_in.payload   := 0
        u_fir_engine.io.data_out.ready    := True
    }

    //============================================================
    // SPDIF
    //============================================================

    val spdif = new ClockingArea(clkSpdifDomain) {
        val calc_next_sample      = Bool
        val sample                = SInt(16 bits)
        val audio_samples         = Vec(SInt(16 bits), 2)


        val u_spdif_out = new SpdifOut(AudioIntfcConfig(maxNrChannels = 2, maxNrBitsPerSample = 16), clkDivRatio = 1)
        u_spdif_out.io.spdif                <> io.led4
        u_spdif_out.io.audio_samples_rdy    <> calc_next_sample
        u_spdif_out.io.audio_samples        <> audio_samples

        val waveform_cntr = Reg(UInt(log2Up(48) bits)) init(0)
        when(calc_next_sample){
            waveform_cntr   := (waveform_cntr =/= 47) ? (waveform_cntr + 1) | 0
        }

        sample    := (waveform_cntr <= 24) ? S(-8000, 16 bits) | S(8000, 16 bits)
        audio_samples(0) := sample
        audio_samples(1) := sample

    }

}


object PdmTestTopVerilogSim {
    def main(args: Array[String]) {

        val config = SpinalConfig(anonymSignalUniqueness = true)

        config.generateVerilog({
            val toplevel = new PdmTestTop()
            InOutWrapper(toplevel)
        })

    }
}

object PdmTestTopVerilogSyn {
    def main(args: Array[String]) {

        val config = SpinalConfig(anonymSignalUniqueness = true)
        config.generateVerilog({
            val toplevel = new PdmTestTop()
            InOutWrapper(toplevel)
            toplevel
        })
    }
}

//Define a custom SpinalHDL configuration with synchronous reset instead of the default asynchronous one. This configuration can be resued everywhere
object MySpinalConfig extends SpinalConfig(defaultConfigForClockDomains = ClockDomainConfig(resetKind = SYNC))


//Generate the MyTopLevel's Verilog using the above custom configuration.
object PdmTestTopVerilogWithCustomConfig {
    def main(args: Array[String]) {
        MySpinalConfig.generateVerilog(new PdmTestTop)
    }
}
