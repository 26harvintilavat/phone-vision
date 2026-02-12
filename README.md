# Phone Vision Project

## Overview

This project builds a dataset and model for **mobile phone detection and classification**.

## Features

* Image scraping from Pexels/Unsplash
* Automatic dataset cleaning using YOLO
* Removes images that do not contain phones
* Organized dataset for training

## Project Structure

```
phone_vision/
│
├── data/ (ignored in GitHub)
├── src/
│   ├── download_images.py
│   └── clean_dataset.py
├── requirements.txt
├── README.md
```

## Setup

1. Clone repository

```
git clone <repo-link>
cd phone_vision
```

2. Install dependencies

```
pip install -r requirements.txt
```

## Clean Dataset

```
python src/clean_dataset.py
```

This removes images that do not contain mobile phones using a pretrained YOLO model.
