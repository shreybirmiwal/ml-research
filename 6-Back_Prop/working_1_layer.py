import random
import math

learning_rate = .01

def getCorrect(input):
    hiddenLayer1 = input * 3 + .6
    return hiddenLayer1

def getLossFunction(expected, actual):
    return abs(actual-expected)

#initialize the starting weights and bias as random
layer1_weight = random.uniform(20, 50)  
bias = random.uniform(-20, 20) 
print("Initial random weight:", layer1_weight)
print("Initial random bias:", bias)

AverageLoss = 10
AverageLoss = 10
curEpoch = 0

while(AverageLoss > 0.01):
    curEpoch += 1
    curSum = 0
    for i in range(500):

        input_num = random.randrange(-10, 10, 1)
        expected_out = getCorrect(input_num)

        #forward prop
        predicted_layer1 = input_num * layer1_weight + bias

        #print("input", input_num)
        #print("layer results ", predicted_layer1)
        #print("Expected", expected_out)
        #print("loss ", MSE_Loss_Function)

        # how much is the weight changing the output and how far are we?
        old_weight = layer1_weight

        #WEIGHT
        upper_bound = getLossFunction(getCorrect(input_num + 0.01), (input_num + 0.01) * layer1_weight + bias)
        lower_bound = getLossFunction(getCorrect(input_num - 0.01), (input_num - 0.01) * layer1_weight + bias)
        approx_slope_weight = (upper_bound - lower_bound) / 0.02
        layer1_weight += learning_rate * approx_slope_weight


        #BIAS
        upper_bound = getLossFunction(getCorrect(input_num), (input_num) * old_weight + bias + 0.01)
        lower_bound = getLossFunction(getCorrect(input_num), (input_num) * old_weight + bias - 0.01)
        approx_slope_bias = (upper_bound - lower_bound) / 0.02
        bias -= learning_rate * approx_slope_bias



        curSum += getLossFunction(getCorrect(input_num),predicted_layer1)


    #break
    AverageLoss = curSum / 100


    print("EPOCH " + str(curEpoch) + " loss:" + str(AverageLoss) + " Current weight: " + str(layer1_weight) + " Current bias: " + str(bias))

