"""
Minimal wordacter-level Vanilla RNN model. Written self.by Andrej Karpathy (@karpathy)
BSD License
"""
import numpy as np
import pickle
import os


class RNN():
  def __init__(self):
    # self.data I/O
    self.path = os.path.dirname(os.path.abspath(__file__))
    self.param_file = os.path.join(self.path, 'params.pkl')
    self.data_file = os.path.join(self.path, 'data.txt')
    with open(self.data_file, 'r') as df:
      self.data = df.read().split() # should be simple plain text file
    self.words = sorted(set(self.data))
    self.data_size, self.vocab_size = len(self.data), len(self.words)
    print('Started with: data has {ds} words, {vs} unique.\n----'.format(ds=self.data_size, vs=self.vocab_size))
    self.word_to_ix = { wd:i for i,wd in enumerate(self.words) }
    self.ix_to_word = { i:wd for i,wd in enumerate(self.words) }
    # hyperparameters
    self.hidden_size = 100 # size of hidden layer of neurons
    self.seq_length = 10 # number of steps to unroll the RNN for
    self.learning_rate = 1e-1
    # model parameters
    self.Wxh = np.random.randn(self.hidden_size, self.vocab_size)*0.01 # input to hidden
    self.Whh = np.random.randn(self.hidden_size, self.hidden_size)*0.01 # hidden to hidden
    self.Why = np.random.randn(self.vocab_size, self.hidden_size)*0.01 # hidden to output
    self.bh = np.zeros((self.hidden_size, 1)) # hidden bias
    self.by = np.zeros((self.vocab_size, 1)) # output bias

    if os.path.isfile(self.param_file):
      with open(self.param_file, 'rb') as f:
        self.Wxh, self.Whh, self.Why, self.bh, self.by = pickle.load(f)
        print("param loaded\n----")


  def lossFun(self, inputs, targets, hprev):
    xs, hs, ys, ps = {}, {}, {}, {}
    hs[-1] = np.copy(hprev)
    loss = 0
    # forward pass
    for t in range(len(inputs)):
      xs[t] = np.zeros((self.vocab_size,1)) # encode in 1-of-k representation
      xs[t][inputs[t]] = 1
      hs[t] = np.tanh(np.dot(self.Wxh, xs[t]) + np.dot(self.Whh, hs[t-1]) + self.bh) # hidden state
      ys[t] = np.dot(self.Why, hs[t]) + self.by # unnormalized log probabilities for next self.words
      ps[t] = np.exp(ys[t]) / np.sum(np.exp(ys[t])) # probabilities for next self.words
      loss += -np.log(ps[t][targets[t],0]) # softmax (cross-entropy loss)
    # backward pass: compute gradients going backwards
    dWxh, dWhh, dWhy = np.zeros_like(self.Wxh), np.zeros_like(self.Whh), np.zeros_like(self.Why)
    dbh, dby = np.zeros_like(self.bh), np.zeros_like(self.by)
    dhnext = np.zeros_like(hs[0])
    for t in reversed(range(len(inputs))):
      dy = np.copy(ps[t])
      dy[targets[t]] -= 1 # backprop into y. see http://cs231n.github.io/neural-networks-case-study/#grad if confused here
      dWhy += np.dot(dy, hs[t].T)
      dby += dy
      dh = np.dot(self.Why.T, dy) + dhnext # backprop into h
      dhraw = (1 - hs[t] * hs[t]) * dh # backprop through tanh nonlinearity
      dbh += dhraw
      dWxh += np.dot(dhraw, xs[t].T)
      dWhh += np.dot(dhraw, hs[t-1].T)
      dhnext = np.dot(self.Whh.T, dhraw)
    for dparam in [dWxh, dWhh, dWhy, dbh, dby]:
      np.clip(dparam, -5, 5, out=dparam) # clip to mitigate exploding gradients
    return loss, dWxh, dWhh, dWhy, dbh, dby, hs[len(inputs)-1]


  def sample(self, h, seed_ix, n):
    x = np.zeros((self.vocab_size, 1))
    x[seed_ix] = 1
    words = []
    for t in range(n):
      h = np.tanh(np.dot(self.Wxh, x) + np.dot(self.Whh, h) + self.bh)
      y = np.dot(self.Why, h) + self.by
      p = np.exp(y) / np.sum(np.exp(y))
      ix = np.random.choice(range(self.vocab_size), p=p.ravel())
      x = np.zeros((self.vocab_size, 1))
      x[ix] = 1
      words.append(self.ix_to_word[ix])
    return set(words)


  def test(self, input_tags, n):
    inputs = list(map(lambda x: self.word_to_ix[x], input_tags))
    x = np.zeros((self.vocab_size, 1))
    x[inputs[0]] = 1
    h = np.zeros((self.hidden_size,1))
    for i in range(len(inputs)):
      h = np.tanh(np.dot(self.Wxh, x) + np.dot(self.Whh, h) + self.bh)
      y = np.dot(self.Why, h) + self.by
      p = np.exp(y) / np.sum(np.exp(y))
      ix = np.random.choice(range(self.vocab_size), p=p.ravel())
      x = np.zeros((self.vocab_size, 1))
      x[inputs[i]] = 1
    return self.sample(h, ix, n)


  def train(self):
    n, p = 0, 0
    mWxh, mWhh, mWhy = np.zeros_like(self.Wxh), np.zeros_like(self.Whh), np.zeros_like(self.Why)
    mbh, mby = np.zeros_like(self.bh), np.zeros_like(self.by) # memory variables for Adagrad
    #smooth_loss = -np.log(1.0/self.vocab_size)*self.seq_length # loss at iteration 0
    while True:
      # prepare inputs (we're sweeping from left to right in steps self.seq_length long)
      if p+self.seq_length+1 >= len(self.data) or n == 0: 
        hprev = np.zeros((self.hidden_size,1)) # reset RNN memory
        p = 0 # go from start of self.data
      inputs = [self.word_to_ix[wd] for wd in self.data[p:p+self.seq_length]]
      targets = [self.word_to_ix[wd] for wd in self.data[p+1:p+self.seq_length+1]]

      # forward self.seq_length self.words through the net and fetch gradient
      loss, dWxh, dWhh, dWhy, dbh, dby, hprev = self.lossFun(inputs, targets, hprev)
      #smooth_loss = smooth_loss * 0.999 + loss * 0.001
      if n % 100 == 0: print ('iter {iter}, loss: {loss}'.format(iter=n, loss=loss)) # print progress
      
      # perform parameter update with Adagrad
      # adagrad update

      mWxh += dWxh * dWxh
      self.Wxh += -self.learning_rate * dWxh / np.sqrt(mWxh + 1e-8)
      mWhh += dWhh * dWhh
      self.Whh += -self.learning_rate * dWhh / np.sqrt(mWhh + 1e-8)
      mWhy += dWhy * dWhy
      self.Why += -self.learning_rate * dWhy / np.sqrt(mWhy + 1e-8)
      mbh += dbh * dbh
      self.bh += -self.learning_rate * dbh / np.sqrt(mbh + 1e-8)
      mby += dby * dby
      self.by += -self.learning_rate * dby / np.sqrt(mby + 1e-8)

      p += self.seq_length # move self.data pointer
      n += 1 # iteration counter

      if n == 1000:
        with open(self.param_file,'wb') as f:
          pickle.dump([self.Wxh, self.Whh, self.Why, self.bh, self.by], f)
        break


if __name__ == "__main__":
    rnn = RNN()
    rnn.train()
    print(rnn.test(["계산기", "dimmer.py"], 3))