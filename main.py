# -*- coding: utf-8 -*-
# filename: main.py
import web
from handle import Handle

urls = (
    '/wx', 'Handle',
    '/','hello'
)

class hello:
    def GET(self):
        raiseweb.seeother('https://www.forcastline.com')

if __name__ == '__main__':
    app = web.application(urls, globals())
    app.run()
