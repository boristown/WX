import werobot
from werobot.session.filestorage import FileStorage
import sys

robot = werobot.WeRoBot(token='ZeroAI')

@robot.text
def hello(message):
    return '维护中，预计北京时间2022-12-11 23点恢复。'

robot.config['HOST'] = '0.0.0.0'
robot.config['PORT'] = 80
robot.run()