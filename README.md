# nutanix-cliOutput2csv
<pre>
Step:
  1. putty 등에서 아래 커맨드의 결과를 로깅.
    ncli host ls
    allssh 'sleep 10; ncc hardware_info show_hardware_info'

  2. csv 파일 생성
    py nclihostls2csv.py <YourOutputFile.out>
  
  
