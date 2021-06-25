"""

Nutanix 로그 파일로 csv 생성
사용예: c:\> py   nclihostls2csv.py   putty.log

수집 내용
1. ncli host ls
2. allssh 'sleep 2 ; ncc hardware_info show_hardware_info'

 ncli host ls : 호스트 정보 수집
 ncc hardware_info show_hardware_info : cpu, mem, disk, 클러스터 명, aos, ahv, ncc, bmc, bios 수집
(ncc: show_hardware_info에 포함되므로 생략가능. 클러스터 명, aos, ahv, ncc, bmc, bios 수집)

"""
from dataclasses import dataclass
#-*- coding:utf-8 -*-
import sys,csv,re
from operator import itemgetter

# Lines 읽어들인 로그
# SeekLocation 현재 탐색 위치
# EndLocation 탐색 종료 위치
DELIMITER_HARDWARE_INFO="+-"
Lines=""
StartSeekLocation=0
EndSeekLocation=0
NodesInfo=[]
ClusterName= ""

def printHelp():
    program=sys.argv[0].split("/")
    path=program[0:len(program)-1]
    program=program[len(program)-1]
    print("usage:\n\n"
          ,"py ",program," c:\downloads\putty.log")



"""
csv에 cvm ip로 한줄 추가.
csv에 key로 사용될 cvm ip가 없을 때도 호출
"""
def appendNodesInfo(targetCvmIp):
    global NodesInfo
    NodesInfo.append({
                    "site":""               , "block model":"","block serial":""  ,"node serial":""
                    ,"cluster name":""       ,"hostname":""
                    ,"ipmiIp":""            ,"ahvIp":""         ,"cvmIp":targetCvmIp,"node id":""
                    ,"ahv":""               ,"aos":""           ,"ncc":""
                    })

def updateNodesInfo(targetCvmIp,dictdata):
    global Lines, EndSeekLocation, StartSeekLocation, NodesInfo,cvmIps
    flagNoKey=1
    # targetCvm을 찾아서
    for i in range(len(NodesInfo)):
        if NodesInfo[i]['cvmIp'] == targetCvmIp:
            # dictdata의 key:value 내용을 변경하거나, 없으면 새로 추가함.
            #
            flagNoKey=0
            for key, value in dictdata.items():
                NodesInfo[i][key]=value
    if flagNoKey == 1:
        print("updateNodesInfo(targetCvm,dictdata): NodesInfo에서 ",targetCvmIp,"를 못찾음")
        print("로그파일에는 ncli host ls가 반드시 있어야 함.")
        #appendNodesInfo(targetCvm)
        #updateNodesInfo(targetCvm,dictdata)

def openfile(filename):
    if __debug__:
        print("call openfile()")
    global Lines, EndSeekLocation, StartSeekLocation
    f = open(filename, 'r',encoding='utf-8')
    Lines = f.readlines()
    f.close()
    StartSeekLocation=0
    EndSeekLocation= len(Lines) - 1
    # 공백제거 strip()
    while StartSeekLocation <= EndSeekLocation:
        Lines[StartSeekLocation]=Lines[StartSeekLocation].strip()
        # 읽은 로그파일 표시
        # print(Lines[StartSeekLocation])
        StartSeekLocation += 1
    StartSeekLocation = 0



"""
gotoPosition(key)
 -범위:SeekLocation ~ EndLocation
 -현재 SeekLocation에서 가장 가까운 key값으로 SeekLocation을 이동함.
    -또한 SeekLocation 정수값을 리턴함.
    -못찾으면 -1을 리턴함 
"""
def gotoPosition(key):
    global Lines, EndSeekLocation, StartSeekLocation
    #print("gotoPosition(",key,")start SeekLocation=", StartSeekLocation, "     EndLocation=", EndSeekLocation)
    for i in range(StartSeekLocation, len(Lines)):
        if Lines[i].find(key)>=0:
            StartSeekLocation=i
            #print("gotoPosition(",key,") Founded SeekLocation=", i)
            return i
    return -1



"""
getVal(word)
 -범위:SeekLocation ~ EndLocation
 -key에 대한 값을 return
"""
def getVal(key):
    global Lines, EndSeekLocation, StartSeekLocation
    retVal = ""
    for i in range(StartSeekLocation+1,EndSeekLocation):
        if Lines[i].find(key)>=0:

            if Lines[i].find("::") >= 0:
                retVal=Lines[i].split("::")[1].strip()
                StartSeekLocation = i
                print('Lines[', StartSeekLocation, '].(', key, ')=', retVal)
                break
            elif Lines[i].find("|")>=0:
                retVal=Lines[i].split("|")[2].strip()
                StartSeekLocation = i
                print('Lines[', StartSeekLocation, '].(', key, ')=', retVal)
                break
            elif Lines[i].find(":") >= 0:
                retVal=Lines[i].split(":")[1].strip()
                StartSeekLocation = i
                print('Lines[', StartSeekLocation, '].(', key, ')=', retVal)
                break

    return retVal


"""
cli 커맨드의 결과가 끝나서 프롬프트 $로 나왔는지 확인하기 위한 목적
cli 결과를 while 루프 돌릴 때 사용 
"""
def setEndSeekLocationUntilDollor():
    global Lines, EndSeekLocation, StartSeekLocation
    for i in range(StartSeekLocation+1, len(Lines)):
        if Lines[i].find('$')>=0:
            EndSeekLocation=i
            print("find range = ",StartSeekLocation," ~ ", EndSeekLocation)
            break



def saveCsv(filename,listdictVar):
    try :
        sortedlistdictVar = sortDict(listdictVar)
        print("saveCsv===========================")
        s = open(filename+".csv", 'w', encoding='utf-8', newline='')
        csvwriter = csv.writer(s)
        longestList=0
        for i in range(len(sortedlistdictVar)):
            if len(sortedlistdictVar[i]) > len(sortedlistdictVar[longestList]) :
                longestList = i
        print("Longest list number = ", longestList)
        print("csv file may use Longest key as below")
        print("==============================")
        print("Key : ")
        for key in sortedlistdictVar[longestList]:
            print(key + ", ", end="")
        print("\n==============================")
        csvwriter.writerow(list(sortedlistdictVar[longestList].keys()))
        for dict in sortedlistdictVar:
            csvwriter.writerow(list(dict.values()))
        s.close()

        showcsv(filename+".csv")
        print("====================")
        print(filename+".csv saved.")
    except Exception as e:
        print ("Exception in creating "+filename+".csv" )
        print ("You may open this file. So this program cannot write csv file.")
        print (e)

def sortDict(listdictVar):
    print("sortDict()")
    sorteddictvar=sorted(listdictVar,key=itemgetter("cvmIp"))
    #print(sorteddictvar)
    return sorteddictvar

def showcsv(filename):
    f=open(filename,'r',encoding='utf-8')
    lines=f.readlines()
    print("======================CSV file view=================================")
    for line in lines:
        print(line,end="")
    f.close()
"""

"""
def ncliruls():
    print("test")

"""
아직 안씀
"""
def ncliclusterinfo():
    global Lines, EndSeekLocation, StartSeekLocation, NodesInfo, ClusterName,Vip,ScsiIp
    print("call ncliclusterinfo()")
    StartSeekLocation=0
    if gotoPosition("ncli cluster info")>=0:
        ClusterName=getVal("Cluster Name")
        Vip = getVal("External IP address")
        ScsiIp = getVal("External Data Services")


"""
가장 선행되어야 함.
host list로 Dictionary List를 생성함.
"""
def nclihostls():
    global Lines, EndSeekLocation, StartSeekLocation, NodesInfo,ClusterName
    StartSeekLocation=0
    if gotoPosition("ncli host ls")>=0:
        setEndSeekLocationUntilDollor()
        while StartSeekLocation<=EndSeekLocation:
            # 옛날 ncli host ls는 ID로 표시됨, 요즘엔 Id로 표시됨.
            print ("ncli host ls lines = ", StartSeekLocation)
            nodeId= getVal("I")
            if nodeId=="":
                break
            print("-nodeId=",nodeId)
            hostname= getVal("Name")
            print("-hostname=",hostname)
            ipmiIp= getVal("IPMI Address")
            cvmIp= getVal("Controller VM Address")
            ahvIp = getVal("Hypervisor Address")
            print("ncli host ls : founded ips",ipmiIp,ahvIp,cvmIp)
            node= getVal("Node Serial (UUID)")
            block=getVal("Block Serial (Model)")

            if block!="":
                blocksn= block.split()[0]
                blockmodel=  block.split("(")[1]
                blockmodel=blockmodel[0:len(blockmodel)-1]
            if node!="":
                nodesn=  block.split("(")[0]

            if cvmIp != "":
                appendNodesInfo(cvmIp)
                updateNodesInfo(cvmIp,
                                {"cluster name": ClusterName, "hostname": hostname, "ipmiIp": ipmiIp, "ahvIp": ahvIp,
                                 "cvmIp": cvmIp, "block model": blockmodel, "block serial": blocksn,
                                 "node serial": nodesn,  "node id": nodeId})






"""
show_hardware_info 결과 업데이트
"""
def showhardwareinfo():
    global Lines, EndSeekLocation, StartSeekLocation, NodesInfo,cvmIps
    StartSeekLocation=0
    EndSeekLocation=len(Lines)
    print("showhardwareinfo() start")
    if gotoPosition("show_hardware_info") >= 0:
        while StartSeekLocation<=len(Lines):
            if gotoPosition("Detailed") >= 0:
                #print("showhardwareinfo()found cvmips : ",Lines[StartSeekLocation+1])
                gotoPosition("Node")
                cvmIps = Lines[StartSeekLocation].split()[1]
                cvmIps = regIp(cvmIps)
                StartSeekLocation = StartSeekLocation + 1

                gotoPosition("Node Module")
                setEndSeekLocationForShowhardware()
                fru=getVal("Product name")
                gotoPosition("BIOS Information")
                setEndSeekLocationForShowhardware()
                bios=getVal("Version")
                gotoPosition("BMC")
                setEndSeekLocationForShowhardware()
                bmc=getVal("Firmware revision")



                cpuInfo=showhardwareCpu()

                dimmInfo=showhardwareDimm()

                satadomInfo=showhardwareSatadom()

                ssdInfo=showhardwareSsd()

                hddInfo=showhardwareHdd()




                updateNodesInfo(cvmIps, {"bmc": bmc})
                updateNodesInfo(cvmIps, {"bios": bios})
                updateNodesInfo(cvmIps, cpuInfo)
                updateNodesInfo(cvmIps, {"Total MEM Size": dimmInfo["Total MEM Size"]})
                updateNodesInfo(cvmIps, {"size/SSD": ssdInfo["size/SSD"]})
                updateNodesInfo(cvmIps, {"SSD qty": ssdInfo["SSD qty"]})
                updateNodesInfo(cvmIps, {"Total HDD size": hddInfo["Total HDD size"]})
                updateNodesInfo(cvmIps, {"<--HW Details->":""})
                updateNodesInfo(cvmIps, {"Dimm spec": dimmInfo["Dimm spec"]})
                updateNodesInfo(cvmIps, {"SSD spec": ssdInfo["SSD spec"]})
                updateNodesInfo(cvmIps, {"HDD spec": hddInfo["HDD spec"]})
                updateNodesInfo(cvmIps, {"SATADOM spec": satadomInfo["SATADOM spec"]})
            #elif :
            #    print("showhardwareinfo break.")
            #    break
            StartSeekLocation += 1


def setEndSeekLocationForShowhardware():
    global  Lines, EndSeekLocation, StartSeekLocation, NodesInfo

    for i in range(StartSeekLocation+2, len(Lines)):
        if Lines[i].find('+-') >= 0 or Lines[i].find('|') >= 0:
            continue
        else:
            EndSeekLocation=i-1
            print("find range = ",StartSeekLocation," ~ ",EndSeekLocation)
            break


def showhardwareCpu():
    global Lines, EndSeekLocation, StartSeekLocation, NodesInfo,cvmIps
    gotoPosition("Processor Information")
    print("Processor Information found StartSeekLocation =", StartSeekLocation)
    setEndSeekLocationForShowhardware()

    corePerCpu = getVal("Core enabled")
    cpumodel = getVal("Version")
    cpunum = 1

    for StartSeekLocation in range(StartSeekLocation, EndSeekLocation - 1):
        if Lines[StartSeekLocation].find("Memory") >= 0:
            print("Memory met : ",StartSeekLocation)
            break
        elif Lines[StartSeekLocation].find("Socket designation") >= 0:
            cpunum += 1
    return {"Processor model":cpumodel,"socket":cpunum,"core/cpu":corePerCpu}

def showhardwareDimm():
    global Lines, EndSeekLocation, StartSeekLocation, NodesInfo
    totalDimmSize = 0
    dimmspec=[]

    gotoPosition("Memory Module")
    print("showhardwareDimm start at StartSeekLocation=", StartSeekLocation)
    setEndSeekLocationForShowhardware()
    while StartSeekLocation<EndSeekLocation:

        dimmLoc = getVal("Location")

        """
        ncc 구버전은 No DIMM 스테이터스가 Location 아래 2번째 줄에 있음.
   +--------------------------------------------------------------------------------------------------+
   | Location                      |   P1-DIMMA1                                                      |
   | Bank connection               |   P0_Node0_Channel0_Dimm0                                        |
   | Capable speed                 |   1333 MHz                                                       |
   | Installed size                |   16384 MB                                                       |
   | Manufacturer                  |   Samsung                                                        |
   | Product part number           |   M393B2G70BH0-CK0                                               |
   | Serial number                 |   0000E959                                                       |
   | Type                          |   0x18 (DDR3)                                                    |
   +--------------------------------------------------------------------------------------------------+
   | Location                      |   P1-DIMMA2                                                      |
   | Bank connection               |   P0_Node0_Channel0_Dimm1                                        |
   | Status                        |   No DIMM  
        """
        if Lines[StartSeekLocation+2].find("No DIMM") == -1:
            dimmSize =getVal("Installed size")
            dimmProd = getVal("Product part number")
            dimmSn = getVal("Serial number")
            foundeddimm = dimmLoc + ':' + dimmSize + ':' + dimmProd + '(' + dimmSn + ')'
            totalDimmSize += int(dimmSize.split()[0])/1024
            print('founded dimm=',foundeddimm)
            print("TOT DIMM=",totalDimmSize)
            dimmspec.append(str(foundeddimm))


        gotoPosition(DELIMITER_HARDWARE_INFO)

    print("END of showhardwareDimm")
    return {"Dimm spec":dimmspec,"Total MEM Size":totalDimmSize}

def showhardwareSatadom():
    global Lines, EndSeekLocation, StartSeekLocation, NodesInfo,cvmIps
    satadomSpec=[]


    # 옛날 ncc는 SATADOM이 없음
    if gotoPosition("SATADOM")>=0:
        print("SATADOM start at StartSeekLocation=", StartSeekLocation)
        setEndSeekLocationForShowhardware()
        while StartSeekLocation<EndSeekLocation:
            satadomCap=getVal("Capacity")
            satadomModel=getVal("Device model")
            satadomSn=getVal("Serial number")
            satadomSpec.append(satadomCap+':'+satadomModel+"("+satadomSn+")")
            #print(StartSeekLocation)
            gotoPosition(DELIMITER_HARDWARE_INFO)
        #print("SATADOM spec     ", {"SATADOM spec":satadomSpec})
    elif gotoPosition("Host Boot RAID Disks") >=0:
        print("Host Boot RAID Disks start at StartSeekLocation=", StartSeekLocation)
        setEndSeekLocationForShowhardware()
        while StartSeekLocation<EndSeekLocation:
            #satadomCap = getVal("Capacity")
            satadomModel = getVal("Model")
            satadomSn = getVal("Serial number")
            satadomSpec.append(satadomCap+':'+satadomModel+"("+satadomSn+")")
            # print(StartSeekLocation)
            gotoPosition(DELIMITER_HARDWARE_INFO)
    else:
        #allflash model의 경우 Hypervisor Disk True가 m.2
        tmp=gotoPosition("SSD")
        setEndSeekLocationForShowhardware()
        while StartSeekLocation<EndSeekLocation:
            #print(Lines[StartSeekLocation])
            satadomCap = getVal("Capacity")
            hypervisorDisk =getVal("Hypervisor disk")
            satadomModel = getVal("Product part number")
            satadomSn = getVal("Serial number")
            if hypervisorDisk=="True":
                satadomSpec.append(satadomCap+':'+satadomModel+"("+satadomSn+")")

            gotoPosition(DELIMITER_HARDWARE_INFO)
        StartSeekLocation=tmp

    print("END of showhardwareSatadom", satadomSpec)
    return {"SATADOM spec": satadomSpec}


def showhardwareSsd():
    global Lines, EndSeekLocation, StartSeekLocation, NodesInfo,cvmIps
    ssdSpec=[]
    totalSsdSize=0
    diskqty=0
    diskCap=""
    gotoPosition("SSD")
    print("showhardwareSsd start at StartSeekLocation=", StartSeekLocation)
    setEndSeekLocationForShowhardware()

    while  StartSeekLocation<EndSeekLocation:
        loc=getVal("Location")
        hypervisorDisk =getVal("Hypervisor disk")

        # hypervisorDisk = True는 M.2임. 따라서 ssd 사이즈 계산에서 제외
        # 옛날 모델은 hypervisorDisk 값이 없음
        if hypervisorDisk == "False" or loc != "":
            StartSeekLocation -= 3
            diskCap = getVal("Capacity")

            diskModel = getVal("Product part number")

            diskSn = getVal("Serial number")

            diskqty += 1
            foundedssd=loc+':'+diskCap+':'+diskModel+'('+diskSn+')'
            ssdSpec.append(foundedssd)

            diskCap=float(diskCap.split()[0])
            totalSsdSize += diskCap
        else:
            break
        #while Lines[StartSeekLocation].find("HDD") < 0 and Lines[StartSeekLocation].find("Location") < 0:



    #print("SSD spec     ", {"SSD spec": ssdSpec,"Total SSD size":totalSsdSize})
    return {"SSD spec": ssdSpec,"Total SSD size":totalSsdSize,"size/SSD":diskCap,"SSD qty":diskqty}

def showhardwareHdd():
    global Lines, EndSeekLocation, StartSeekLocation, NodesInfo,cvmIps

    hddSpec=[]
    totalHddSize=0


    if gotoPosition("HDD")>=0:
        print("showhardwareHdd start at StartSeekLocation=", StartSeekLocation)
        setEndSeekLocationForShowhardware()
        while StartSeekLocation<EndSeekLocation:
            loc= getVal('Location')
            hddCap = getVal("Capacity")
            totalHddSize += float(hddCap.split()[0])
            hddModel = getVal("Product part number")
            hddSn = getVal("Serial number")
            foundedhdd = loc + ':' + hddCap + ':' + hddModel + '(' + hddSn + ')'
            hddSpec.append(foundedhdd)
            #print(StartSeekLocation)
            gotoPosition(DELIMITER_HARDWARE_INFO)
        #print("HDD spec     ", {"HDD spec": hddSpec,"Total SSD size":totalHddSize})
        return {"HDD spec": hddSpec,"Total HDD size":totalHddSize}
    else:
        return {"HDD spec": "", "Total HDD size":""}

"""
ncc 실행결과로 cluster name을 업데이트 함.
"""
def ncc():
    global Lines, EndSeekLocation, StartSeekLocation, NodesInfo
    StartSeekLocation=0
    EndSeekLocation=len(Lines)

    ncc=getVal("ncc_version")
    setEndSeekLocationUntilDollor()
    print("founded ncc_version loc=",StartSeekLocation, ", ",ncc)
    if ncc != "":

        clusterName = getVal("cluster name")
        while StartSeekLocation<EndSeekLocation:
            cvmIp=getVal("service vm external ip")
            ahv=getVal("hypervisor version")
            aos=getVal("software version")
            if cvmIp != "":
                updateNodesInfo(cvmIp, {"cluster name": clusterName,"ahv":ahv,"aos":aos,"ncc":ncc})
            else:
                break

def regIp(ip):
    #regex=re.compile('[0-9]+.[0-9]+.[0-9]+.[0-9]+')
    regex = '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+'
    print("before reg ip = ",ip)
    ip=re.search(regex,ip).group()
    print ("after reg ip = ",ip)
    return ip

"""

MAIN
nclihostls()가 가장 우선 실행되어야, 노드의 리스트가 만들어지고
나머지 함수는 만들어진 노드 리스트에 업데이트함.

"""
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        printHelp()
        filename ="putty.log"
        #exit()

    openfile(filename)
    # ncliclusterinfo()
    nclihostls()
    ncc()
    showhardwareinfo()


    print("==============================================================================")
    #for node in NodesInfo:
    #    print(node)
    saveCsv(filename, NodesInfo)





# See PyCharm help at https://www.jetbrains.com/help/pycharm/
