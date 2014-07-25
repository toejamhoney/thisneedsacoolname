import SocketServer
import config
import json
import logging
import sys
import rpc_controller

class Voodo_Server(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True
    daemon_threads = True
    
    def __init__(self, server_address, RequestHandlerClass):
        SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass)
        logging.info('Voodo serving on: %s', server_address)


class Voodo_Job_Server(SocketServer.ForkingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True

    def __init__(self, server_address, RequestHandlerClass, srv_type='jobs'):
        self.remote_ctrl = rpc_controller.Controller(srv_type)
        SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass)
        logging.info('Voodo Job (%s) serving on: %s', srv_type, server_address)


class Voodo_RPC_Server(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True
    
    def __init__(self, server_address, RequestHandlerClass, srv_type=''):
        self.remote_ctrl = rpc_controller.Controller(srv_type)
        SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass)
        logging.info('Voodo RPC serving on: %s', server_address)


class VoodoBaseHandler(SocketServer.BaseRequestHandler):

    def __init__(self, request, client_address, server):
        self.header = ''
        self.msg_len = 0
        self.msg = ''
        self.ret_val = False 
        SocketServer.BaseRequestHandler.__init__(self, request, client_address, server)

    def setup(self):
        logging.info('VoodoBaseHandler.setup()...')
        pass

    def handle(self):
        logging.debug('VoodoBaseHandler.handle()')
        self.get_header()
        if not self.verify_header():
            return False
        self.get_msg_len()
        self.get_msg()
        logging.info('Msg Recvd (%d bytes): [%s]', self.msg_len, self.msg)
    
    def transmit(self, data):
        logging.debug('VoodoBaseHandler.transmit()')
        bytes_total = len(data)
        bytes_sent = self.request.send(data)
        while bytes_sent < bytes_total:
            bytes_sent += self.request.send(data[bytes_sent:])

    def finish(self):
        logging.debug('VoodoBaseHandler.finish()')
        try:
            logging.info('JSON Encoding...')
            response = json.dumps(self.ret_val)
        except Exception as err:
            logging.debug('JSON Failed...')
            response = repr(err)
        logging.info('Creating header...')
        header = self.create_header(len(response))
        self.transmit(header)
        logging.info('Header sent...')
        self.transmit(response)
        logging.info('Response sent...\n\n')
    
    def create_header(self, data_len):
        return "_{0:010d}_".format(data_len)

    def get_header(self):
        logging.debug('Getting header')
        self.header = self.request.recv(12)

    def verify_header(self):
        logging.debug('VoodoBaseHandler.verify_header()')
        if self.header[0] != '_' or self.header[11] != '_':
            logging.debug('Header is not right: %s..........%s', self.header[0], self.header[11])
            return False
        self.header = self.header.strip('_')
        return True
    
    def get_msg_len(self):
        self.msg_len = int(self.header)
        
    def get_msg(self):
        recvd = 0
        while recvd < self.msg_len:
            self.msg += self.request.recv(self.msg_len - recvd)
            recvd += len(self.msg)


class RPCRequestHandler(VoodoBaseHandler):

    def __init__(self, request, client_address, server):
        self.method = None
        self.params = None
        VoodoBaseHandler.__init__(self, request, client_address, server)
        # Super class props:
        #    self.header = ''
        #    self.msg_len = 0
        #    self.msg = ''
        #    self.ret_val = False
        
    def handle(self):
        VoodoBaseHandler.handle(self)
        call_dict = self.unmarshall()
        logging.debug('Handle() Unmarshall:' + str(call_dict))
        self.ret_val = self.server.remote_ctrl.dispatch(call_dict)
        logging.debug('Handle() Result:' + str(self.ret_val))
       
    def unmarshall(self):
        ret_val = None
        try:
            ret_val = json.loads(self.msg)
        except Exception as error:
            logging.warn('Unmarshall() error: %s', error)
            logging.warn('<%s>', str(self.msg))
            self.ret_val = False
            raise error
        else:
            return ret_val


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    try:
        srv_type = sys.argv[1]
    except IndexError:
        srv_type = ''
    if srv_type.startswith('job'):
        port = config.SETTINGS.get('JOB_PORT')
        srv = Voodo_Job_Server( ('0.0.0.0', port), RPCRequestHandler, "jobs")
    else:
        port = config.SETTINGS.get('NEW_PORT')
        srv = Voodo_RPC_Server( ('0.0.0.0', port), RPCRequestHandler, srv_type)
    srv.serve_forever()
