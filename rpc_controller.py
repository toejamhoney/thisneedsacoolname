# Python Modules
import logging

# Voodo Modules
import rpc_factory


class Controller(object):

    def __init__(self, ftype):
        self.abs_factory = rpc_factory.AbstractFactory()
        self.factory = self.abs_factory.create_factory(ftype)
        self.rpc_obj = self.factory.create_RPC_obj()
    
    def call(self, method, args):
        ret_val = 'rpc_controller.Controller.call() entry'
        try:
            logging.info('method(args)')
            ret_val = method(args)
        except (TypeError, Exception) as t_err:
            if '() takes' in str(t_err):
                try:
                    ret_val = method()
                except Exception as err:
                    import traceback
                    ret_val = traceback.format_exc() + str(err)
                    logging.debug('Controller.call() method()' + ret_val)
            else:
                import traceback
                ret_val = traceback.format_exc() + str(t_err)
                logging.debug('Controller.call(method(args)): ' + ret_val)
        finally:
            return ret_val

    def dispatch(self, dic):
        ret_val = {}
        mth_name = dic.get('method')
        try:
            logging.info('Finding ' + str(dic.get('method')))
            method = getattr(self.rpc_obj, mth_name)
        except AttributeError as err:
            logging.debug('Method not found:',repr(err))
            ret_val = 'Dispatch():' + repr(err)
        else:
            params = dic.get('parameters')
            logging.info('Method params:' + str(dic.get('parameters')))
            ret_val = self.call(method, params)
        finally:
            return ret_val

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.info('Begin RPC Controller test')
    #ctrl = Controller('jobs')
    #$result = ctrl.dispatch( {'method':'get_a_job'} )
    #print 'Controller test response:', result
    ctrl2 = Controller('rpc')
    result = ctrl2.dispatch( {'method':'echo', 'parameters':{'stuff':'value'}} )
    print 'Controller rpc response:', result
    result = ctrl2.dispatch( {'method':'pin', 'parameters':{'stuff':'value'}} )
    print 'Controller rpc response:', result
