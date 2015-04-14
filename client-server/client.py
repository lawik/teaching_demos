from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory
import logging
from threading import Thread
from twisted.internet import reactor
import time
import json

log = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)


class ChatClientProtocol(WebSocketClientProtocol):
    def onConnect(self, response):
        #log.info("Server connected: {0}".format(response.peer))
        print "Connecting..."

    def onOpen(self):
        self.userlist = None
        #log.info("WebSocket connection open.")
        print "Connected."
        name = raw_input("Enter a username:")
        self.setName(name)

    def onMessage(self, payload, isBinary):
        if isBinary:
            log.info("Binary message received: {0} bytes".format(len(payload)))
        else:
            log.info("Text message received: {0}".format(payload.decode('utf8')))
            try:
                data = json.loads(payload)
                self.handleMessage(data)
            except:
                log.error('Could not parse JSON.', payload)

    def onClose(self, wasClean, code, reason):
        log.info("WebSocket connection closed: {0}".format(reason))

    def setName(self, name):
        data = {
            'type': 'set_name',
            'name': name,
        }
        self.send(data)

    def message(self, message):
        data = {
            'type': 'message',
            'message': message,
        }
        self.send(data)

    def send(self, data):
        try:
            data_string = json.dumps(data)
            self.sendMessage(data_string)
        except:
            log.error("An error occurred when formulating your message. A JSON issue :(")

    def handleMessage(self, data):
        if data['type'] == 'userlist':
            print "Received a new userlist:"
            print data['users']
            self.userlist = data['users']
            self.message("My first message, automated.")
        if data['type'] == 'message':
            print data['message']
        if data['type'] == 'error':
            log.error("Server reported an error: %s" % data['error'])


def start_client(endpoint):
    factory = WebSocketClientFactory(endpoint, debug=False)
    factory.protocol = ChatClientProtocol

    reactor.connectTCP("127.0.0.1", 9000, factory)
    reactor.run()

if __name__ == '__main__':
    endpoint = "ws://localhost:9000"
    # client_thread = threading.Thread(target=start_client, args=(endpoint))
    # client_thread.daemon = True
    # client_thread.start()
    start_client(endpoint)

    # while True:
    #     written = input()
    #     if written.startswith('/name'):
    #         new_name = written.replace('/name ')
