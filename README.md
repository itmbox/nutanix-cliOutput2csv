# nutanix-cliOutput2csv
make a csv file from nutanix cli outputs.
1. this script collect the following output from session logging files such as putty.log.
  ncli host ls
  ncc hardware_info show_hardware_info

2. As a result, csv is created in the same directory.
  <csv key>
  site,block model,block serial,node serial,cluster name,hostname,ipmiIp,ahvIp,cvmIp,node id,ahv,aos,ncc,bmc,bios,Processor model,socket,core/cpu,Total MEM Size,size/SSD,SSD qty,Total HDD size,<--HW Details->,Dimm spec,SSD spec,HDD spec,SATADOM spec
