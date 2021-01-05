
package pdm

import scala.collection.mutable.ArrayBuffer

import spinal.core._
import spinal.lib._

case class FirFilterInfo( 
        name                : String, 
        dataBufSize         : Int, 
        isHalfBand          : Boolean,
        decimationRatio     : Int,
        coefs               : Array[Int]
    )
{
}

case class FirFilterFixedInfoHW(conf: FirEngineConfig, idx: Int) extends Bundle 
{
    val data_buf_start_addr       = UInt(conf.nrMemAddrBits bits)
    val data_buf_stop_addr        = UInt(conf.nrMemAddrBits bits)

    val coef_buf_start_addr       = UInt(conf.nrMemAddrBits bits)
    val coef_buf_stop_addr        = UInt(conf.nrMemAddrBits bits)

    val is_halfband               = Bool

}

// Operation:
// For each filter stage, there's a counter that counts the number of new samples that have been
// stored in its input buffer.
// For the first stage, the new samples are coming in from the input interface.
// When the necessary number of samples have arrived for the first stage, the FSM kicks in and starts
// calcating.

case class FirEngineConfig(
          filters       : Array[FirFilterInfo],
          nrDataBits    : Int,
          nrCoefBits    : Int
    )
{
    // Coefficients are tightly packed one after the other in RAM,
    // so simply add length of each coefficient array together.
    def totalNrCoefs          = filters.foldLeft(0){_ + _.coefs.length}
    def maxNrCoefs            = filters.foldLeft(0)((m,f) => ( if (f.coefs.size > m) f.coefs.size else m ))

    def maxDataBufAddr        = dataBufStopAddrs.foldLeft(0)((m,f) => ( if (f > m) f else m ))

    def coefBufStartAddrs     = filters.scanLeft( 0) { _ + _.coefs.length }.dropRight(1)
    def coefBufStopAddrs      = filters.scanLeft(-1) { _ + _.coefs.length }.drop(1)

    def dataBufStartAddrs     = filters.scanLeft( 0) { _ + _.dataBufSize }.dropRight(1)
    def dataBufStopAddrs      = filters.scanLeft(-1) { _ + _.dataBufSize }.drop(1)

    def maxDecimationRatio    = filters.foldLeft(0)((m,f) => ( if (f.decimationRatio > m) f.decimationRatio else m ))
    def totalDecimationRatio  = filters.foldLeft(1){ _ * _.decimationRatio } 

    def filterOrders          = filters.scanLeft(0)((m,f) => ( if (f.isHalfBand) (f.coefs.length-1)*2 else f.coefs.length-1 )).drop(1)

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

    def nrMemAddrs      = maxDataBufAddr + 1 + totalNrCoefs

    def nrMemDataBits   = nrDataBits.max(nrCoefBits)
    def nrMemAddrBits   = log2Up(nrMemAddrs)

    def allCoefs = filters.foldLeft(ArrayBuffer[Int]()){ _ ++ _.coefs }

    def memInit : Array[SInt] = {
        val l = ArrayBuffer[SInt]()

        allCoefs.foreach({ l.append(_) }) 
        (0 to maxDataBufAddr).foreach({ _ => l.append(0) })
        l.toArray
    }

    def toFirFilterFixedInfoHW(idx : Int) : FirFilterFixedInfoHW = {
      
        val fiHW = FirFilterFixedInfoHW(this, idx)

        fiHW
    }
}

class FirEngine(conf: FirEngineConfig) extends Component
{
    val io = new Bundle {
        val data_in           = slave(Stream(SInt(conf.nrDataBits bits)))
        val data_out          = master(Flow(SInt(conf.nrDataBits bits)))

        val branch_nr         = out UInt(5 bits)
    }

    printf("totalNrCoefs: %d\n", conf.totalNrCoefs)
    printf("maxDataBufAddr: %d\n",  conf.maxDataBufAddr)
    printf("nrMemAddrs: %d\n",  conf.nrMemAddrs)
    printf("maxDecimationRatio: %d\n",  conf.maxDecimationRatio)
    printf("totalDecimationRatio: %d\n",  conf.totalDecimationRatio)

    //============================================================
    // Data and coefficient RAM - Read
    //============================================================
    val mem_rd_en_p0    = Bool
    val mem_rd_addr_p0  = UInt(conf.nrMemAddrBits bits)
    val mem_rd_data_p1  = SInt(conf.nrMemDataBits bits)

    val u_mem = Mem(SInt(conf.nrMemDataBits bits), conf.memInit)
    mem_rd_data_p1 := u_mem.readSync(
                        address   = mem_rd_addr_p0,
                        enable    = mem_rd_en_p0)

    //============================================================
    // Data and coefficient RAM - Write
    //============================================================
    //
    val mem_wr_en       = Bool
    val mem_wr_addr     = UInt(conf.nrMemAddrBits bits)
    val mem_wr_data     = SInt(conf.nrMemDataBits bits)

    u_mem.write(
          address   = mem_wr_addr,
          data      = mem_wr_data,
          enable    = mem_wr_en)

    //============================================================
    // Filter stage contexts
    //============================================================

    // Fixed config values
    val data_buf_start_addrs    = Vec(UInt(conf.nrMemAddrBits bits), conf.filters.size)
    val data_buf_stop_addrs     = Vec(UInt(conf.nrMemAddrBits bits), conf.filters.size)
    val coef_buf_start_addrs    = Vec(UInt(conf.nrMemAddrBits bits), conf.filters.size)
    val coef_buf_middle_addrs   = Vec(UInt(conf.nrMemAddrBits bits), conf.filters.size)
    val coef_buf_stop_addrs     = Vec(UInt(conf.nrMemAddrBits bits), conf.filters.size)
    val filter_is_halfbands     = Vec(Bool, conf.filters.size)
    val decimation_ratios       = Vec(UInt(log2Up(conf.maxDecimationRatio+1) bits), conf.filters.size)

    for ((startAddr, i) <- conf.dataBufStartAddrs.zipWithIndex) { data_buf_start_addrs(i)  := startAddr   + conf.totalNrCoefs }
    for ((stopAddr,  i) <- conf.dataBufStopAddrs.zipWithIndex)  { data_buf_stop_addrs(i)   := stopAddr    + conf.totalNrCoefs }
    for ((startAddr, i) <- conf.coefBufStartAddrs.zipWithIndex) { coef_buf_start_addrs(i)  := startAddr  }
    for ((filter, i)    <- conf.filters.zipWithIndex)           { coef_buf_middle_addrs(i) := conf.coefBufStartAddrs(i) + filter.coefs.length/2 }
    for ((stopAddr, i)  <- conf.coefBufStopAddrs.zipWithIndex)  { coef_buf_stop_addrs(i)   := stopAddr   }
    for ((filter, i)    <- conf.filters.zipWithIndex)           { filter_is_halfbands(i)   := Bool(filter.isHalfBand)}
    for ((filter, i)    <- conf.filters.zipWithIndex)           { decimation_ratios(i)     := U(filter.decimationRatio) }

    // Variables 
    val data_buf_wr_ptrs        = Vec(Reg(UInt(conf.nrMemAddrBits bits)) init(0), conf.filters.size)
    val data_buf_rd_start_ptrs  = Vec(Reg(UInt(conf.nrMemAddrBits bits)) init(0), conf.filters.size)
    val nr_new_inputs           = Vec(Reg(UInt(log2Up(conf.totalDecimationRatio+1) bits)) init(0), conf.filters.size)

    //============================================================
    // Context for currently selected stage
    //============================================================

    val filter_cntr       = Reg(UInt(log2Up(conf.filters.size) bits)) init(0)

    val data_buf_start_addr     = data_buf_start_addrs(filter_cntr)
    val data_buf_stop_addr      = data_buf_stop_addrs(filter_cntr)
    val coef_buf_middle_addr    = coef_buf_middle_addrs(filter_cntr)
    val coef_buf_stop_addr      = coef_buf_stop_addrs(filter_cntr)
    val filter_is_halfband      = filter_is_halfbands(filter_cntr)
    val decimation_ratio        = decimation_ratios(filter_cntr)

    val data_buf_rd_start_ptr   = data_buf_rd_start_ptrs(filter_cntr)
    val coef_buf_start_addr     = coef_buf_start_addrs(filter_cntr)

    // the _next signals are used to update the write point of the next stage filter.
    val filter_cntr_next  = UInt(log2Up(conf.filters.size) bits)

    if (conf.filters.size == 1)
        filter_cntr_next  := U(0) 
    else 
        filter_cntr_next  := (filter_cntr === conf.filters.size-1) ? U(0) | filter_cntr + 1

    val data_buf_start_addr_fnext   = data_buf_start_addrs(filter_cntr_next)
    val data_buf_stop_addr_fnext    = data_buf_stop_addrs(filter_cntr_next)
    val data_buf_wr_ptr_fnext       = data_buf_wr_ptrs(filter_cntr_next)
    val nr_new_input_fnext          = nr_new_inputs(filter_cntr_next)
    val decimation_ratio_fnext      = decimation_ratios(filter_cntr_next)

    val coef_buf_ptr            = Reg(UInt(conf.nrMemAddrBits bits)) init(0)
    val data_buf_rd_ptr         = Reg(UInt(conf.nrMemAddrBits bits)) init(0)

    val mem_rd_data_is_coef_p0  = Bool
    val mem_rd_data_is_coef_p1  = RegNext(mem_rd_data_is_coef_p0) init(False)

    val data_buf_rd_start_ptr_p_decim = UInt(conf.nrMemAddrBits+1 bits) 
    data_buf_rd_start_ptr_p_decim := data_buf_rd_start_ptr.resize(conf.nrMemAddrBits+1) + decimation_ratio

    val fir_mem_wr_en_p0              = Bool
    val fir_mem_wr_addr_p0            = UInt(conf.nrMemAddrBits bits)
    val fir_mem_wr_data_is_output_p0  = Bool

    object FsmState extends SpinalEnum {
        val Config          = newElement()
        val Idle            = newElement()
        val SetupStage      = newElement()
        val FetchCoef       = newElement()
        val FetchData       = newElement()
    }

    val cur_state = Reg(FsmState()) init(FsmState.Config)
    val branch_nr = Reg(UInt(5 bits)) init(0)
    io.branch_nr  := branch_nr

    mem_rd_en_p0                  := False
    mem_rd_addr_p0                := 0
    mem_rd_data_is_coef_p0        := False

    fir_mem_wr_en_p0              := False
    fir_mem_wr_addr_p0            := 0
    fir_mem_wr_data_is_output_p0  := False

    val is_last_filter_stage = (filter_cntr === conf.filters.size-1)

    switch(cur_state){
        is(FsmState.Config){
            for ((filter, i) <- conf.filters.zipWithIndex){
                data_buf_rd_start_ptrs(i)  := conf.dataBufStartAddrs(i)                            + conf.totalNrCoefs
                data_buf_wr_ptrs(i)        := conf.dataBufStartAddrs(i) + conf.filterOrders(i) + 2 + conf.totalNrCoefs
                nr_new_inputs(i)           := 0 
            }

            cur_state         := FsmState.Idle
        }
        is(FsmState.Idle){
          when(nr_new_inputs(0) >= decimation_ratios(0)){
                filter_cntr       := 0
                cur_state         := FsmState.SetupStage
                
                // We can immediately set this back to 0 as long as the write pointer is at least *decimation_ratio* larger than
                // data_buf_rd_start_ptr + decimation_ratio
                nr_new_inputs(0)  := nr_new_inputs(0) - decimation_ratios(0)
            }
        }
        is(FsmState.SetupStage){
            coef_buf_ptr              := coef_buf_start_addr
            data_buf_rd_ptr           := data_buf_rd_start_ptr
            cur_state                 := FsmState.FetchCoef
        }
        is(FsmState.FetchCoef){
            mem_rd_data_is_coef_p0    := True
            mem_rd_addr_p0            := coef_buf_ptr
            mem_rd_en_p0              := True

            cur_state                 := FsmState.FetchData
        }
        is(FsmState.FetchData){
            mem_rd_data_is_coef_p1    := False
            mem_rd_addr_p0            := data_buf_rd_ptr
            mem_rd_en_p0              := True


            when(filter_is_halfband && (coef_buf_ptr === coef_buf_middle_addr-1 || coef_buf_ptr === coef_buf_middle_addr)){
                // For halfband filter, the data ptr normally needs to be incremented by 2, except
                // for the center tap where we need to increment twice by 1
                data_buf_rd_ptr       := (data_buf_rd_ptr === data_buf_stop_addr) ? data_buf_start_addr | data_buf_rd_ptr + 1
            }
            .elsewhen(filter_is_halfband){
                data_buf_rd_ptr       := (data_buf_rd_ptr === data_buf_stop_addr)    ? (data_buf_start_addr + 1)  |
                                         ((data_buf_rd_ptr === data_buf_stop_addr-1) ?  data_buf_start_addr       | 
                                                                                          (data_buf_rd_ptr + 2))
            }
            .otherwise{
                data_buf_rd_ptr       := (data_buf_rd_ptr === data_buf_stop_addr)   ? data_buf_start_addr | data_buf_rd_ptr + 1
            }

            when(coef_buf_ptr =/= coef_buf_stop_addr){
                // Current filter still ongoing
                coef_buf_ptr    := coef_buf_ptr + 1
                cur_state       := FsmState.FetchCoef
                branch_nr       := 1
            }
            .otherwise{
                // Last element of the filter. 

                // Increase start of input data buffer for current filter by <decimation ratio>
                data_buf_rd_start_ptr   := ((data_buf_rd_start_ptr_p_decim > data_buf_stop_addr) ? (data_buf_rd_start_ptr_p_decim - data_buf_stop_addr + data_buf_start_addr) 
                                                                                                 |  data_buf_rd_start_ptr_p_decim).resize(conf.nrMemAddrBits)


                // Write newly calculated output to input buffer of the next filter or the output
                fir_mem_wr_en_p0              := True
                fir_mem_wr_addr_p0            := data_buf_wr_ptr_fnext
                fir_mem_wr_data_is_output_p0  := is_last_filter_stage

                when(!is_last_filter_stage){
                    data_buf_wr_ptr_fnext := (data_buf_wr_ptr_fnext === data_buf_stop_addr_fnext) ? data_buf_start_addr_fnext | data_buf_wr_ptr_fnext + 1
                }

                when(is_last_filter_stage){
                    // Last filter stage created an output. Back to idle.
                    filter_cntr           := 0

                    cur_state             := FsmState.Idle
                    branch_nr             := 2
                }
                .elsewhen(nr_new_input_fnext =/= decimation_ratio_fnext-1){
                    // We don't have enough new samples yet for the next stage. Back to idle.
                    nr_new_input_fnext    := nr_new_input_fnext + 1
                    filter_cntr           := 0

                    cur_state             := FsmState.Idle
                    branch_nr             := 3
                }
                .otherwise{
                    // Switch to next filter in the chain
                    if (conf.filters.size != 1)
                        filter_cntr       := filter_cntr + 1

                    nr_new_input_fnext    := U(0, nr_new_inputs(0).getWidth bits)

                    cur_state             := FsmState.SetupStage
                    branch_nr             := 4
                }
            }
        }
    }

    val mem_rd_en_p1  = RegNext(mem_rd_en_p0) init(False)

    val cur_coef_p2   = Reg(SInt(conf.nrCoefBits bits))
    val cur_data_p2   = Reg(SInt(conf.nrDataBits bits))

    when(mem_rd_en_p1 && mem_rd_data_is_coef_p1){
        cur_coef_p2   := mem_rd_data_p1.resize(conf.nrCoefBits)
    }

    val mul_en_p2     = Reg(Bool) init(False)

    mul_en_p2   := False
    when(mem_rd_en_p1 && !mem_rd_data_is_coef_p1){
        cur_data_p2   := mem_rd_data_p1.resize(conf.nrDataBits)
        mul_en_p2     := True
    }

    val mul_p3 = Reg(SInt(conf.nrCoefBits + conf.nrDataBits bits)) init(0)

    val accum_en_p3   = Reg(Bool) init(False)

    accum_en_p3  := False
    when(mul_en_p2){
        mul_p3        := cur_data_p2 * cur_coef_p2
        accum_en_p3   := True
    }

    val accum_p4 = Reg(SInt(conf.nrCoefBits + conf.nrDataBits bits)) init(0)
    when(accum_en_p3){
        accum_p4  := accum_p4 + mul_p3
    }

    val fir_mem_wr_en_final              = Delay(fir_mem_wr_en_p0, 4)
    val fir_mem_wr_addr_final            = Delay(fir_mem_wr_addr_p0, 4)
    val fir_mem_wr_data_is_output_final  = Delay(fir_mem_wr_data_is_output_p0, 4)
    val fir_mem_wr_data_final            = (accum_p4 >> (conf.nrCoefBits-1)).resize(conf.nrDataBits)

    val data_out_valid    = Reg(Bool) init(False)
    val data_out_payload  = Reg(SInt(conf.nrDataBits bits)) init(0)

    data_out_valid     := False
    when(fir_mem_wr_en_final){
        accum_p4              := 0

        when(fir_mem_wr_data_is_output_final){
            data_out_valid     := True
            data_out_payload   := fir_mem_wr_data_final
        }
    }

    io.data_out.valid   := data_out_valid
    io.data_out.payload := data_out_payload

    //============================================================
    // Save to mem
    //============================================================
    // There are two sources for writes to memory
    // - the main FIR FSM. This one is responsible to write samples that come from intermediate stages.
    //   Writes from this source can't be stalled, so it has priority.
    // - the data input
    //   These can be stalled so they get second priority.
    // Irrespective of the source, the block below keeps track of the number of new samples that have been
    // written towards a particular stage: input stage -> stage 0, stage n -> stage n+1.
    //
    mem_wr_en                 := False
    mem_wr_addr               := 0
    mem_wr_data               := 0

    io.data_in.ready    := False

    //val data_buf_wr_ptr_0_incr = (data_buf_wr_ptrs(0) === data_buf_stop_addr) ? data_buf_start_addr | data_buf_wr_ptrs(0) + 1

    when(fir_mem_wr_en_final && !fir_mem_wr_data_is_output_final){
        mem_wr_en           := fir_mem_wr_en_final
        mem_wr_addr         := fir_mem_wr_addr_final
        mem_wr_data         := fir_mem_wr_data_final.resize(conf.nrMemDataBits)
    }
    .elsewhen(io.data_in.valid && !nr_new_inputs(0).andR){
        io.data_in.ready    := True

        mem_wr_en           := True
        mem_wr_addr         := data_buf_wr_ptrs(0)
        mem_wr_data         := io.data_in.payload.resize(conf.nrMemDataBits)

        data_buf_wr_ptrs(0) := (data_buf_wr_ptrs(0) === data_buf_stop_addrs(0)) ? data_buf_start_addrs(0) | data_buf_wr_ptrs(0) + 1
        nr_new_inputs(0)    := nr_new_inputs(0) + 1
    }

}

object FirEngineTopVerilogSyn {
    def main(args: Array[String]) {



        val config = SpinalConfig(anonymSignalUniqueness = true)
        config.generateVerilog({

            val firs = ArrayBuffer[FirFilterInfo]()
    
            if (false){
                firs += FirFilterInfo("HB1",  256, true,  2, Array[Int](1,2,3,4,5,6,7,8,9)) 
                firs += FirFilterInfo("HB2",   64, true,  4, Array[Int](1,2,3,4,5)) 
                firs += FirFilterInfo("FIR1",  64, false, 2, Array[Int](1,2,3)) 
                firs += FirFilterInfo("FIR2",  64, false, 1, Array[Int](1,2,3,4,5,6,7,8,9,10)) 
            }
            else if (true){
                firs += FirFilterInfo("HB1", 25, true, 2, Array[Int](878,-6713,38602,65535,38602,-6713,878))
                firs += FirFilterInfo("HB2", 27, true, 2, Array[Int](94,-723,3032,-9781,40145,65535,40145,-9781,3032,-723,94))
                firs += FirFilterInfo("FIR", 62, false, 1, Array[Int](-14,-50,-84,-49,117,349,423,108,-518,-932,-518,737,1854,1476,
                                                                      -738,-3193,-3245,293,5148,6520,1184,-8322,-13605,-5839,16758,
                                                                      45494,65535,65535,45494,16758,-5839,-13605,-8322,1184,6520,5148,
                                                                      293,-3245,-3193,-738,1476,1854,737,-518,-932,-518,108,423,
                                                                      349,117,-49,-84,-50,-14))

            }
            else{
                firs += FirFilterInfo("FIR1",  20, false,  1, Array[Int](131071)) 
                firs += FirFilterInfo("FIR2",  20, false,  1, Array[Int](131071)) 
            }
            

            val conf = FirEngineConfig(
                firs.toArray, 
                16,
                18
            )

            conf.filterOrders.foreach { printf("order: %d\n", _) }

            val toplevel = new FirEngine(conf)
            toplevel
        })
    }
}

