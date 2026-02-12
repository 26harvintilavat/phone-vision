"""
PhoneVision API-Based Scraper
Uses official free APIs - MOST RELIABLE METHOD
Get free API keys from:
- Pexels: https://www.pexels.com/api/
- Unsplash: https://unsplash.com/developers
"""

import os
import time
import requests
from pathlib import Path
import json
import hashlib
from datetime import datetime
from PIL import Image
import io
import random


class APIBasedScraper:
    def __init__(self, output_dir: str = "phone_dataset_api"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create directories
        self.raw_dir = self.output_dir / "raw"
        self.train_dir = self.output_dir / "train"
        self.val_dir = self.output_dir / "val"
        self.test_dir = self.output_dir / "test"
        
        for dir_path in [self.raw_dir, self.train_dir, self.val_dir, self.test_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # API Keys (you need to add your own)
        self.pexels_api_key = os.getenv('PEXELS_API_KEY', 'nBkyEFE0H5QOR9pEhfB1LqvYAsRXt0rbjefQgoCjpPtEvyE2eRlakbgp')
        self.unsplash_access_key = os.getenv('UNSPLASH_API_KEY', 'UrMGyiK9UpCAId0jY5tGjyMn7p-oV1ei1U0jyk3K0ks')
        
        self.session = requests.Session()
        self.downloaded_hashes = set()
        self.stats = {
            'total_attempted': 0,
            'successful': 0,
            'failed': 0,
            'duplicates': 0
        }
        
        print("🔑 API Status:")
        print(f"  Pexels: {'✅ Configured' if self.pexels_api_key else '❌ Not configured'}")
        print(f"  Unsplash: {'✅ Configured' if self.unsplash_access_key else '❌ Not configured'}")
        
        if not self.pexels_api_key and not self.unsplash_access_key:
            print("\n⚠️  NO API KEYS FOUND!")
            print("📝 To use this scraper:")
            print("1. Get free API key from https://www.pexels.com/api/")
            print("2. Get free API key from https://unsplash.com/developers")
            print("3. Set environment variables:")
            print("   export PEXELS_API_KEY='your_key_here'")
            print("   export UNSPLASH_ACCESS_KEY='your_key_here'")
            print("\nOr edit this file and add keys directly:\n")
    
    def get_image_hash(self, image_data: bytes) -> str:
        """Generate hash"""
        return hashlib.md5(image_data).hexdigest()
    
    def download_image(self, url: str, save_path: Path) -> bool:
        """Download and save image"""
        try:
            response = self.session.get(url, timeout=15, stream=True)
            response.raise_for_status()
            
            image_data = response.content
            size_kb = len(image_data) / 1024
            
            if size_kb < 10 or size_kb > 15360:
                return False
            
            img_hash = self.get_image_hash(image_data)
            if img_hash in self.downloaded_hashes:
                self.stats['duplicates'] += 1
                return False
            
            # Validate and save
            img = Image.open(io.BytesIO(image_data))
            if img.format not in ['JPEG', 'PNG', 'WEBP']:
                return False
            
            width, height = img.size
            if width < 100 or height < 100:
                return False
            
            if img.mode != 'RGB':
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    if img.mode in ('RGBA', 'LA'):
                        background.paste(img, mask=img.split()[-1])
                        img = background
                else:
                    img = img.convert('RGB')
            
            img.save(save_path, 'JPEG', quality=95)
            self.downloaded_hashes.add(img_hash)
            self.stats['successful'] += 1
            return True
            
        except Exception as e:
            self.stats['failed'] += 1
            return False
    
    def search_pexels(self, query: str, per_page: int = 80) -> list:
        """Search Pexels API"""
        if not self.pexels_api_key:
            return []
        
        print(f"  🔍 Searching Pexels...")
        urls = []
        
        try:
            headers = {'Authorization': self.pexels_api_key}
            
            # Search photos
            search_url = f"https://api.pexels.com/v1/search?query={query}&per_page={per_page}"
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                photos = data.get('photos', [])
                
                for photo in photos:
                    # Get large or original size
                    img_url = photo.get('src', {}).get('large2x') or photo.get('src', {}).get('large')
                    if img_url:
                        urls.append(img_url)
                
                print(f"    ✓ Found {len(urls)} images from Pexels")
            else:
                print(f"    ⚠️  Pexels API error: {response.status_code}")
        
        except Exception as e:
            print(f"    ⚠️  Pexels error: {str(e)[:60]}")
        
        return urls
    
    def search_unsplash(self, query: str, per_page: int = 30) -> list:
        """Search Unsplash API"""
        if not self.unsplash_access_key:
            return []
        
        print(f"  🔍 Searching Unsplash...")
        urls = []
        
        try:
            headers = {'Authorization': f'Client-ID {self.unsplash_access_key}'}
            
            # Search photos
            search_url = f"https://api.unsplash.com/search/photos?query={query}&per_page={per_page}"
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                for photo in results:
                    # Get regular or full size
                    img_url = photo.get('urls', {}).get('regular') or photo.get('urls', {}).get('full')
                    if img_url:
                        urls.append(img_url)
                
                print(f"    ✓ Found {len(urls)} images from Unsplash")
            else:
                print(f"    ⚠️  Unsplash API error: {response.status_code}")
        
        except Exception as e:
            print(f"    ⚠️  Unsplash error: {str(e)[:60]}")
        
        return urls
    
    def scrape_phone_model(self, brand: str, model: str, target_images: int = 100):
        """Scrape images for a phone model"""
        print(f"\n{'='*70}")
        print(f"📱 {brand} {model}")
        print(f"{'='*70}")
        
        model_name = f"{brand}_{model.replace(' ', '_').replace('/', '_')}"
        model_dir = self.raw_dir / model_name
        model_dir.mkdir(exist_ok=True)
        
        # Search queries
        queries = [
            f"{brand} {model}",
            f"{brand} {model} phone",
            f"{brand} {model} smartphone",
        ]
        
        all_urls = []
        
        print("🔍 Collecting image URLs from APIs...")
        for query in queries:
            # Pexels
            pexels_urls = self.search_pexels(query, per_page=30)
            all_urls.extend(pexels_urls)
            time.sleep(1)
            
            # Unsplash
            unsplash_urls = self.search_unsplash(query, per_page=30)
            all_urls.extend(unsplash_urls)
            time.sleep(1)
        
        all_urls = list(set(all_urls))
        print(f"\n📊 Total unique URLs: {len(all_urls)}")
        
        if len(all_urls) == 0:
            print("⚠️  No images found. Check API keys!")
            return 0
        
        # Download
        downloaded = 0
        print(f"\n⬇️  Downloading images (target: {target_images})...")
        
        for i, url in enumerate(all_urls):
            if downloaded >= target_images:
                break
            
            self.stats['total_attempted'] += 1
            
            filename = f"{model_name}_{downloaded+1:04d}.jpg"
            save_path = model_dir / filename
            
            if save_path.exists():
                continue
            
            print(f"  [{downloaded+1}/{target_images}] Downloading...", end='\r')
            if self.download_image(url, save_path):
                downloaded += 1
            
            time.sleep(0.3)
        
        print(f"\n✅ Downloaded {downloaded} images")
        return downloaded
    
    def split_dataset(self, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15):
        """Split dataset"""
        print("\n📂 Splitting dataset...")
        
        model_dirs = [d for d in self.raw_dir.iterdir() if d.is_dir()]
        
        for model_dir in model_dirs:
            model_name = model_dir.name
            images = list(model_dir.glob("*.jpg"))
            
            if not images:
                continue
            
            random.shuffle(images)
            
            n_images = len(images)
            n_train = int(n_images * train_ratio)
            n_val = int(n_images * val_ratio)
            
            for split_dir in [self.train_dir, self.val_dir, self.test_dir]:
                (split_dir / model_name).mkdir(exist_ok=True)
            
            import shutil
            for i, img_path in enumerate(images):
                if i < n_train:
                    dest_dir = self.train_dir / model_name
                elif i < n_train + n_val:
                    dest_dir = self.val_dir / model_name
                else:
                    dest_dir = self.test_dir / model_name
                
                shutil.copy2(img_path, dest_dir / img_path.name)
            
            print(f"  ✓ {model_name}: {n_train} train, {n_val} val, {n_images - n_train - n_val} test")
    
    def print_summary(self, duration: float):
        """Print summary"""
        print(f"\n{'='*70}")
        print("🎉 SCRAPING COMPLETE!")
        print(f"{'='*70}")
        print(f"⏱️  Time: {duration/60:.1f} minutes")
        print(f"🎯 Attempted: {self.stats['total_attempted']}")
        print(f"✅ Successful: {self.stats['successful']}")
        print(f"❌ Failed: {self.stats['failed']}")
        print(f"🔄 Duplicates: {self.stats['duplicates']}")
        print(f"💾 Output: {self.output_dir.absolute()}")
        print(f"{'='*70}\n")


def main():
    """Main execution"""
    
    phone_models = [
        {'brand': 'Apple', 'model': 'iPhone 15 Pro'},
        {'brand': 'Apple', 'model': 'iPhone 14'},
        {'brand': 'Samsung', 'model': 'Galaxy S24 Ultra'},
        {'brand': 'Samsung', 'model': 'Galaxy S23'},
        {'brand': 'Google', 'model': 'Pixel 8 Pro'},
        {'brand': 'Google', 'model': 'Pixel 7'},
        {'brand': 'OnePlus', 'model': 'OnePlus 12'},
        {'brand': 'Xiaomi', 'model': 'Xiaomi 14 Pro'},
        {'brand': 'Samsung', 'model': 'Galaxy A54'},
        {'brand': 'Apple', 'model': 'iPhone 13'},
    ]
    
    print("🚀 PhoneVision API-Based Scraper (Most Reliable)")
    print(f"📱 Models: {len(phone_models)}\n")
    
    start_time = datetime.now()
    
    scraper = APIBasedScraper(output_dir="phone_dataset_api")
    
    total = 0
    for idx, phone in enumerate(phone_models, 1):
        print(f"\n[{idx}/{len(phone_models)}]")
        downloaded = scraper.scrape_phone_model(
            phone['brand'], 
            phone['model'], 
            target_images=100
        )
        total += downloaded
        time.sleep(2)
    
    if total > 0:
        scraper.split_dataset()
    
    duration = (datetime.now() - start_time).total_seconds()
    scraper.print_summary(duration)
    
    if total == 0:
        print("\n❌ NO IMAGES DOWNLOADED!")
        print("\n📝 SOLUTIONS:")
        print("1. Get free Pexels API key: https://www.pexels.com/api/")
        print("2. Get free Unsplash API key: https://unsplash.com/developers")
        print("3. Set environment variables with your keys")
        print("\nAlternatively, use the Selenium scraper for automated browsing.")


if __name__ == "__main__":
    main()