# ATTiny414 10-bit ADC Firmware

## API

Authored by: Sonny Winstrup
Contributors: Seth Loh

In a serial console to `/dev/tty/AMA1`:

`01` - get API version.  
`02` - get oversample bits.  
`03 <N>` - set oversample bits e.g. `03 08` to set a cumulative total of 256 samples (`sum_samples/N` to get an average reading).  
`04 <N>` - to set sample rate. e.g. `04 05` to get 5 readings a second.
