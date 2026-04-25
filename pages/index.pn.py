# panel 就比较简单了
import panel as pn

pn.extension(notifications=True)  # 确保启用前端通知系统

# 自定义异常处理，直接在前端弹出通知
def exception_handler(exc):
    pn.state.notifications.error(str(exc))

pn.config.exception_handler = exception_handler

_button = pn.widgets.Button(name="测试弹出异常")

def _reconnect(event):
    # 模拟异常
    raise ValueError("这是一个测试异常")

_button.on_click(_reconnect)

pn.Column(_button).servable()
