# -*- coding: utf-8 -*-\
import numpy as np
import autograd as ad

# =============================================================================
# IMPORTANT (MATHEMATICAL) NOTE
# what is named here as gradient, is a wrong denomination
# as we are dealing with vector function, the right word to use is more Jacobian
# =============================================================================

class Block():
    """
    main class for the blocks of the AD package. The several blocks will be of several types
    For now we envision two types of block : simple and double, depending on the number of
    variables as input.
    For instance :
        sin(.) is a simple block as it has only one input

        dot(.,.) is a double block as it has two inputs


    NOTE : Maybe we should define the following functions as class methods
    This way we will not have to instantiate these class to use them.
    for instance instead of doing :
        import sin
        sinBlock = sin()
        y=sinBlock(x)

    we could have an implementation like :
        import sin
        y=sin(x)
    """



    def data_fn(self,*args, **kwargs):
        """
        function to apply to the input Variable.
        for instance :
            sin.data_fn(x) will return sin(x)
        """
        raise NotImplementedError

    def get_jacobians(self, *args, **kwargs):
        """
        get the jacobians of the current block, evaluated at the input.data point

        we specify jacobianS as we want to have the jacobian of the ouput of the block with respect
        to each of the inputs
        """
        raise NotImplementedError



    def gradient_forward(self, *args, **kwargs):
        """
        function implementing the forward pass of the gradient.

        Let's consider a computational graph which transforms
        x_0 --> x_1 --> x_2 --> x_3 --> y
        let's call the output of that block y, then the output of
        gradient_forward(x3), will contain the jacobian of the function x_0 --> y

        this function is in charge of pushing the gradients forward, it will combine the
        previously computed gradients to the derivative of this block_function



        this function will depend on wether this is a simple block or a double block.
        for instance :
            sin.gradient_forward(x) will return grad(x) * cos(x)

            multiply(x,y) will return : grad(x)*y + x*grad(y)
        """
        """
        (x + y)' = x' + y'
        """
        #operator_check(args)

        #concatenate the input gradients
        input_grad = np.concatenate([var.gradient for var in args], axis=0)

        #concatenate the jacobians
        jacobians = self.get_jacobians(*args, **kwargs)
        jacobian = np.concatenate([jacob for jacob in jacobians], axis=1)

        new_grad = np.matmul(jacobian, input_grad)
        return(new_grad)

    def __call__(self, *args, **kwargs):
        """
        applies the forward pass of the data and the gradient.
        returns a new variable with the updated information on data and gradient.
        """
        #python circular import fix
        if not 'Variable' in dir():
            from autograd.variable import Variable


        new_data=self.data_fn(*args, **kwargs)

        #in forward mode, we force the flow of gradients with the dats
        if ad.mode=='forward':
            new_grad=self.gradient_forward(*args, **kwargs)

            #in forward mode, we return a full Variable, with gradients
            return(Variable(new_data, new_grad))



        else:
            #reverse mode, we will make a forward pass on the data but will store the jacobians
            # we pay attention not to include the Constants in the computational graph
            input_variables =[]
            variables_indexes=[]
            for index, arg in enumerate(args):
                if type(arg)==Variable:
                    input_variables+=[arg]
                    variables_indexes+=[index]

            children_nodes = [var.node for var in input_variables]
            children_jacs = self.get_jacobians(*args, **kwargs)

            #in reverse mode, the Variable does not store the gradients
            outputVariable = Variable(new_data)


            for i in variables_indexes:
                outputVariable.node.childrens+=[{'node':children_nodes[i], 'jacobian':children_jacs[i]}]

                #increase the counter
                children_nodes[i].times_used +=1

            return(outputVariable)








class SimpleBlock(Block):
    """
    this block is meant to implement one-variable functions that have been vectorized :
        sin(vector) is the vector of coordinates (sin(vector[i]))

    For this, these functions are functions from Rn to Rn and they have a Jacobian which is
    a square matrix, with elements only on the diagonal
    """
    def gradient_fn(self, *args, **kwargs):
        """
        function implementing the gradient of data_fn, when it is easy to express
        for instance :
            sin.gradient_fn(x) will return cos(x)
        """
        raise NotImplementedError


    def get_jacobians(self, *args, **kwargs):
        """
        get the Jacobian matrix of the simple block. It is a diagonal matrix easy to build from the
        derivative function of the simpleBlock
        """
        #get the elements of the diagonal
        elts = self.gradient_fn(*args, **kwargs)
        jacobian = np.diag(elts)
        return([jacobian])
