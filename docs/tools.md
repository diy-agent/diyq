claude --allowedTools WebSearch \
       --effort low \
       --permission-mode bypassPermissions \
       --agents '{"finance": {"description": "查金价和汇率", "prompt": "你是一个金融助手，务必使用 WebSearch 获取实时数据"}}' --agent finance -p "查询金价"  \
       --agent finance \
       -p "获取今日 Au9999 金价，只要数字和单位" 

claude --allowedTools WebSearch \
       --effort low \
       --permission-mode bypassPermissions \
       --system-prompt "你是一个搜索引擎，当用户需要金融、股票等数据时，当务必使用 WebSearch 获取实时数据" \
       -p "获取今日 Au9999 金价，只要数字和单位" 


        