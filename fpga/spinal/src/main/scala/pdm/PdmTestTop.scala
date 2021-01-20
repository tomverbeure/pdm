
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

class PdmTestTop(isSim: Boolean) extends Component 
{
    val io = new Bundle {

        val osc_clk_in      = in(Bool)

        val pdm_clk         = out(Bool)
        val pdm_sel         = out(Bool)
        val pdm_dat         = in(Bool)

        val spdif_out       = out(Bool)

        val led0            = out(Bool)
    }

    io.pdm_sel    := False

    noIoPrefix()

    // Clock architecture:
    // osc_clk_in (50MHz or 25MHz depending on source) -> PLL -> 18.432 MHz = clk_audio_max
    // 18.432MHz / 8 = 2.304 MHz: clk_pdm:   goes to output as and drives the CIC filter
    // 18.432MHz / 3 = 6.144 MHz: clk_spdif: drives the SPDIF output interface, which needs a clock 
    //                                       that's 128x higher than the sample rate
    // osc_clk_in (50MHz or 25MHz depending on source) -> PLL -> 92.16 MHz = clk_calc
    //                      drives the FIR filter
    // osc_clk_in (50MHz or 25MHz depending on source) -> PLL -> 46.08 MHz = clk_cpu

    val clk_audio_max = Bool
    val clk_pdm       = Bool
    val clk_cpu       = Bool
    val clk_calc      = Bool
    val clk_spdif     = Bool

    if (isSim) new Area {
        clk_audio_max := io.osc_clk_in
        clk_calc      := io.osc_clk_in
        clk_cpu       := io.osc_clk_in
    }
    else{

        val u_pll = new pll()
        u_pll.io.inclk0          <> io.osc_clk_in
        u_pll.io.c0              <> clk_audio_max       // 18.432 MHz
        u_pll.io.c1              <> clk_calc            // 92.16 Mhz
        u_pll.io.c2              <> clk_cpu             // 46.08 MHz
    }

    //============================================================
    // Create clk audio max 
    //============================================================

    val clkAudioMaxRawDomain = ClockDomain(
        clock       = clk_audio_max,
        frequency   = FixedFrequency(18.432 MHz),
        config      = ClockDomainConfig(
            resetKind = BOOT
        )
    )

    val clk_audio_max_reset_  = Bool

    val clk_audio_max_reset_gen = new ClockingArea(clkAudioMaxRawDomain) {
        val reset_unbuffered_ = True

        val reset_cntr = Reg(UInt(5 bits)) init(0)
        when(reset_cntr =/= U(reset_cntr.range -> true)){
            reset_cntr := reset_cntr + 1
            reset_unbuffered_ := False
        }

        clk_audio_max_reset_ := RegNext(reset_unbuffered_)
    }

    val clkAudioMaxDomain = ClockDomain(
        clock       = clk_audio_max,
        reset       = clk_audio_max_reset_,
        frequency   = FixedFrequency(18.432 MHz),
        config      = ClockDomainConfig(
            resetKind = ASYNC,
            resetActiveLevel = LOW
        )
    )

    //============================================================
    // Create clk pdm 
    //============================================================

    val clk_pdm_reset_  = Bool

    val pdm_raw = new ClockingArea(clkAudioMaxDomain) {
        val pdm_div_cntr = Counter(0, if (isSim) 15 else 7)
        pdm_div_cntr.increment()
        clk_pdm   := pdm_div_cntr < (if (isSim) 8 else 4)

        val reset_cntr = Reg(UInt(3 bits)) init(0)
        when(pdm_div_cntr === 0){
            when(reset_cntr =/= U(reset_cntr.range -> true)){
                reset_cntr := reset_cntr + 1
            }
        }
        clk_pdm_reset_ := RegNext(reset_cntr === U(reset_cntr.range->true))
    }
    
    val clkPdmDomain = ClockDomain(
        clock       = clk_pdm,
        reset       = clk_pdm_reset_,
        frequency   = FixedFrequency(2.304 MHz),
        config      = ClockDomainConfig(
            resetKind = ASYNC,
            resetActiveLevel = LOW
        )
    )

    //============================================================
    // Create clk spdif 
    //============================================================

    val clk_spdif_reset_  = Bool

    val spdif_raw = new ClockingArea(clkAudioMaxDomain) {
        val spdif_div_cntr = Counter(0, if (isSim) 5 else 2)
        spdif_div_cntr.increment()
        clk_spdif   := spdif_div_cntr < 1

        val reset_cntr = Reg(UInt(3 bits)) init(0)
        when(spdif_div_cntr === 0){
            when(reset_cntr =/= U(reset_cntr.range -> true)){
                reset_cntr := reset_cntr + 1
            }
        }

        clk_spdif_reset_ := RegNext(reset_cntr === U(reset_cntr.range -> true))
    }
    
    val clkSpdifDomain = ClockDomain(
        clock       = clk_spdif,
        reset       = clk_spdif_reset_,
        frequency   = FixedFrequency(6.144 MHz),
        config      = ClockDomainConfig(
            resetKind = ASYNC,
            resetActiveLevel = LOW
        )
    )

    /*
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
            resetKind = ASYNC,
            resetActiveLevel = LOW
        )
    )
    */

    //============================================================
    // Create clk calc 
    //============================================================
    
    val clkCalcRawDomain = ClockDomain(
        clock       = clk_calc,
        frequency   = FixedFrequency(92.16 MHz),
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
        frequency   = FixedFrequency(92.16 MHz),
        config      = ClockDomainConfig(
            resetKind = ASYNC,
            resetActiveLevel = LOW
        )
    )

/*
    //============================================================
    // CPU
    //============================================================

    val cpu = new ClockingArea(clkCpuDomain) {
        val u_cpu = new CpuTop()
        u_cpu.io.led_red        <> io.led0
        u_cpu.io.led_green      <> io.led1
        u_cpu.io.led_blue       <> io.led2
    }
    */


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


    val fir = new ClockingArea(clkCalcDomain) {

        val firs = ArrayBuffer[FirFilterInfo]()

        firs += FirFilterInfo("HB1",  true,  2, Array[Int](1,2,3,4,5,6,7,8,9)) 
        firs += FirFilterInfo("HB2",  true,  2, Array[Int](1,2,3,4,5)) 
        firs += FirFilterInfo("FIR",  false, 1, Array[Int](1,2,3)) 

        val conf = FirEngineConfig(
            firs.toArray, 
            16,
            18
          )

        val u_fir_engine = new FirEngine(conf)
        u_fir_engine.io.data_in.valid     := False
        u_fir_engine.io.data_in.payload   := 0
    }

    //============================================================
    // SPDIF
    //============================================================

    val spdif = new ClockingArea(clkSpdifDomain) {
        val calc_next_sample      = Bool
        val sample                = SInt(16 bits)
        val audio_samples         = Vec(SInt(16 bits), 2)


        val u_spdif_out = new SpdifOut(AudioIntfcConfig(maxNrChannels = 2, maxNrBitsPerSample = 16), clkDivRatio = 1)
        u_spdif_out.io.audio_samples_rdy    <> calc_next_sample
        u_spdif_out.io.audio_samples        <> audio_samples

        io.led0       := u_spdif_out.io.spdif
        io.spdif_out  := u_spdif_out.io.spdif

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
            val toplevel = new PdmTestTop(isSim = true)
            InOutWrapper(toplevel)
        })

    }
}

object PdmTestTopVerilogSyn {
    def main(args: Array[String]) {

        val config = SpinalConfig(anonymSignalUniqueness = true)
        config.generateVerilog({
            val toplevel = new PdmTestTop(isSim = false)
            InOutWrapper(toplevel)
            toplevel
        })
    }
}

