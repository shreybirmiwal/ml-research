class val:
    def __init__(self, data, children=(), op='leaf'):
        self.data = data
        self.grad = 0
        self.children = children
        self.op = op

    def ret(self):
        print("Data: ", self.data)
        if (len(self.children) > 0):
            print("Child 1: ", self.children[0].data)
            print("Child 2: ", self.children[1].data)
            print("Op: ", self.op)
            print("Grad: ", self.grad)
            print("Grad 1: ", self.children[0].grad)
            print("Grad 2: ", self.children[1].grad)
        print("#################")
    
    def __add__(self, other):
        return val(self.data + other.data, (self, other), '+')

    def __mul__(self, other):
        return val(self.data * other.data, (self, other), '*')
    

    def backward(self):
        topo_order = []
        visited = set()

        def build_topo(node):
            if node not in visited:
                visited.add(node)
                for child in node.children:
                    build_topo(child)
                topo_order.append(node)

        build_topo(self)

        self.grad = 1  # Seed the gradient
        for node in reversed(topo_order):

            print("Node: ", node.data)
            if node.op == '+':
                node.children[0].grad += 1 * node.grad
                node.children[1].grad += 1 * node.grad
            elif node.op == '*':
                node.children[0].grad += node.children[1].data * node.grad
                node.children[1].grad += node.children[0].data * node.grad
            
            print("Grad: ", node.grad)
            if (len(node.children) > 0):
                print("Grad 1: ", node.children[0].grad)
                print("Grad 2: ", node.children[1].grad)
            print("#################")
    

    # def getAllChildren(self):
    #     out = []
    #     if (len(self.children) > 0):
    #         for i in self.children:
    #             i.getAllChildren()
            
    #         out.append(self.children[0])
    #         out.append(self.children[1])
    #     print(self.data)
    
    # def backward(self):

    #     self.grad = 1
    #     # top grad = 1

    #     #build a order of what nodes to do back on


    #     if (len(self.children) > 0):
    #         if self.op == '+':
    #             self.children[0].grad += 1 * self.grad
    #             self.children[1].grad += 1 * self.grad

    #         if self.op == '*':
    #             self.children[0].grad += self.children[1].data * self.grad
    #             self.children[1].grad += self.children[0].data * self.grad

    #         self.children[0].backward()
    #         self.children[1].backward()
    




# example neuron (minimize)
inp_x = val(3)
inp_y = val(4)
w = val(2)
b = val(4)


xw = inp_x * w
yw = inp_y * w

weights = xw + yw
z = weights + b

z.backward()
z.ret()
weights.ret()
yw.ret()
xw.ret()




class neuron():

    def __init__(self, inps):
        self.inps = inps
        self.w = val(2)
        self.b = val(2)
        self.z = val(0)
        # these shd be random

    def forward(self):
        sum = val(0)
        for i in range(len(self.inps)):
            xw = val(self.inps[i]) * self.w
            sum += xw

        z = sum + self.b
        self.z = z
        return z

    def backward(self):
        self.z.backward()
        self.w.ret()
        self.b.ret()
        self.z.ret()


class layer():
    neuron([3, 4])
    neuron([4, 5])
    neuron([5, 6])

    


x = neuron([3,4]).forward()
x.z.backward()



