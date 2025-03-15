import requests
import json
import time
from tqdm import tqdm
from typing import List, Dict, Set
import os
import names
import concurrent.futures
from itertools import islice
import argparse

def generate_name() -> str:
    """Generate a random real name."""
    name_type = names.get_first_name()
    return name_type.lower()

def search_wallets(name: str) -> List[Dict]:
    """Search wallets using TON API."""
    url = f"https://tonapi.io/v2/accounts/search?name={name}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        # Filter out jettons and only keep actual accounts
        wallets = [
            addr for addr in data.get("addresses", [])
            if "· account" in addr.get("name", "").lower() and not addr.get("name", "").lower().endswith("· jetton")
        ]
        return wallets
    except requests.RequestException as e:
        print(f"Error searching for name '{name}': {e}")
        return []

def process_batch(names_batch: List[str]) -> List[Dict]:
    """Process a batch of names and return unique wallets."""
    wallets = []
    for name in names_batch:
        results = search_wallets(name)
        wallets.extend(results)
        time.sleep(0.2)  # Small delay between requests in the same batch
    return wallets

def load_existing_wallets(output_file: str) -> tuple[List[Dict], Set[str]]:
    """Load existing wallets from file if it exists."""
    try:
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                data = json.load(f)
                wallets = data.get("addresses", [])
                unique_addresses = {w["address"] for w in wallets}
                print(f"Loaded {len(wallets)} existing wallets from {output_file}")
                return wallets, unique_addresses
    except Exception as e:
        print(f"Error loading existing wallets: {e}")
    return [], set()

def find_ton_wallets(target_count: int = 1000, output_file: str = "ton_wallets.json", 
                     batch_size: int = 10, max_workers: int = 5) -> None:
    """
    Find TON wallets by searching names in parallel until reaching target count.
    
    Args:
        target_count: Number of unique wallets to find
        output_file: Path to save the JSON output
        batch_size: Number of names to process in each batch
        max_workers: Number of parallel workers
    """
    # Load existing wallets
    found_wallets, unique_wallets = load_existing_wallets(output_file)
    remaining_count = max(0, target_count - len(unique_wallets))
    
    if remaining_count == 0:
        print(f"Already have {len(unique_wallets)} wallets, target reached!")
        return
        
    attempts = 0
    max_attempts = remaining_count * 5  # Reduced since we're using real names

    # Create progress bar
    pbar = tqdm(total=target_count, initial=len(unique_wallets), desc="Finding wallets")
    
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            while len(unique_wallets) < target_count and attempts < max_attempts:
                # Generate batch of names
                names_batch = [generate_name() for _ in range(batch_size)]
                
                # Process batch in parallel
                future = executor.submit(process_batch, names_batch)
                wallets = future.result()
                
                # Process new wallets
                for wallet in wallets:
                    if wallet["address"] not in unique_wallets:
                        unique_wallets.add(wallet["address"])
                        found_wallets.append(wallet)
                        pbar.update(1)
                        
                        # Save progress when reaching milestones
                        if len(unique_wallets) % 50 == 0:
                            save_wallets(found_wallets, output_file)
                            print(f"\nFound {len(unique_wallets)} unique wallets so far...")
                        
                        if len(unique_wallets) >= target_count:
                            break
                
                attempts += 1
                
    except KeyboardInterrupt:
        print("\nSearch interrupted by user")
    finally:
        pbar.close()
        save_wallets(found_wallets, output_file)
        
    print(f"\nFound {len(unique_wallets)} unique wallets")
    print(f"Results saved to {output_file}")

def save_wallets(wallets: List[Dict], output_file: str) -> None:
    """Save wallets to JSON file."""
    os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump({"addresses": wallets}, f, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find TON wallets using parallel processing')
    parser.add_argument('-c', '--count', type=int, default=1000,
                      help='Number of wallets to find (default: 1000)')
    parser.add_argument('-w', '--workers', type=int, default=5,
                      help='Number of parallel workers (default: 5)')
    parser.add_argument('-b', '--batch-size', type=int, default=10,
                      help='Number of names to process in each batch (default: 10)')
    parser.add_argument('-o', '--output', type=str, default="ton_wallets.json",
                      help='Output JSON file path (default: ton_wallets.json)')
    parser.add_argument('--new', action='store_true',
                      help='Start fresh and ignore existing wallets in the output file')
    
    args = parser.parse_args()
    
    # If --new flag is used, remove existing file
    if args.new and os.path.exists(args.output):
        os.remove(args.output)
        print(f"Removed existing file: {args.output}")
    
    find_ton_wallets(
        target_count=args.count,
        max_workers=args.workers,
        batch_size=args.batch_size,
        output_file=args.output
    )
