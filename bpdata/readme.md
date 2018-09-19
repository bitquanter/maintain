### 概述  
bpdata包用于从交易所获取数据
### 安装说明
只适用于python3环境  
安装前确保python3不缺少依赖  
sudo apt update  
sudo apt install python3.6-dev  
运行命令  
pip3 install -r requirements.txt  
### 文件说明：
bpdata/tick2redis.py文件将交易所tick数据写入redis  
bpdata/depth2redis.py文件将交易所depth数据写入redis  
bpdata/monitor_entry.py文件用于监控redis中数据更新状态  
scripts/gen_next_day_db_placeholder.py脚本用于定时生成第二天要采样数据占位符  
scripts/update_fund_dynamic_data.py脚本用于以确定间隔在每天的特定时间点采样redis数据写入数据库    
### 使用说明
前台运行  
python3 xxxx.py  
后台运行  
screen python3 xxxx.py &  
xxxx.py 为文件说明中所示文件  
### 查看输出
redis-cli  
keys *  
get tick/{exchange}/{coinpair}  
get depth/{exchange}/{coinpair}  
get stat/keys_count  
