"""
Fridge Manager - Functions to manage fridge contents stored in CSV format.
"""

import csv
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from pathlib import Path


class FridgeManager:
    """Manager class for fridge contents operations."""
    
    def __init__(self, csv_path: Optional[str] = None):
        """
        Initialize FridgeManager with path to CSV file.
        
        Args:
            csv_path: Path to the CSV file. If None, uses default path.
        """
        if csv_path is None:
            # Default to fridge_contents.csv in the same directory as this file
            current_dir = Path(__file__).parent
            self.csv_path = current_dir / "fridge_contents.csv"
        else:
            self.csv_path = Path(csv_path)
            
        self.fieldnames = ['item name', 'category', 'purchase date', 'best before date', 'items']
    
    def _read_csv(self) -> List[Dict[str, str]]:
        """Read the CSV file and return list of dictionaries."""
        if not self.csv_path.exists():
            return []
            
        with open(self.csv_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return list(reader)
    
    def _write_csv(self, data: List[Dict[str, str]]) -> None:
        """Write data to the CSV file."""
        # Ensure the directory exists
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=self.fieldnames)
            writer.writeheader()
            writer.writerows(data)
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string in YYYY-MM-DD format."""
        if not date_str or date_str.strip() == '':
            return None
        try:
            return datetime.strptime(date_str.strip(), '%Y-%m-%d')
        except ValueError:
            return None
    
    def list_all_items(self) -> List[Dict[str, str]]:
        """
        List all items in the fridge.
        
        Returns:
            List of dictionaries containing all fridge items.
        """
        return self._read_csv()
    
    def list_items_by_category(self, category: str) -> List[Dict[str, str]]:
        """
        List items from a specific category.
        
        Args:
            category: Category to filter by (case-insensitive).
            
        Returns:
            List of dictionaries containing items from the specified category.
        """
        all_items = self._read_csv()
        category_lower = category.lower()
        return [item for item in all_items 
                if item['category'].lower() == category_lower]
    
    def list_items_close_to_expiry(self, days_threshold: int) -> List[Dict[str, str]]:
        """
        List items close to their best before date.
        
        Args:
            days_threshold: Number of days to consider as "close to expiry".
                           Items expiring within this many days will be returned.
            
        Returns:
            List of dictionaries containing items close to expiry.
        """
        all_items = self._read_csv()
        current_date = datetime.now()
        threshold_date = current_date + timedelta(days=days_threshold)
        
        close_to_expiry = []
        for item in all_items:
            best_before = self._parse_date(item['best before date'])
            if best_before and best_before <= threshold_date:
                close_to_expiry.append(item)
        
        return close_to_expiry
    
    def update_item(self, item_name: str, updates: Dict[str, str], 
                   match_index: Optional[int] = None) -> bool:
        """
        Update an existing item based on name.
        
        Args:
            item_name: Name of the item to update (case-insensitive).
            updates: Dictionary of field names and new values to update.
            match_index: If multiple items have the same name, specify which one 
                        to update by index (0-based). If None, updates the first match.
            
        Returns:
            True if item was updated, False if item was not found.
        """
        all_items = self._read_csv()
        item_name_lower = item_name.lower()
        matches_found = 0
        updated = False
        
        for i, item in enumerate(all_items):
            if item['item name'].lower() == item_name_lower:
                if match_index is None or matches_found == match_index:
                    # Update the item
                    for field, value in updates.items():
                        if field in self.fieldnames:
                            item[field] = value
                    updated = True
                    break
                matches_found += 1
        
        if updated:
            self._write_csv(all_items)
        
        return updated
    
    def delete_item(self, item_name: str, match_index: Optional[int] = None) -> bool:
        """
        Delete an existing item by name.
        
        Args:
            item_name: Name of the item to delete (case-insensitive).
            match_index: If multiple items have the same name, specify which one 
                        to delete by index (0-based). If None, deletes the first match.
            
        Returns:
            True if item was deleted, False if item was not found.
        """
        all_items = self._read_csv()
        item_name_lower = item_name.lower()
        matches_found = 0
        
        for i, item in enumerate(all_items):
            if item['item name'].lower() == item_name_lower:
                if match_index is None or matches_found == match_index:
                    # Delete the item
                    all_items.pop(i)
                    self._write_csv(all_items)
                    return True
                matches_found += 1
        
        return False
    
    def add_item(self, item_name: str, category: str, purchase_date: str,
                 best_before_date: str = "", items: str = "1") -> bool:
        """
        Add a new item to the fridge.
        
        Args:
            item_name: Name of the item.
            category: Category of the item.
            purchase_date: Purchase date in YYYY-MM-DD format.
            best_before_date: Best before date in YYYY-MM-DD format (optional).
            items: Description/quantity of items (default: "1").
            
        Returns:
            True if item was added successfully.
        """
        all_items = self._read_csv()
        
        new_item = {
            'item name': item_name,
            'category': category,
            'purchase date': purchase_date,
            'best before date': best_before_date,
            'items': items
        }
        
        all_items.append(new_item)
        self._write_csv(all_items)
        return True
    
    def get_item_count_by_name(self, item_name: str) -> int:
        """
        Get the count of items with the same name.
        
        Args:
            item_name: Name of the item to count (case-insensitive).
            
        Returns:
            Number of items with the given name.
        """
        all_items = self._read_csv()
        item_name_lower = item_name.lower()
        return sum(1 for item in all_items 
                  if item['item name'].lower() == item_name_lower)


# Convenience functions for standalone usage
def create_fridge_manager(csv_path: Optional[str] = None) -> FridgeManager:
    """Create and return a FridgeManager instance."""
    return FridgeManager(csv_path)


# Standalone function interfaces
def list_all_items(csv_path: Optional[str] = None) -> List[Dict[str, str]]:
    """List all items in the fridge."""
    manager = FridgeManager(csv_path)
    return manager.list_all_items()


def list_items_by_category(category: str, csv_path: Optional[str] = None) -> List[Dict[str, str]]:
    """List items from a specific category."""
    manager = FridgeManager(csv_path)
    return manager.list_items_by_category(category)


def list_items_close_to_expiry(days_threshold: int, csv_path: Optional[str] = None) -> List[Dict[str, str]]:
    """List items close to their best before date."""
    manager = FridgeManager(csv_path)
    return manager.list_items_close_to_expiry(days_threshold)


def update_item(item_name: str, updates: Dict[str, str], 
               match_index: Optional[int] = None, csv_path: Optional[str] = None) -> bool:
    """Update an existing item based on name."""
    manager = FridgeManager(csv_path)
    return manager.update_item(item_name, updates, match_index)


def delete_item(item_name: str, match_index: Optional[int] = None, 
               csv_path: Optional[str] = None) -> bool:
    """Delete an existing item by name."""
    manager = FridgeManager(csv_path)
    return manager.delete_item(item_name, match_index)


def add_item(item_name: str, category: str, purchase_date: str,
            best_before_date: str = "", items: str = "1", 
            csv_path: Optional[str] = None) -> bool:
    """Add a new item to the fridge."""
    manager = FridgeManager(csv_path)
    return manager.add_item(item_name, category, purchase_date, best_before_date, items)


if __name__ == "__main__":
    # Example usage
    manager = FridgeManager()
    
    print("All items in fridge:")
    for item in manager.list_all_items():
        print(f"- {item['item name']} ({item['category']}) - {item['items']}")
    
    print("\nDairy items:")
    dairy_items = manager.list_items_by_category("Dairy")
    for item in dairy_items:
        print(f"- {item['item name']} - {item['items']}")
    
    print("\nItems expiring in 5 days:")
    expiring_items = manager.list_items_close_to_expiry(5)
    for item in expiring_items:
        print(f"- {item['item name']} expires on {item['best before date']}")
