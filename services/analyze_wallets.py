import json
import os
import time
from typing import Dict, List, Any
from decimal import Decimal
from tqdm import tqdm
import argparse
from ton_services import get_balance


class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle Decimal objects."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def load_input_wallets(input_file: str) -> List[Dict]:
    """Load wallet addresses from input file."""
    if not os.path.exists(input_file):
        print(f"Input file {input_file} does not exist. Creating empty file.")
        os.makedirs(os.path.dirname(input_file) or '.', exist_ok=True)
        with open(input_file, 'w') as f:
            json.dump({"addresses": []}, f, indent=2)
        return []
        
    with open(input_file, 'r') as f:
        try:
            data = json.load(f)
            return data.get("addresses", [])
        except json.JSONDecodeError:
            print(f"Error reading {input_file}. File may be corrupted. Creating new empty file.")
            with open(input_file, 'w') as f:
                json.dump({"addresses": []}, f, indent=2)
            return []


def load_existing_analysis(output_file: str) -> Dict[str, Dict]:
    """Load existing analysis results if available."""
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            try:
                data = json.load(f)
                return data
            except json.JSONDecodeError:
                return {}
    return {}


def save_analysis(analysis: Dict, output_file: str) -> None:
    """Save analysis results to file using custom JSON encoder for Decimal values."""
    os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2, cls=DecimalEncoder)


def process_wallet_data(wallet_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process wallet data to ensure all values are JSON serializable."""
    processed_data = {}
    for key, value in wallet_data.items():
        if isinstance(value, dict):
            processed_data[key] = process_wallet_data(value)
        elif isinstance(value, Decimal):
            processed_data[key] = float(value)
        else:
            processed_data[key] = value
    return processed_data


def analyze_wallets(input_file: str = "ton_wallets.json", 
                   output_file: str = "wallet_analysis.json",
                   batch_size: int = 50) -> None:
    """
    Analyze TON wallets and their token balances.
    
    Args:
        input_file: Path to JSON file containing wallet addresses
        output_file: Path to save the analysis results
        batch_size: Number of wallets to process before saving progress
    """
    # Load input wallets
    wallets = load_input_wallets(input_file)
    print(f"Loaded {len(wallets)} wallets from {input_file}")
    
    # Load existing analysis
    analysis = load_existing_analysis(output_file)
    print(f"Loaded {len(analysis)} existing analysis results from {output_file}")
    
    # Create progress bar
    pbar = tqdm(total=len(wallets), desc="Analyzing wallets")
    pbar.update(len(analysis))
    
    try:
        for wallet in wallets:
            address = wallet["address"]
            
            # Skip if already analyzed
            if address in analysis:
                continue
            
            try:
                # Get wallet balance and token information
                balance_info = get_balance(address)
                if balance_info:
                    # Process the data to handle Decimal values
                    processed_balance_info = process_wallet_data(balance_info)
                    
                    analysis[address] = {
                        "name": wallet.get("name", ""),
                        "balances": processed_balance_info,
                        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    pbar.update(1)
                
                # Save progress after each batch
                if len(analysis) % batch_size == 0:
                    save_analysis(analysis, output_file)
                    print(f"\nSaved progress: {len(analysis)} wallets analyzed")
                    
            except Exception as e:
                print(f"\nError analyzing wallet {address}: {str(e)}")
                continue
                
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user")
    finally:
        pbar.close()
        save_analysis(analysis, output_file)
        
    print(f"\nAnalysis complete. Processed {len(analysis)} wallets")
    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze TON wallets and their token balances')
    parser.add_argument('-i', '--input', type=str, default="ton_wallets.json",
                      help='Input JSON file containing wallet addresses (default: ton_wallets.json)')
    parser.add_argument('-o', '--output', type=str, default="wallet_analysis.json",
                      help='Output JSON file for analysis results (default: wallet_analysis.json)')
    parser.add_argument('-b', '--batch-size', type=int, default=50,
                      help='Number of wallets to process before saving progress (default: 50)')
    
    args = parser.parse_args()
    
    analyze_wallets(
        input_file=args.input,
        output_file=args.output,
        batch_size=args.batch_size
    )
