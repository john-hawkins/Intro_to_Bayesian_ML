
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import math
import random

mu = 0
variance = 1
sigma = math.sqrt(variance)

x = np.linspace(mu - 4*sigma, mu + 4*sigma, 200)
y = stats.norm.pdf(x, mu, sigma)

# CHOOSE TWO SETS OF RANDOM SAMPLES
indecies = [x for x in range(0,200)]
sampled = random.sample(indecies,k=10)
sample1_x = x[sampled]
sample1_y = y[sampled]

s_x = np.random.normal(mu, sigma, 10)
s_y = stats.norm.pdf(s_x, mu, sigma)

plt.plot(x, stats.norm.pdf(x, mu, sigma), 'r-', label='Error Distribution')
plt.scatter(sample1_x, sample1_y, c='b', marker='+', label="Sample 1" )
plt.scatter(s_x, s_y, c='g', marker='o', label="Sample 2")
for i in range(0,10):
    plt.plot( (sample1_x[i],sample1_x[i]), (0, sample1_y[i]), 'b')

for i in range(0,10):
    plt.plot( (s_x[i], s_x[i]), (0, s_y[i]), 'g')

plt.xlabel("Error")
plt.ylabel("Density")
plt.title('Error Distribution')

plt.savefig("Error_Distribution.png")

