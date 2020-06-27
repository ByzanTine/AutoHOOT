import numpy as np
import ctf
from .core import Backend


class CTFBackend(Backend):
    backend_name = 'ctf'

    @staticmethod
    def context(tensor):
        return {'dtype': tensor.dtype}

    @staticmethod
    def tensor(data, dtype=None):
        return ctf.astensor(data, dtype=dtype)

    @staticmethod
    def is_tensor(tensor):
        return isinstance(tensor, ctf.core.tensor)

    @staticmethod
    def to_numpy(tensor):
        return ctf.to_nparray(tensor)

    @staticmethod
    def shape(tensor):
        if isinstance(tensor, float):
            return ()
        return tensor.shape

    @staticmethod
    def ndim(tensor):
        return tensor.ndim

    @staticmethod
    def sqrt(tensor):
        raise NotImplementedError

    @staticmethod
    def max(tensor):
        raise NotImplementedError

    @staticmethod
    def inv(matrix):
        U, s, V = ctf.svd(matrix)
        return ctf.dot(ctf.transpose(V),
                       ctf.dot(ctf.diag(s**-1), ctf.transpose(U)))

    @staticmethod
    def tensorinv(tensor, ind=2):
        oldshape = tensor.shape
        if ind > 0:
            invshape = oldshape[ind:] + oldshape[:ind]
            prod = np.prod(oldshape[:ind])
            assert prod == np.prod(oldshape[ind:])
        else:
            raise ValueError("Invalid ind argument.")
        tensor = tensor.reshape(prod, -1)
        invtensor = CTFBackend.inv(tensor)
        return invtensor.reshape(*invshape)

    @staticmethod
    def einsum(subscripts, *operands):
        # This is because ctf cannot deal with the einsum of two scalars: einsum(",->", a, b)
        if len(operands) == 2 and len(operands[0].shape) == 0 and len(
                operands[1].shape) == 0:
            return operands[0] * operands[1]
        return ctf.einsum(subscripts, *operands)

    @staticmethod
    def power(a, b):
        if isinstance(a, ctf.core.tensor):
            return ctf.power(a, b)
        else:
            return np.power(a, b)

    @staticmethod
    def norm(tensor, order=2, axis=None):
        # handle difference in default axis notation
        if axis == ():
            axis = None
        if axis != None:
            raise NotImplementedError

        if order == 'inf':
            return tensor.norm_infty()
        elif order == 1:
            return tensor.norm1()
        elif order == 2:
            return tensor.norm2()
        else:
            raise NotImplementedError

    @staticmethod
    def array_equal(a, b):
        return np.array_equal(ctf.to_nparray(a), ctf.to_nparray(b))

    @staticmethod
    def ones_like(tensor):
        return ctf.ones(CTFBackend.shape(tensor))

    @staticmethod
    def zeros_like(tensor):
        return ctf.zeros(CTFBackend.shape(tensor))


for name in [
        'reshape', 'transpose', 'copy', 'qr', 'ones', 'zeros', 'eye', 'abs',
        'dot', 'sum', 'identity', 'solve_tri', 'cholesky', 'diag', 'svd',
        'eigh', 'tensordot'
]:
    CTFBackend.register_method(name, getattr(ctf, name))

for name in ['random', 'seed']:
    CTFBackend.register_method(name, getattr(ctf.random, name))
