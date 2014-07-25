import logging

class AbstractFactory(object):

    def __init__(self):
        pass

    def create_factory(self, ftype=''):
        if ftype == 'jobs':
            logging.info("AbstFact: Getting jobs server factory")
            factory = ServerFactory(ftype)
        else:
            logging.info("AbstFact: Getting rpc server factory")
            factory = RPCFactory()
        return factory

class ServerFactory(object):

    def __init__(self, ftype):
        self.srv_module = None
        self.producer = None
        if ftype == 'jobs':
            self.srv_module = __import__(ftype)
            self.producer = self.srv_module.Jobber()

    def create_RPC_obj(self):
        return self.producer


class RPCFactory(object):

    def __init__(self):
        self.rpc_object = __import__('rpc_object')
        self.producer = self.rpc_object.RPC_Object()

    def create_RPC_obj(self):
        return self.producer

if __name__ == '__main__':
    abs_fact = AbstractFactory()
    fact = abs_fact.create_factory('jobs')
    jobber = fact.create_RPC_obj()
    try:
        jobber.get_a_job()
    except sqlite3.OperationalError:
        print 'DB Error. Did you run init_db.py?'
