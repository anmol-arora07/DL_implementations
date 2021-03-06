import os
import pandas as pd
import torch
import matplotlib.pyplot as plt
from torch import nn, optim
from torchvision import datasets, transforms
import torch.nn.functional as F
from torch.utils.data import random_split
from torch.utils.data import DataLoader

device=torch.device("cuda" if torch.cuda.is_available() else "cpu")

class AlexNet(nn.Module):
    def __init__(self) -> None:
        super(AlexNet,self).__init__()
        self.conv1=nn.Conv2d(in_channels=3,out_channels=96,kernel_size=11,stride=4,padding=0)
        self.maxpool=nn.MaxPool2d(kernel_size=3, stride=2)
        self.conv2=nn.Conv2d(in_channels=96, out_channels=256, kernel_size=5, stride=1, padding=2)
        self.conv3=nn.Conv2d(in_channels=256,out_channels=384, kernel_size=3, stride=1, padding=1)
        self.conv4=nn.Conv2d(in_channels=384, out_channels=384, kernel_size=3, stride=1, padding=1)
        self.conv5=nn.Conv2d(in_channels=384,out_channels=256, kernel_size=3, stride=1, padding=1)
        self.fc1=nn.Linear(in_features=9216,out_features=4096)
        self.fc2=nn.Linear(in_features=4096, out_features=4096)
        self.fc3=nn.Linear(in_features=4096, out_features=10)

    def forward(self,x):
        x=F.relu(self.conv1(x))
        x=self.maxpool(x)
        x=F.relu(self.conv2(x))
        x=self.maxpool(x)
        x=F.relu(self.conv3(x))
        x=F.relu(self.conv4(x))
        x=F.relu(self.conv5(x))
        x=self.maxpool(x)
        x=x.reshape(x.shape[0],-1)
        x=F.relu(self.fc1(x))
        x=F.relu(self.fc2(x))
        x=self.fc3(x)
        return x

##CIFAR DATASET ##

#creating a dinstinct transform class for the train, validation and test dataset
transform_train = transforms.Compose([transforms.Resize((227,227)), transforms.RandomHorizontalFlip(p=0.7), transforms.ToTensor(), transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])
transform_test = transforms.Compose([transforms.Resize((227,227)), transforms.ToTensor(), transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])


torch.manual_seed(43)
train_ds=datasets.CIFAR10("data/",train=True,download=True, transform=transform_train)
val_size = 10000 #there are 10,000 test images and since there are no transforms performed on the test, we keep the validation as 10,000
train_size = len(train_ds) - val_size
train_ds, val_ds = random_split(train_ds, [train_size, val_size]) #Extracting the 10,000 validation images from the train set
test_ds = datasets.CIFAR10("data/", train=False, download=True, transform=transform_test) #10,000 images

#passing the train, val and test datasets to the dataloader
train_dl = DataLoader(train_ds, batch_size=64, shuffle=True)
val_dl = DataLoader(val_ds, batch_size=64, shuffle=False)
test_dl = DataLoader(test_ds, batch_size=64, shuffle=False)


#Training the Model

model=AlexNet()
model=model.to(device=device)

lr=1e-4
load_model=True
criterion=nn.CrossEntropyLoss()
optimizer=optim.Adam(model.parameters(),lr=lr)

for epoch in range(50):
    loss_ep=0

    for batch_idx, (data,targets) in enumerate(train_dl):
        data=data.to(device=device)
        targets=targets.to(device=device)

        #Forward Pass
        optimizer.zero_grad()
        scores=model(data)
        loss=criterion(scores,targets)
        loss.backward()
        optimizer.step()
        loss_ep+=loss.item()

    print( f"loss in epoch {epoch} :::: {loss_ep/len(train_dl)}")


    with torch.no_grad():
        num_correct=0
        num_samples=0

        for batch_idx, (data,targets) in enumerate(val_dl):
            data=data.to(device=device)
            targets=targets.to(device=device)

            #Forward Pass
            scores=model(data)
            _, predictions= scores.max(1)
            num_correct+= (predictions==targets).sum()
            num_samples+=predictions.size(0)

        print(f"Got {num_correct}/{num_samples} with accuracy {float(num_correct)/float(num_samples) *100: .2f}")
