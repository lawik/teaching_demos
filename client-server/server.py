from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory
import logging
import json

log = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)

users = {}
blacklisted_names = ('<nameless>')

class ChatServerProtocol(WebSocketServerProtocol):
    @classmethod
    def emit(cls, data):
        for protocol, username in users.iteritems():
            protocol.send(data)

    @classmethod
    def emitUserList(cls, new=False, left=False):
        userlist = {
            'type': 'userlist',
            'users': [username for username in users.values()],
            'new': new,
            'left': left,
        }
        cls.emit(userlist)

    @classmethod
    def emitMessage(cls, username, message):
        message = {
            'type': 'message',
            'user': username,
            'message': message
        }
        cls.emit(message)

    def onConnect(self, request):
        log.info("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        log.info("WebSocket connection open.")
        users[self] = '<nameless>'

    def onMessage(self, payload, isBinary):
        if isBinary:
            log.info("Binary message received: {0} bytes".format(len(payload)))
        else:
            # log.info("Text message received: {0}".format(payload.decode('utf8')))
            try:
                data = json.loads(payload)
                self.handleMessage(data)
            except:
                self.errorResponse('Could not parse JSON.', payload)

    def send(self, data):
        try:
            data_string = json.dumps(data)
            self.sendMessage(data_string)
        except:
            self.errorResponse("An error occurred when formulating your response. A JSON issue :(", False)

    def onClose(self, wasClean, code, reason):
        log.info("WebSocket connection closed: {0}".format(reason))
        if users[self]:
            left = users[self]
            del users[self]
            self.emitUserList(left=left)
        else:
            # silent removal
            del users[self]

    def handleMessage(self, data):
        try:
            if data['type'] == 'set_name':
                # log.info("Received name change. From %s to %s." % (users[self], data['name']))
                if data['name'] not in blacklisted_names and data['name'] not in users.values():
                    users[self] = data['name']
                    log.info("Name change done. Updating user lists.")
                    self.emitUserList(new=users[self]) # Send userlist to everyone, it has changed
                else:
                    log.info("Name change not allowed.")
                    self.errorResponse("Could not change username. It is not available.", data)
            if data['type'] == 'message':
                message = unicode(data['message'])
                # log.info("Received chat message: %s" % message)
                username = users[self]
                self.emitMessage(username, message)
        except:
            log.exception("Could not handle message, caught exception:")
            self.errorResponse("Could not handle message. Please try something else.", data)

    def errorResponse(self, error_message, data=None):
        error_data = {
            'type': 'error',
            'error': error_message,
            'data': data
        }
        self.send(error_data)

if __name__ == '__main__':

    from twisted.internet import reactor

    factory = WebSocketServerFactory("ws://localhost:9000", debug=False)
    factory.protocol = ChatServerProtocol
    # factory.setProtocolOptions(maxConnections=2)

    reactor.listenTCP(9000, factory)
    log.info("Running server...")
    reactor.run()
