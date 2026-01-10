# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


import os
import sys
from loguru import logger

def main():
    logger.info("启动量化交易系统...")
    # 默认启动 Streamlit UI
    os.system("streamlit run src/ui/app.py")

if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
