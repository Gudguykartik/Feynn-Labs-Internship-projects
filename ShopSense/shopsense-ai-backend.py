import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta
import joblib
import warnings
warnings.filterwarnings('ignore')

class ShopSenseAI:
    def __init__(self):
        self.inventory_model = None
        self.pricing_model = None
        self.customer_segmentation_model = None
        self.scaler = StandardScaler()
        
    def train_inventory_optimization(self, historical_data):
        """
        Train the inventory optimization model using historical sales data
        
        Parameters:
        historical_data (pd.DataFrame): DataFrame containing columns:
            - date: Date of sale
            - product_id: Unique identifier for each product
            - quantity_sold: Number of units sold
            - stock_level: Inventory level at start of day
            - is_weekend: Boolean flag for weekend
            - is_holiday: Boolean flag for holiday
        """
        # Prepare features for inventory prediction
        X = historical_data[['is_weekend', 'is_holiday', 'stock_level']].copy()
        y = historical_data['quantity_sold']
        
        # Train random forest model for demand prediction
        self.inventory_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.inventory_model.fit(X, y)
        
        return self.inventory_model
    
    def predict_optimal_inventory(self, current_stock, is_weekend, is_holiday):
        """
        Predict optimal inventory levels based on current conditions
        """
        if self.inventory_model is None:
            raise ValueError("Model not trained. Please train the model first.")
            
        features = np.array([[is_weekend, is_holiday, current_stock]])
        predicted_demand = self.inventory_model.predict(features)[0]
        
        # Calculate optimal reorder point with safety stock
        safety_stock = predicted_demand * 0.2  # 20% safety stock
        reorder_point = predicted_demand + safety_stock
        
        return {
            'predicted_demand': round(predicted_demand, 2),
            'reorder_point': round(reorder_point, 2),
            'safety_stock': round(safety_stock, 2)
        }
    
    def train_dynamic_pricing(self, pricing_data):
        """
        Train the dynamic pricing model
        
        Parameters:
        pricing_data (pd.DataFrame): DataFrame containing:
            - price: Historical price points
            - demand: Corresponding demand
            - competitor_price: Competitor's price
            - cost: Product cost
            - inventory_level: Current stock level
        """
        X = pricing_data[['competitor_price', 'cost', 'inventory_level']].copy()
        y = pricing_data['demand']
        
        self.pricing_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.pricing_model.fit(X, y)
        
        return self.pricing_model
    
    def recommend_price(self, competitor_price, cost, inventory_level):
        """
        Recommend optimal price based on market conditions
        """
        if self.pricing_model is None:
            raise ValueError("Pricing model not trained. Please train the model first.")
            
        # Generate price points around competitor price
        price_range = np.linspace(cost * 1.1, competitor_price * 1.2, 50)
        max_revenue = 0
        optimal_price = cost * 1.5  # Default markup
        
        for price in price_range:
            features = np.array([[competitor_price, cost, inventory_level]])
            predicted_demand = self.pricing_model.predict(features)[0]
            revenue = predicted_demand * (price - cost)
            
            if revenue > max_revenue:
                max_revenue = revenue
                optimal_price = price
        
        return {
            'recommended_price': round(optimal_price, 2),
            'estimated_revenue': round(max_revenue, 2),
            'profit_margin': round((optimal_price - cost) / optimal_price * 100, 2)
        }
    
    def segment_customers(self, customer_data):
        """
        Segment customers based on their behavior
        
        Parameters:
        customer_data (pd.DataFrame): DataFrame containing:
            - recency: Days since last purchase
            - frequency: Number of purchases
            - monetary: Total spend amount
        """
        # Prepare RFM data
        X = customer_data[['recency', 'frequency', 'monetary']].copy()
        X = self.scaler.fit_transform(X)
        
        # Train KMeans clustering
        self.customer_segmentation_model = KMeans(n_clusters=4, random_state=42)
        segments = self.customer_segmentation_model.fit_predict(X)
        
        # Analyze segments
        customer_data['segment'] = segments
        segment_analysis = customer_data.groupby('segment').agg({
            'recency': 'mean',
            'frequency': 'mean',
            'monetary': 'mean'
        })
        
        # Label segments
        segment_labels = {
            segment: self._get_segment_label(row['recency'], row['frequency'], row['monetary'])
            for segment, row in segment_analysis.iterrows()
        }
        
        return segment_labels, customer_data['segment']
    
    def _get_segment_label(self, recency, frequency, monetary):
        """Helper function to label customer segments"""
        if frequency > 0.5 and monetary > 0.5:
            return 'VIP'
        elif frequency > 0.5 and monetary <= 0.5:
            return 'Loyal'
        elif recency <= 0.5:
            return 'Recent'
        else:
            return 'At Risk'
    
    def generate_recommendations(self, customer_segment, product_data):
        """
        Generate personalized product recommendations based on customer segment
        """
        recommendations = {
            'VIP': {
                'discount_level': 0.15,
                'marketing_message': 'Exclusive VIP offer just for you!',
                'product_focus': 'Premium items'
            },
            'Loyal': {
                'discount_level': 0.1,
                'marketing_message': 'Special offer for our loyal customer!',
                'product_focus': 'New arrivals'
            },
            'Recent': {
                'discount_level': 0.05,
                'marketing_message': 'Welcome back! Check out our latest items',
                'product_focus': 'Popular items'
            },
            'At Risk': {
                'discount_level': 0.2,
                'marketing_message': 'We miss you! Come back and save big',
                'product_focus': 'Best sellers'
            }
        }
        
        return recommendations.get(customer_segment, recommendations['Recent'])

    def save_models(self, path):
        """Save trained models to disk"""
        if self.inventory_model:
            joblib.dump(self.inventory_model, f'{path}/inventory_model.joblib')
        if self.pricing_model:
            joblib.dump(self.pricing_model, f'{path}/pricing_model.joblib')
        if self.customer_segmentation_model:
            joblib.dump(self.customer_segmentation_model, f'{path}/segmentation_model.joblib')
        if self.scaler:
            joblib.dump(self.scaler, f'{path}/scaler.joblib')

    def load_models(self, path):
        """Load trained models from disk"""
        try:
            self.inventory_model = joblib.load(f'{path}/inventory_model.joblib')
            self.pricing_model = joblib.load(f'{path}/pricing_model.joblib')
            self.customer_segmentation_model = joblib.load(f'{path}/segmentation_model.joblib')
            self.scaler = joblib.load(f'{path}/scaler.joblib')
        except Exception as e:
            print(f"Error loading models: {str(e)}")
            raise

# Example usage
def demo_shopsense():
    # Initialize ShopSenseAI
    ai = ShopSenseAI()
    
    # Sample historical data for inventory optimization
    historical_data = pd.DataFrame({
        'date': pd.date_range(start='2024-01-01', periods=100),
        'product_id': [1] * 100,
        'quantity_sold': np.random.normal(50, 10, 100),
        'stock_level': np.random.normal(200, 20, 100),
        'is_weekend': [i.weekday() >= 5 for i in pd.date_range(start='2024-01-01', periods=100)],
        'is_holiday': [False] * 100
    })
    
    # Train inventory model
    ai.train_inventory_optimization(historical_data)
    
    # Get inventory recommendations
    inventory_recommendation = ai.predict_optimal_inventory(
        current_stock=180,
        is_weekend=True,
        is_holiday=False
    )
    print("\nInventory Optimization Results:")
    print(inventory_recommendation)
    
    # Sample pricing data
    pricing_data = pd.DataFrame({
        'price': np.random.uniform(10, 50, 100),
        'demand': np.random.normal(100, 20, 100),
        'competitor_price': np.random.uniform(15, 45, 100),
        'cost': np.random.uniform(5, 25, 100),
        'inventory_level': np.random.uniform(50, 200, 100)
    })
    
    # Train pricing model
    ai.train_dynamic_pricing(pricing_data)
    
    # Get price recommendation
    price_recommendation = ai.recommend_price(
        competitor_price=25.0,
        cost=15.0,
        inventory_level=150
    )
    print("\nDynamic Pricing Results:")
    print(price_recommendation)
    
    # Sample customer data
    customer_data = pd.DataFrame({
        'customer_id': range(100),
        'recency': np.random.uniform(1, 100, 100),
        'frequency': np.random.uniform(1, 50, 100),
        'monetary': np.random.uniform(100, 5000, 100)
    })
    
    # Segment customers
    segment_labels, segments = ai.segment_customers(customer_data)
    print("\nCustomer Segmentation Results:")
    print("Segment Labels:", segment_labels)
    
    # Generate recommendations for a VIP customer
    recommendations = ai.generate_recommendations('VIP', None)
    print("\nPersonalized Recommendations for VIP:")
    print(recommendations)

if __name__ == "__main__":
    demo_shopsense()
