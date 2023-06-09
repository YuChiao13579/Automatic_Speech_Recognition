import torch 
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

from torch.utils.data import Dataset
from torch.utils.data import DataLoader

from tqdm import tqdm

from model import model_conv, model_lstm
import numpy as np
import preprocess
import plot

# get dataset with desired type
class SpeechDataset(Dataset):
    def __init__(self, inputdata, label):
        self.inputdata = inputdata
        self.label = label

    def __len__(self):
        return len(self.inputdata)

    def __getitem__(self, idx):
        features = torch.FloatTensor(self.inputdata[idx])
        label = torch.LongTensor(self.label[idx])

        return features, label

# loss function: use cross entropy
def get_loss(label, output):
    loss = F.cross_entropy(output, label.view(-1))
    return loss
 
# accuracy: use argmax & calculate num of correct prediction
def get_acc(label, output):
    pred = torch.argmax(output, dim=1)
    label = label.view(-1)
    acc_sum = (label==pred).sum().item()

    return acc_sum

if __name__ == "__main__":
    print("------LSTM with torch model------")
    # preprocess.save_data()
    featureType = "mfcc"
    trainX, testX, trainY, testY = preprocess.getTrainTest(featureType)

    # use DataLoader to batch and shuffle the data
    train_dataset = SpeechDataset(trainX, trainY)
    train_data_loader = DataLoader(
        train_dataset, batch_size=200, num_workers=2, shuffle=True)

    test_dataset = SpeechDataset(testX, testY)
    test_data_loader = DataLoader(
        test_dataset, batch_size=200, num_workers=2, shuffle=False)

    # call models from model.py
    network = model_lstm(99, 12, 12)
    # network = model_conv(99, 12, 12)
    optimizer = optim.SGD(network.parameters(),
                          lr=0.1)
    
    train_accuracy = list()
    train_loss = list()
    test_accuracy = list()
    test_loss = list()

    for i in range(10):
        train_total_acc = 0
        train_total_loss = 0
        test_total_acc = 0
        test_total_loss = 0
        for feature, label in tqdm(train_data_loader):
            optimizer.zero_grad()

            network.train()
            output = network(feature)

            loss = get_loss(label, output)
            accp = get_acc(label, output)
            train_total_loss+=loss.item()
            train_total_acc+=accp
            
            loss.backward()
            optimizer.step()
            
        print("train_avg_acc(%): ", train_total_acc/11400 * 100)
        print("train_avg_loss: ", train_total_loss/(11400/200.0))
        train_accuracy.append(train_total_acc/11400 * 100)
        train_loss.append(train_total_loss/(11400/200.0))
        
        for feature, label in tqdm(test_data_loader):
            network.eval()
            output = network(feature)

            loss = get_loss(label, output)
            accp = get_acc(label, output)
            test_total_loss+=loss.item()
            test_total_acc+=accp
        print("test_avg_acc(%): ", test_total_acc/600 * 100)
        print("test_avg_loss: ", test_total_loss)
        test_accuracy.append(test_total_acc/600 * 100)
        test_loss.append(test_total_loss)
    
    plot.ploting(train_accuracy, train_loss, test_accuracy, test_loss)
