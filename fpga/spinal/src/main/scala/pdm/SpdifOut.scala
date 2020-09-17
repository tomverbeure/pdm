
package pdm

import spinal.core._
import spinal.lib._


// Clock domain is expected to be 128x sample rate * some division ratio
// For example, if sample rate is 48kHz, then the input clock should be at least 6.144MHz,
// or an integer factor higher.


case class AudioIntfcConfig(
    maxNrChannels       : Int,
    maxNrBitsPerSample  : Int
) { }

class SpdifOut(audioIntfcConfig: AudioIntfcConfig, clkDivRatio : Int = 1) extends Component 
{
    val io = new Bundle {
        val spdif               = out(Bool)

        val audio_samples_rdy   = out(Bool)
        val audio_samples       = in(Vec(SInt(audioIntfcConfig.maxNrBitsPerSample bits), audioIntfcConfig.maxNrChannels))
    }

    val clk_div_cntr      = Counter(clkDivRatio, True)
    val time_slot_cntr    = Counter(64, clk_div_cntr.willOverflow)          // 64 instead of 32 because each bit takes 2 cycles
    val subframe_cntr     = Counter(audioIntfcConfig.maxNrChannels, time_slot_cntr.willOverflow)
    val frame_cntr        = Counter(192, subframe_cntr.willOverflow)

    val audio_samples_rdy   = Reg(Bool) init(False)
    val audio_samples       = Reg(io.audio_samples)

    audio_samples_rdy   := False
    when(clk_div_cntr === 0){
        when(subframe_cntr === 0 && time_slot_cntr === 0){
            // Grab the new sample
            audio_samples_rdy       := True
            audio_samples           := io.audio_samples
        }
    }

    val b_preamble  = B"11101000".asBools.reverse.asBits
    val m_preamble  = B"11100010".asBools.reverse.asBits
    val w_preamble  = B"11100100".asBools.reverse.asBits

    val preamble    =  (subframe_cntr =/= 0) ? w_preamble | (
                       (frame_cntr === 0)    ? b_preamble | 
                                               m_preamble )

    val spdif_out       = Reg(Bool) init(False)

    val sample_data     = audio_samples(subframe_cntr) ## B"0".resize(24-audioIntfcConfig.maxNrBitsPerSample)
    val valid_flag_     = False
    val user_data       = False
    val channel_status  = True
    val non_parity_data = channel_status ## user_data ## valid_flag_ ## sample_data
    val parity          = non_parity_data.xorR

    val output_data     = parity ## non_parity_data ## B"0000"

    when(clk_div_cntr === 0){
        when(time_slot_cntr < 2*4){
            spdif_out   := preamble(time_slot_cntr(2 downto 0))
        }
        .otherwise{
            // always invert on the first tick of a time slot. Only invert on second tick
            // when bit value is True.
            spdif_out   := (!time_slot_cntr(0)) ? !spdif_out | (spdif_out ^ (output_data >> (time_slot_cntr >> 1))(0))
        }
    }

    io.spdif              := spdif_out
    io.audio_samples_rdy  := audio_samples_rdy
}

//object MySpinalConfig extends SpinalConfig(defaultConfigForClockDomains = ClockDomainConfig(resetKind = SYNC))

//Generate the MyTopLevel's Verilog using the above custom configuration.
object SpdifVerilog{
    def main(args: Array[String]) {
        SpinalConfig(defaultConfigForClockDomains = ClockDomainConfig(resetKind = SYNC)).generateVerilog(new SpdifOut(AudioIntfcConfig(2, 16)))
    }
}
