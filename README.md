# nutanix-cliOutput2csv

1. session logging한 output 파일로부터 아래의 정보를 수집함.
  ncli host ls
  ncc hardware_info show_hardware_info

2. 동일 디렉토리에 csv 파일을 생성함.
  <csv key>
  site,block model,block serial,node serial,cluster name,hostname,ipmiIp,ahvIp,cvmIp,node id,ahv,aos,ncc,bmc,bios,Processor model,socket,core/cpu,Total MEM Size,size/SSD,SSD qty,Total HDD size,<--HW Details->,Dimm spec,SSD spec,HDD spec,SATADOM spec
