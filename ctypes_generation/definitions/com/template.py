import functools
import ctypes


generate_IID = IID.from_raw


class COMHRESULT(HRESULT):
    _type_ = HRESULT._type_
    def _check_retval_(self):
        # We CAN NOT try to adapt the self.value and transform it with flags
        # here, we need to do it with the errcheck
        # So we have the peer-interface callback system on errcheck :)
        return self.value # The value will be send to errcheck :)

class COMInterface(ctypes.c_void_p):
    _functions_ = {
    }

    # So COMInterface completely bypass the HRESULT
    # return value check on restype by setting the restype to COMHRESULT
    # But we add the 'errcheck' callbakc capacity for all COMInterface and subclasses
    # So the default implem of the callbakc must have the same behavior as
    # standard HRESULT restype.
    # This is why default errcheck callback call ctypes._check_HRESULT
    def _default_errcheck(self, result, func, args):
        ctypes._check_HRESULT(result)
        return args

    def __getattr__(self, name):
        if name in self._functions_:
            winfunc = self._functions_[name]
            # Hacking the HRESULT _check_retval_ and
            # letting COMInterface.errcheck do the work of validating / raising
            winfunc.restype = COMHRESULT
            effective_errcheck = getattr(self, "errcheck", self._default_errcheck)
            winfunc.errcheck = effective_errcheck
            return functools.partial(winfunc, self)
        return super(COMInterface, self).__getattribute__(name)

    def __repr__(self):
        description = "<NULL>" if not self.value else ""
        return "<{0}{1} at {2:#x}>".format(type(self).__name__, description, id(self))

    # Simplified API for QueryInterface for interface embeding there IID
    def query(self, interfacetype):
        interface = interfacetype()
        self.QueryInterface(interface.IID, interface)
        return interface









