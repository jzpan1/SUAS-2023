import os
import numpy as np
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision import models
from torch.utils.data import Dataset, DataLoader
import cv2


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Define the path to the data
data_dir = ".data/full_drop_zone"
image_dir = os.path.join(data_dir, "images")
metadata_dir = os.path.join(data_dir, "metadata")
results_dir = os.path.join(data_dir, "results")

# Define hyperparameters
batch_size = 8
lr = 0.001
num_epochs = 1

# Define custom dataset class
class DropZoneDataset(Dataset):
    def __init__(self, image_dir, metadata_dir, transform=None):
        self.image_dir = image_dir
        self.metadata_dir = metadata_dir
        self.image_files = os.listdir(image_dir)
        self.transform = transform

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        image_name = self.image_files[idx]
        image_path = os.path.join(self.image_dir, image_name)
        metadata_path = os.path.join(self.metadata_dir, image_name.replace(".png", ".txt"))

        # resize image 
        image = cv2.imread(image_path)
        image = cv2.resize(image, (224, 224)) 

        # metadata
        with open(metadata_path, 'r') as f:
            data = f.readlines()
        drop_locations = []
        for line in data:
            coords = line.split("(")[1].split(")")[0].split(",")
            x, y = int(coords[0]), int(coords[1])
            drop_locations.append((x, y))

        # Padding to resolve error
        while len(drop_locations) < 5:
            drop_locations.append((0, 0))  

        sample = {'image': image, 'drop_locations': drop_locations}

        if self.transform:
            sample = self.transform(sample)

        return sample


class ToTensor(object):
    def __call__(self, sample):
        image, drop_locations = sample['image'], sample['drop_locations']
        image = image.transpose((2, 0, 1))
        return {'image': torch.tensor(image, dtype=torch.float).to(device),
                'drop_locations': torch.tensor(drop_locations, dtype=torch.float).to(device)}


class DropZoneModel(nn.Module):
    def __init__(self):
        super(DropZoneModel, self).__init__()
        self.resnet = models.resnet18(pretrained=True)
        self.fc = nn.Linear(1000, 5 * 2)  # Output layer gives x, y coords

    def forward(self, x):
        x = self.resnet(x)
        x = self.fc(x)
        x = x.view(-1, 5, 2)
        return x.to(device)



def train(model, train_loader, criterion, optimizer, num_epochs):
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        for i, data in enumerate(train_loader, 0):
            inputs, labels = data['image'], data['drop_locations']
            optimizer.zero_grad()

            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        print(f"Epoch {epoch+1}, Loss: {running_loss / len(train_loader)}")



def find_drop_locations(model, test_loader):
    model.eval()
    predicted_locations_list = []
    with torch.no_grad():
        for i, data in enumerate(test_loader, 0):
            inputs, _ = data['image'], data['drop_locations']
            outputs = model(inputs)
            predicted_locations = outputs.cpu().numpy()
            predicted_locations_list.append(predicted_locations)
    return predicted_locations_list



def highlight_drop_locations(test_dataset, predicted_locations_list):
    for i in range(len(test_dataset)):
        image, _ = test_dataset[i]['image'], test_dataset[i]['drop_locations']
        image = image.cpu()
        predicted_locations = predicted_locations_list[i]
        image = np.transpose(image, (1, 2, 0))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        for loc in predicted_locations:
            cv2.rectangle(image, (int(loc[0])-5, int(loc[1])-5), (int(loc[0])+5, int(loc[1])+5), (255, 0, 0), 2)
        cv2.imwrite(os.path.join(results_dir, f"result_{i}.png"), image)




def main():
    dataset = DropZoneDataset(image_dir=image_dir, metadata_dir=metadata_dir, transform=ToTensor())
    train_size = int(0.8 * len(dataset))
    test_size = len(dataset) - train_size
    train_dataset, test_dataset = torch.utils.data.random_split(dataset, [train_size, test_size])
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    # Define the model, loss function, and optimizer
    model = DropZoneModel().to(device)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    # Train the model
    train(model, train_loader, criterion, optimizer, num_epochs)

    # Find drop locations
    predicted_locations_list = find_drop_locations(model, test_loader)

    # Highlight drop locations on images and save
    highlight_drop_locations(test_dataset, predicted_locations_list)
    print("Evaluation complete. Results saved in 'data/full_drop_zone/results'")

if __name__ == "__main__":
    main()