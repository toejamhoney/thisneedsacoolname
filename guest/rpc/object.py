class RPC_Object(object):
    
    def __init__(self):
        self.name = ''
        self.err_num = 0
        self.errors = { 0: 'RPC module not found in guest_tools: ',
                       1: 'Tool is not correct. rpc_hook() not found in: '}
    
    def __getattr__(self, name):
        ret_val = ''
        self.name = name
        try:
            pkg = __import__('guest_tools.' + name)
        except ImportError:
            self.err_num = 0
            ret_val = self.error
        else:
            module = getattr(pkg, name)
            try:
                ret_val = getattr(module, 'rpc_hook')
            except AttributeError:
                self.err_num = 1
                ret_val = self.error
        finally:
            return ret_val
    
    def error(self, args=None):
        return self.errors.get(self.err_num) + self.name
        
            
if __name__ == '__main__':
    obj = RPC_Object()
    method = getattr(obj, 'pin')
    result = method()
    print result
