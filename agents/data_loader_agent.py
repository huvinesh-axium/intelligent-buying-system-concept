import pandas as pd
from typing import Dict, Any
from .base_agent import BaseAgent

class DataLoaderAgent(BaseAgent):
    def __init__(self):
        super().__init__("DataLoader")
        self.data_cache = {}
    
    def load_suppliers(self) -> pd.DataFrame:
        if 'suppliers' not in self.data_cache:
            self.data_cache['suppliers'] = pd.read_csv('data/suppliers.csv')
        return self.data_cache['suppliers']
    
    def load_inventory(self) -> pd.DataFrame:
        if 'inventory' not in self.data_cache:
            df = pd.read_csv('data/inventory.csv')
            df['last_updated'] = pd.to_datetime(df['last_updated'])
            self.data_cache['inventory'] = df
        return self.data_cache['inventory']
    
    def load_purchase_orders(self) -> pd.DataFrame:
        if 'purchase_orders' not in self.data_cache:
            df = pd.read_csv('data/purchase_orders.csv')
            df['order_date'] = pd.to_datetime(df['order_date'])
            df['expected_delivery_date'] = pd.to_datetime(df['expected_delivery_date'])
            df['actual_delivery_date'] = pd.to_datetime(df['actual_delivery_date'], errors='coerce')
            self.data_cache['purchase_orders'] = df
        return self.data_cache['purchase_orders']
    
    def get_stockout_items(self) -> pd.DataFrame:
        inventory = self.load_inventory()
        return inventory[inventory['stock_quantity'] <= inventory['reorder_level']]
    
    def get_supplier_performance(self) -> pd.DataFrame:
        po_df = self.load_purchase_orders()
        suppliers_df = self.load_suppliers()
        
        # Calculate delivery performance metrics
        completed_orders = po_df[po_df['order_status'] == 'Completed'].copy()
        completed_orders['delivery_delay'] = (
            completed_orders['actual_delivery_date'] - completed_orders['expected_delivery_date']
        ).dt.days
        
        performance = completed_orders.groupby('supplier_id').agg({
            'order_id': 'count',
            'delivery_delay': ['mean', 'std'],
            'quantity_received': 'sum',
            'was_expedited': 'sum',
            'was_substitution': 'sum'
        }).round(2)
        
        performance.columns = ['total_orders', 'avg_delay_days', 'delay_std', 
                              'total_quantity', 'expedited_orders', 'substitutions']
        performance['on_time_rate'] = (
            (performance['total_orders'] - performance['expedited_orders']) / performance['total_orders'] * 100
        ).round(2)
        
        return performance.merge(suppliers_df, on='supplier_id', how='left')
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'suppliers': self.load_suppliers(),
            'inventory': self.load_inventory(),
            'purchase_orders': self.load_purchase_orders(),
            'stockout_items': self.get_stockout_items(),
            'supplier_performance': self.get_supplier_performance()
        }
