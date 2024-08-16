import numpy as np
import nltk
from sklearn.model_selection import train_test_split
import torch
import torch.nn as nn
import torch.optim as optim
from nltk_utils import bag_of_words, tokenize, stem
from chatbotModel import NeuralNet
import json

nltk.download('punkt')


with open('intents.json', 'r') as f:
    intents = json.load(f)

# Prepare data
all_words = []
tags = []
xy = []

for intent in intents['intents']:
    for pattern in intent['patterns']:
        # tokenizinge each word in the sentence
        word_list = tokenize(pattern)
        all_words.extend(word_list)
        xy.append((word_list, intent['tag']))
    # adding tag to tags if it's not already there
    if intent['tag'] not in tags:
        tags.append(intent['tag'])

# stem and lower each word and remove duplicates
all_words = [stem(w) for w in all_words]
all_words = sorted(set(all_words))
tags = sorted(tags)

# Create training data
X_train = []
y_train = []

for (pattern_sentence, tag) in xy:
    bag = bag_of_words(pattern_sentence, all_words)
    X_train.append(bag)
    y_train.append(tags.index(tag))

X_train = np.array(X_train)
y_train = np.array(y_train)

# Split data into training and testing
X_train, X_test, y_train, y_test = train_test_split(X_train, y_train, test_size=0.2, random_state=42)

# Set up the neural network
input_size = len(X_train[0])
hidden_size = 8
output_size = len(tags)

model = NeuralNet(input_size, hidden_size, output_size)

# Loss and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Train the model
num_epochs = 1000

for epoch in range(num_epochs):
    # Forward pass
    outputs = model(torch.tensor(X_train, dtype=torch.float32))
    loss = criterion(outputs, torch.tensor(y_train, dtype=torch.long))

    # Backward and optimize
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if (epoch+1) % 100 == 0:
        print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')

# Save the model and other data
data = {
    "input_size": input_size,
    "hidden_size": hidden_size,
    "output_size": output_size,
    "all_words": all_words,
    "tags": tags,
    "model_state": model.state_dict()
}

FILE = "data.pth"
torch.save(data, FILE)

print(f"Model training complete and saved to {FILE}")
