import random
import math

#correct: input * 3 = output

learning_rate = .01

def getCorrect(input):
    hiddenLayer1 = input * 3
    return hiddenLayer1

def getLossFunction(expected, actual):
    return math.pow(actual-expected,2)

#tarting weights and bias as random
layer1_weight = random.randrange(-5, 5, 1)
print("Inital random weight", layer1_weight )

for epoch in range (1, 20):
    
    curSum = 0
    for i in range(100):
    
        input_num = random.randrange(-10, 10, 1)
        expected_out = getCorrect(input_num)
    
        #forward prop
        predicted_layer1 = input_num * layer1_weight
        MSE_Loss_Function = (expected_out-predicted_layer1) #squared difference
    
        #print("input", input_num)
        #print("layer results ", predicted_layer1)
        #print("Expected", expected_out)
        #print("loss ", MSE_Loss_Function)
    
        # how much is the weight changing the output and how far are we?
        upper_bound = getLossFunction(getCorrect(input_num + .01), (input_num+.01)*layer1_weight)
        lower_bound = getLossFunction(getCorrect(input_num - .01), (input_num-.01)*layer1_weight)

        approx_slope = (upper_bound - lower_bound)/.02

        #print("Approx slope ", approx_slope)

        layer1_weight +=  learning_rate * approx_slope
        
        #if approx_slope_of_weight > 0:
        #layer1_weight = learning_rate * approx_slope_of_weight
            #layer1_weight-=newLearningRate
            
        #this means the loss func in increasing if we go in + direction
        #else:
            #layer1_weight += curLearningRate * approx_slope_of_weight
            #layer1_weight += newLearningRate   
    
        #print("updated weights")
    
        curSum += MSE_Loss_Function
    
    print("AVERAGE LOSS EPOCH" + str(epoch) + "loss:" + str(curSum/100) + " Current weight: " + str(layer1_weight))
        
    