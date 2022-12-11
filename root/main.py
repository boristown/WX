import werobot
import handle
from werobot.session.filestorage import FileStorage

robot = werobot.WeRoBot(token='ZeroAI')

@robot.text
def hello(message):
    return handle.chat(message.content,message.source,message.target,message.time)

robot.config['HOST'] = '0.0.0.0'
robot.config['PORT'] = 80
robot.run()