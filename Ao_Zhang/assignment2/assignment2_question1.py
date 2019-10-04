"""
CSI 5138: Assignment 2 ----- Question 1
Student:            Ao   Zhang
Student Number:     0300039680
"""
##### for plotting through X11 #####
# import matplotlib
# matplotlib.use("tkagg")
# ##### set specific gpu #####
# import os
# os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
# os.environ["CUDA_VISIBLE_DEVICES"]="1"
##### other dependencies #####
# import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np
from tqdm import tqdm
from multiprocessing import Process

class QuestionOne:
    def __init__(self, K):
        """
        Args:
            k               ->              dimension of input vector X
        """ 
        self.K = K
        self.X = tf.placeholder(tf.float32, shape = (None, self.K, 1))
        self.A = tf.Variable(tf.glorot_uniform_initializer()((self.K, self.K)))
        self.B = tf.Variable(tf.glorot_uniform_initializer()((self.K, self.K)))
        self.learning_rate = 0.01

    ###################################################################
    # define all functions and its relative gradients
    ###################################################################
    def FuncLinear(self, var1, var2):
        """
        Function: y = A * x
        """
        return tf.matmul(var1, var2)

    def GradientLinear(self, var1, var2):
        """
        Function: \partial{grad(y)}{var1} = x; \partial{grad(y)}{var1} = A; 
        """
        length = tf.shape(self.X)[0]
        return tf.transpose(var2, perm = [0, 2, 1]), \
                tf.reshape(tf.tile(tf.transpose(var1), tf.constant([length])), [length, self.K, self.K])

    def Sigmoid(self, var):
        """
        Function: Sigmoid
        """
        return 1. / (1. + tf.exp( - var))

    def GradientSigmoid(self, var):
        """
        Function: grad(sigmoid) = sigmoid * (1 - sigmoid)
        """
        return self.Sigmoid(var) * (1 - self.Sigmoid(var))

    def FuncMultiplication(self, var1, var2, var3):
        """
        Function: y = A * (u * v)
        """
        return tf.matmul(var1, (var2 * var3))

    def GradientMultiplication(self, var1, var2, var3):
        """
        Function: \partial{grad(y)}{var1} = var2 * var3
        """
        return tf.transpose(var2 * var3, perm = [0, 2, 1]), \
                tf.transpose(tf.matmul(var1, var3), perm = [0, 2, 1]), \
                tf.transpose(tf.matmul(var1, var2), perm = [0, 2, 1])

    def EuclideanNorm(self, var):
        """
        Function: Euclidean Norm(X)
        """
        return tf.reduce_sum(tf.square(var))
    
    def GradientEuclideanNorm(self, var):
        """
        Function: 2*x_1, 2*x_2, ... , 2*x_n
        """
        return 2 * var

    ###################################################################
    # calculate the forward graph, gradient graph and dual gradient
    ###################################################################
    def ForwardGradientGraph(self, name = "gradient"):
        """
        Function: Calculate loss function and forward gradient
        """
        y = self.FuncLinear(self.A, self.X)
        u = self.Sigmoid(y)
        v = self.FuncLinear(self.B, self.X)
        z = self.FuncMultiplication(self.A, u, v)
        omega = self.FuncLinear(self.A, z)
        loss = self.EuclideanNorm(omega)

        grad_y_A, grad_y_X = self.GradientLinear(self.A, self.X)
        grad_u_y = self.GradientSigmoid(y)
        grad_v_B, grad_v_X = self.GradientLinear(self.B, self.X)
        grad_z_A, grad_z_u, grad_z_v = self.GradientMultiplication(self.A, u, v)
        grad_omega_A, grad_omega_z = self.GradientLinear(self.A, z)
        grad_loss_omega = self.GradientEuclideanNorm(omega)

        grad_A = tf.matmul(tf.matmul(grad_omega_z, grad_loss_omega) * grad_z_u * grad_u_y, grad_y_A) \
                # + tf.matmul(tf.matmul(grad_omega_z, grad_loss_omega), grad_z_A) \
                # + tf.matmul(grad_loss_omega, grad_omega_A)

        grad_A = grad_y_A * grad_u_y * grad_z_u * grad_omega_z * grad_loss_omega \
                + grad_z_A * grad_omega_z * grad_loss_omega \
                + grad_omega_A * grad_loss_omega
        grad_B = grad_v_B * grad_z_v * grad_omega_z * grad_loss_omega

        if name == "loss":
            return loss
        elif name == "gradient":
            return grad_omega_z, grad_loss_omega
        else:
            raise ValueError("Namescope is wrong, please doublecheck the arguments")
    
    # def GradientGraph(self):
    #     """
    #     Function: Calculate forward gradient graph
    #     """
    #     grad_y_A, grad_y_X = self.GradientLinear(self.A)
    #     grad_u = self.GradientSigmoid(grad_y)
    #     grad_v = self.GradientLinear(self.B)
    #     grad_z = self.GradientMultiplication(self.A, grad_u, grad_v)
    #     grad_omega = self.GradientLinear(self.A) * grad_z
    #     grad_loss = self.GradientEuclideanNorm(grad_omega)
    #     return grad_loss

    def DualGradient(self):
        """
        Function: Dual gradient = gradient.transpose()
        """
        gradient_A, gradient_B = self.ForwardGradientGraph(name = "gradient")
        # Since the first dimension is the batch size, we should keep it in the first column
        dual_grad_A = tf.transpose(gradient_A, perm = [0, 2, 1])
        dual_grad_B = tf.transpose(gradient_B, perm = [0, 2, 1])
        return dual_grad_A, dual_grad_B

    def BackPropGradientDescent(self):
        """
        Function: Apply GD based on back propagation
        """
        grad_L_A, grad_L_B = self.DualGradient()
        learning_A = tf.add(self.A, - tf.reduce_sum(self.learning_rate * grad_L_A, \
                                                    axis = 0, keepdims=True))
        learning_B = tf.add(self.B, -  tf.reduce_sum(self.learning_rate * grad_L_B, \
                                                    axis = 0, keepdims=True))
        operation_A = self.A.assign(learning_A)
        operation_B = self.B.assign(learning_B)
        return operation_A, operation_B


if __name__ == "__main__":
    K = 5

    # fig = plt.figure()
    # ax1 = fig.add_subplot(111)

    Q_one =  QuestionOne(K)
    X_data = np.random.randint(10, size = (100, K, 1))

    gpu_options = tf.GPUOptions(allow_growth=True)
    sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))
    init = tf.initializers.global_variables()

    sess.run(init)

    # loss = Q_one.ForwardGradientGraph(name = "loss")
    # opA, opB = Q_one.BackPropGradientDescent()

    opA, opB = Q_one.ForwardGradientGraph()


    indall = []
    lossall = []
    i = 1
    # for i in range(1000):
    t1, t2 = sess.run([opA, opB], feed_dict = {Q_one.X: X_data})
    print(t1.shape)
    print(t2.shape)

        # sess.run([opA, opB], feed_dict = {Q_one.X: X_data})
        # test = sess.run(loss, feed_dict = {Q_one.X: X_data})
        # print(test)
        # indall.append(i)
        # lossall.append(test)

        # plt.cla()
        # ax1.clear()
        # ax1.plot(indall, lossall)
        # fig.canvas.draw()
        # plt.pause(0.1)        


    



