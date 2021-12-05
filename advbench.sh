#!/bin/bash
time1=$(date)
echo "Begin Benchmark at $time1"


tmp_fifofile="/tmp/my_temp.fifo"
mkfifo $tmp_fifofile      # 新建一个fifo类型的文件
exec 6<>$tmp_fifofile     # 将fd6指向fifo类型
rm -f $tmp_fifofile    #删也可以

thread_num=16

#根据线程总数量设置令牌个数
for ((i=0;i<${thread_num};i++));do
    echo
done >&6

for file in ` ls $1 |grep '.bin$' `  
do  
    read -u6
    #可以把具体的需要执行的命令封装成一个函数
    {
        python /home/toor/SADPonzi/teether/bin/gen_exploit.py "$1/$file" 
        echo "" >&6 
    } &
    
done  

wait
exec 6>&- # 关闭fd6
time2=$(date)
echo "End Benchmark at $time2"
echo "================= Finished ============"
