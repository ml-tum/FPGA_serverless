for {set j 0}  {$j < $cfg(n_reg)} {incr j} {

##################################################################
# CREATE IP axis_data_fifo_0
##################################################################

set axis_data_fifo_0 [create_ip -name axis_data_fifo -vendor xilinx.com -library ip -version 2.0 -module_name axis_data_fifo_0_c11_$j]

set_property -dict { 
  CONFIG.TDATA_NUM_BYTES {4}
  CONFIG.HAS_WR_DATA_COUNT {1}
  CONFIG.HAS_RD_DATA_COUNT {1}
  CONFIG.FIFO_DEPTH {16384}
  CONFIG.HAS_PROG_FULL {1}
  CONFIG.PROG_FULL_THRESH {15000}
  CONFIG.FIFO_MEMORY_TYPE {ultra}
} [get_ips axis_data_fifo_0_c11_$j]

set_property -dict { 
  GENERATE_SYNTH_CHECKPOINT {1}
} $axis_data_fifo_0

move_files -of_objects [get_reconfig_modules design_user_wrapper_c11_$j] [get_files axis_data_fifo_0_c11_$j.xci]

##################################################################
# CREATE IP axis_dwidth_converter_4_64
##################################################################

set axis_dwidth_converter_4_64 [create_ip -name axis_dwidth_converter -vendor xilinx.com -library ip -version 1.1 -module_name axis_dwidth_converter_4_64_c11_$j]

set_property -dict { 
  CONFIG.S_TDATA_NUM_BYTES {4}
  CONFIG.M_TDATA_NUM_BYTES {64}
  CONFIG.HAS_TLAST {1}
  CONFIG.HAS_TKEEP {0}
  CONFIG.HAS_MI_TKEEP {1}
} [get_ips axis_dwidth_converter_4_64_c11_$j]

set_property -dict { 
  GENERATE_SYNTH_CHECKPOINT {1}
} $axis_dwidth_converter_4_64
	
move_files -of_objects [get_reconfig_modules design_user_wrapper_c11_$j] [get_files axis_dwidth_converter_4_64_c11_$j.xci]
	
##################################################################

##################################################################
# CREATE IP axis_dwidth_converter_64_4
##################################################################

set axis_dwidth_converter_64_4 [create_ip -name axis_dwidth_converter -vendor xilinx.com -library ip -version 1.1 -module_name axis_dwidth_converter_64_4_c11_$j]

set_property -dict { 
  CONFIG.S_TDATA_NUM_BYTES {64}
  CONFIG.M_TDATA_NUM_BYTES {4}
  CONFIG.HAS_TLAST {1}
} [get_ips axis_dwidth_converter_64_4_c11_$j]

set_property -dict { 
  GENERATE_SYNTH_CHECKPOINT {1}
} $axis_dwidth_converter_64_4

move_files -of_objects [get_reconfig_modules design_user_wrapper_c11_$j] [get_files axis_dwidth_converter_64_4_c11_$j.xci]

##################################################################

##################################################################
# CREATE IP floating_point_add
##################################################################

set floating_point_add [create_ip -name floating_point -vendor xilinx.com -library ip -version 7.1 -module_name floating_point_add_c11_$j]

set_property -dict { 
  CONFIG.Has_ARESETn {true}
  CONFIG.Add_Sub_Value {Add}
  CONFIG.Flow_Control {NonBlocking}
  CONFIG.Has_RESULT_TREADY {false}
  CONFIG.C_Latency {11}
} [get_ips floating_point_add_c11_$j]

set_property -dict { 
  GENERATE_SYNTH_CHECKPOINT {1}
} $floating_point_add

move_files -of_objects [get_reconfig_modules design_user_wrapper_c11_$j] [get_files floating_point_add_c11_$j.xci]

##################################################################

##################################################################
# CREATE IP floating_point_mul
##################################################################

set floating_point_mul [create_ip -name floating_point -vendor xilinx.com -library ip -version 7.1 -module_name floating_point_mul_c11_$j]

set_property -dict { 
  CONFIG.Has_ARESETn {true}
  CONFIG.Operation_Type {Multiply}
  CONFIG.A_Precision_Type {Single}
  CONFIG.C_A_Exponent_Width {8}
  CONFIG.C_A_Fraction_Width {24}
  CONFIG.Result_Precision_Type {Single}
  CONFIG.C_Result_Exponent_Width {8}
  CONFIG.C_Result_Fraction_Width {24}
  CONFIG.C_Mult_Usage {Full_Usage}
  CONFIG.Flow_Control {NonBlocking}
  CONFIG.Axi_Optimize_Goal {Resources}
  CONFIG.Has_RESULT_TREADY {false}
  CONFIG.C_Latency {8}
  CONFIG.C_Rate {1}
} [get_ips floating_point_mul_c11_$j]

set_property -dict { 
  GENERATE_SYNTH_CHECKPOINT {1}
} $floating_point_mul

move_files -of_objects [get_reconfig_modules design_user_wrapper_c11_$j] [get_files floating_point_mul_c11_$j.xci]

##################################################################

##################################################################
# CREATE IP xfft_1
##################################################################

set xfft_1 [create_ip -name xfft -vendor xilinx.com -library ip -version 9.1 -module_name xfft_1_c11_$j]

set_property -dict { 
  CONFIG.transform_length {32768}
  CONFIG.implementation_options {automatically_select}
  CONFIG.target_data_throughput {1000}
  CONFIG.run_time_configurable_transform_length {true}
  CONFIG.data_format {floating_point}
  CONFIG.input_width {32}
  CONFIG.phase_factor_width {24}
  CONFIG.scaling_options {scaled}
  CONFIG.aresetn {true}
  CONFIG.output_ordering {natural_order}
  CONFIG.number_of_stages_using_block_ram_for_data_and_phase_factors {7}
  CONFIG.memory_options_hybrid {true}
  CONFIG.complex_mult_type {use_mults_performance}
  CONFIG.butterfly_type {use_xtremedsp_slices}
} [get_ips xfft_1_c11_$j]

set_property -dict { 
  GENERATE_SYNTH_CHECKPOINT {1}
} $xfft_1

move_files -of_objects [get_reconfig_modules design_user_wrapper_c11_$j] [get_files xfft_1_c11_$j.xci]

##################################################################

}
