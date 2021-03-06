
import os, sys
sys.path.append("../..")

import tensorflow as tf
import tensorbuilder as tb

##############################
##### FUNCTIONS
##############################


##############################
##### builder
##############################

# The following example shows you how to construct a `tensorbuilder.builders.Builder` from a tensorflow Tensor.

import tensorflow as tf
import tensorbuilder as tb

a = tf.placeholder(tf.float32, shape=[None, 8])
a_builder = tb.builder(a)

# The previous is the same as

a_builder = tf.placeholder(tf.float32, shape=[None, 8]).builder()

##############################
##### branches
##############################

# Given a list of Builders and/or BuilderTrees you construct a `tensorbuilder.builders.BuilderTree`.

import tensorflow as tf
import tensorbuilder as tb

a = tf.placeholder(tf.float32, shape=[None, 8]).builder()
b = tf.placeholder(tf.float32, shape=[None, 8]).builder()

tree = tb.branches([a, b])

#`tensorbuilder.builders.BuilderTree`s are usually constructed using `tensorbuilder.builders.Builder.branch` of the `tensorbuilder.builders.Builder` class, but you can use this for special cases



##############################
##### BUILDER
##############################

##############################
##### connect_weights
##############################

# The following builds `tf.matmul(x, w)`
import tensorflow as tf
import tensorbuilder as tb

x = tf.placeholder(tf.float32, shape=[None, 5])

z = x.builder().connect_weights(3, weights_name="weights") 



##############################
##### connect_bias
##############################

# The following builds `tf.matmul(x, w) + b`
import tensorflow as tf
import tensorbuilder as tb

x = tf.placeholder(tf.float32, shape=[None, 5])

z = (
	x.builder()
	.connect_weights(3, weights_name="weights")
	.connect_bias(bias_name="bias")
)

# Note, the previous is equivalent to using `tensorbuilder.builders.Builder.connect_layer` like this
z = (
	x.builder()
	.connect_layer(3, weights_name="weights", bias_name="bias")
)




##############################
##### connect_layer
##############################

# The following builds the computation `tf.nn.sigmoid(tf.matmul(x, w) + b)`
import tensorflow as tf
import tensorbuilder as tb

x = tf.placeholder(tf.float32, shape=[None, 5])

h = (
	x.builder()
	.connect_layer(3, fn=tf.nn.sigmoid, weights_name="weights", bias_name="bias")
)

# The previous is equivalent to using 
h = (
	x.builder()
	.connect_weights(3, weights_name="weights")
	.connect_bias(bias_name="bias")
	.map(tf.nn.sigmoid)
)

# You can chain various `connect_layer`s to get deeper neural networks

import tensorflow as tf
import tensorbuilder as tb

x = tf.placeholder(tf.float32, shape=[None, 40])

h = (
	x.builder()
	.connect_layer(100, fn=tf.nn.tanh)
	.connect_layer(30, fn=tf.nn.softmax)
)




##############################
##### map
##############################

#The following constructs a neural network with the architecture `[40 input, 100 tanh, 30 softmax]` and and applies `dropout` to the tanh layer

import tensorflow as tf
import tensorbuilder as tb

x = tf.placeholder(tf.float32, shape=[None, 40])
keep_prob = tf.placeholder(tf.float32)

h = (
	x.builder()
	.connect_layer(100, fn=tf.nn.tanh)
	.map(tf.nn.dropout, keep_prob)
	.connect_layer(30, fn=tf.nn.softmax)
)




##############################
##### then
##############################

# The following *manually* constructs the computation `tf.nn.sigmoid(tf.matmul(x, w) + b)` while updating the `tensorbuilder.tensorbuiler.Builder.variables` dictionary.

import tensorflow as tf
import tensorbuilder as tb

x = tf.placeholder(tf.float32, shape=[None, 40])
keep_prob = tf.placeholder(tf.float32)

def sigmoid_layer(builder, size):
	m = int(builder.tensor.get_shape()[1])
	n = size

	w = tf.Variable(tf.random_uniform([m, n], -1.0, 1.0))
	b = tf.Variable(tf.random_uniform([n], -1.0, 1.0))

	builder.variables[w.name] = w
	builder.variables[b.name] = b

	builder.tensor = tf.nn.sigmoid(tf.matmul(builder.tensor, w) + b)

	return builder

h = (
	x.builder()
	.then(lambda builder: sigmoid_layer(builder, 3))
)

# Note that the previous if equivalent to

h = (
	x.builder()
	.connect_layer(3, fn=tf.nn.sigmoid)
)




##############################
##### branch
##############################

# The following will create a sigmoid layer but will branch the computation at the logit (z) so you get both the output tensor `h` and `trainer` tensor. Observe that first the logit `z` is calculated by creating a linear layer with `connect_layer(1)` and then its branched out

import tensorflow as tf
import tensorbuilder as tb

x = tf.placeholder(tf.float32, shape=[None, 5])
y = tf.placeholder(tf.float32, shape=[None, 1])

[h, trainer] = (
    x.builder()
    .connect_layer(1)
    .branch(lambda z:
    [
        z.map(tf.nn.sigmoid)
    ,
        z.map(tf.nn.sigmoid_cross_entropy_with_logits, y)
        .map(tf.train.AdamOptimizer(0.01).minimize)
    ])
    .tensors()
)

# Note that you have to use the `tensorbuilder.builders.BuilderTree.tensors` method from the `tensorbuilder.builders.BuilderTree` class to get the tensors back.

# Remember that you can also contain `tensorbuilder.builders.BuilderTree` elements when you branch out, this means that you can keep branching inside branch. Don't worry that the tree keep getting deeper, `tensorbuilder.builders.BuilderTree` has methods that help you flatten or reduce the tree. 
#The following example will show you how create a (overly) complex tree and then connect all the leaf nodes to a single `sigmoid` layer

import tensorflow as tf
import tensorbuilder as tb

x = tf.placeholder(tf.float32, shape=[None, 5])
keep_prob = tf.placeholder(tf.float32)

h = (
    x.builder()
    .connect_layer(10)
    .branch(lambda base:
    [
        base
        .connect_layer(3, fn=tf.nn.relu)
    ,
        base
        .connect_layer(9, fn=tf.nn.tanh)
        .branch(lambda base2: 
        [
        	base2
        	.connect_layer(6, fn=tf.nn.sigmoid)
        ,
        	base2
        	.map(tf.nn.dropout, keep_prob)
        	.connect_layer(8, tf.nn.softmax)
        ])
    ])
    .connect_layer(6, fn=tf.nn.sigmoid)
)

##############################
##### BUILDER TREE
##############################

##############################
##### builder
##############################

import tensorflow as tf
import tensorbuilder as tb

x = tf.placeholder(tf.float32, shape=[None, 5])
y = tf.placeholder(tf.float32, shape=[None, 1])

[h_builder, trainer_builder] = (
    x.builder()
    .connect_layer(1)
    .branch(lambda z:
    [
        z.map(tf.nn.sigmoid)
    ,
        z.map(tf.nn.sigmoid_cross_entropy_with_logits, y)
        .map(tf.train.AdamOptimizer(0.01).minimize)
    ])
    .builders()
)



##############################
##### tensors
##############################

import tensorflow as tf
import tensorbuilder as tb

x = tf.placeholder(tf.float32, shape=[None, 5])
y = tf.placeholder(tf.float32, shape=[None, 1])

[h_tensor, trainer_tensor] = (
    x.builder()
    .connect_layer(1)
    .branch(lambda z:
    [
        z.map(tf.nn.sigmoid)
    ,
        z.map(tf.nn.sigmoid_cross_entropy_with_logits, y)
        .map(tf.train.AdamOptimizer(0.01).minimize)
    ])
    .tensors()
)

##############################
##### connect_layer
##############################

# The following example shows you how to connect two tensors (rather builders) of different shapes to a single `softmax` layer of shape [None, 3]

import tensorflow as tf
import tensorbuilder as tb

a = tf.placeholder(tf.float32, shape=[None, 8]).builder()
b = tf.placeholder(tf.float32, shape=[None, 5]).builder()

h = (
	tb.branches([a, b])
	.connect_layer(3, fn=tf.nn.softmax)
)

# The next example show you how you can use this to pass the input layer directly through one branch, and "analyze" it with a `tanh layer` filter through the other, both of these are connect to a single `softmax` output layer

import tensorflow as tf
import tensorbuilder as tb

x = tf.placeholder(tf.float32, shape=[None, 5])

h = (
	x.builder()
	.branch(lambda x: 
	[
		x
	,
		x.connect_layer(10, fn=tf.nn.tanh)
	])
	.connect_layer(3, fn=tf.nn.softmax)
)
