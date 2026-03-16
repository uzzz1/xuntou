'''
Author: HideInTower 1075277345@qq.com
Date: 2026-02-26 11:19:13
LastEditors: HideInTower 1075277345@qq.com
LastEditTime: 2026-03-16 17:11:00
Description: 

Copyright (c) 2026 by ${git_name_email}, All Rights Reserved. 
'''
import logging
import os
from model import model
import time
from datetime import datetime
log_dir = "./logs"

def setup_logging():
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    # 配置根日志器 (Root Logger) 或者配置一个特定的顶级 logger
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(asctime)s %(filename)s:%(lineno)d %(message)s",
        handlers=[
            logging.StreamHandler(),  # 输出到控制台
            logging.FileHandler(f'./logs/xt_trader_{datetime.now().strftime("%Y-%m-%d")}.log', encoding='utf-8')
        ]
    )

if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Trading start")
    from core import PositionManager
    PositionManager.position_instance.run()