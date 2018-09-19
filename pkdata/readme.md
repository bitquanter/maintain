### 概述  
pkdata包用于从交易所抽取币对相关数据并解析入库
### 文件说明：
__main__.py文件是程序主入口  
config.py配置数据存放位置  
download_raw_data.py文件从交易所下载原始数据  
exchange_enum.py定义了交易所枚举  
orm.py定义了数据库表结构和数据操作类  
parse_raw_data.py文件将交易所取出的原始数据解析成数据库中存放的格式  
### 使用说明
安装requirements.txt中的依赖包  
运行 python __main__.py -t init可以将数据导入数据库  
运行 python __main__.py -t coin_exchange可以将数据库中数据生成coin_exchange_map.json    
运行 python __main__.py -t exchange_coin可以将数据库中数据生成exchange_coin_map.json  
运行 python __main__.py -t contraint可以将数据库中数据生成coin_constraints.json    
### 默认配置
默认原始数据存放在./pkdata/raw_data
默认解析后的文件输出到./pkdata/outputs
