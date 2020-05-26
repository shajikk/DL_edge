#  Answers to Question 2

### Name all the layers in the network, describe what they do.

Input is 24x24 = grayscale image :
```javascript
layer_defs.push({type:'input', out_sx:24, out_sy:24, out_depth:1});
```

8 5x5 filters will be convolved with the input :
```javascript
layer_defs.push({type:'conv', sx:5, filters:8, stride:1, pad:2, activation:'relu'});
```

Performs max pooling :
```javascript
layer_defs.push({type:'pool', sx:2, stride:2});
```

16 5x5 filters will be convolved with the input :
```javascript
layer_defs.push({type:'conv', sx:5, filters:16, stride:1, pad:2, activation:'relu'});
```

Performs max pooling :
```javascript
layer_defs.push({type:'pool', sx:3, stride:3});
```

Softmax layer. In softmax, the outputs are probabilities that sum to 1 :
```javascript
layer_defs.push({type:'softmax', num_classes:10});
```

### Experiment with the number and size of filters in each layer. Does it improve the accuracy?
I don't observe any significant change in accuracy.

### Remove the pooling layers. Does it impact the accuracy?
It does not affect accuracy.

### Add one more conv layer. Does it help with accuracy?
No, accuracy drops after adding one more conv layer

### Increase the batch size. What impact does it have?
The loss is getting a bit choppy.

### What is the best accuracy you can achieve? Are you over 99%? 99.5%?
The best I have seen is 97%

