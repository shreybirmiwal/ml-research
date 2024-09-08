import random

#random data with a negative linear relationship (i just asked gpt to generate these nums)
x = [2.5, 3.1, 3.8, 4.2, 4.7, 5.1, 5.5, 5.9, 6.3, 6.8, 7.2, 7.6, 8.1, 8.5, 9.0, 9.4]
y = [11.5, 10.8, 9.5, 8.3, 7.8, 7.2, 6.9, 6.1, 5.7, 5.1, 4.9, 4.2, 3.8, 3.1, 2.7, 2.1]

def getLoss(m, b):
    overall_loss = 0

    #loop through each data point, determine how far away the predicted y value is from the actual y value and add the loss to overall loss
    for i in range(len(x)):
        x_val = x[i]
        y_val = y[i]
        predicted_y = m * x_val + b
        loss = abs(predicted_y - y_val)
        overall_loss += loss

    
    return overall_loss



m = random.uniform(-10, 10) #slope (weight) (m)
b = random.uniform(-10, 10) #y intercept (bias) (b)

loss = 999
learning_rate = 0.0001
epoch = 0

while loss > 1:
    loss = getLoss(m, b)
    print("Loss: ", loss, "m: ", m, "b: ", b, "Epoch: ", epoch)

    dm_respect_to_loss = (getLoss(m + 0.01, b) - getLoss(m, b)) / 0.01
    db_respect_to_loss = (getLoss(m, b + 0.01) - getLoss(m, b)) / 0.01

    m -= dm_respect_to_loss * learning_rate
    b -= db_respect_to_loss * learning_rate

    epoch += 1


