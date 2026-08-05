import torch
from torchvision import models, transforms

# VOC classes (21 classes including background)
VOC_CLASSES = [
    'background', 'aeroplane', 'bicycle', 'bird', 'boat', 'bottle', 'bus', 'car',
    'cat', 'chair', 'cow', 'diningtable', 'dog', 'horse', 'motorbike', 'person',
    'pottedplant', 'sheep', 'sofa', 'train', 'tvmonitor'
]

# For demo, map VOC classes to a subset for visualization
CLASS_NAME_MAP = {
    0: 'background',
    1: 'sky',        # aeroplane (simulate sky)
    2: 'road',       # bicycle (simulate road)
    3: 'tree',       # bird (simulate tree)
    6: 'car',        # car
    15: 'person',    # person
    7: 'car',        # bus (as car)
    14: 'car',       # motorbike (as car)
    11: 'building',  # diningtable (simulate building)
    17: 'tree',      # sheep (simulate tree)
    # ...other classes can be mapped as needed
}

# Preprocessing for DeepLabV3
preprocess = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((520, 520)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def load_segmentation_model():
    model = models.segmentation.deeplabv3_resnet101(pretrained=True).eval()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    return model, VOC_CLASSES

def segment_frame(model, frame):
    device = next(model.parameters()).device
    input_tensor = preprocess(frame).unsqueeze(0).to(device)
    with torch.no_grad():
        output = model(input_tensor)['out'][0]
        mask = output.argmax(0).cpu().numpy().astype('uint8')
    return mask
