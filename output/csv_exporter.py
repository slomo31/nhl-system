"""CSV Exporter"""
import pandas as pd
import os
from datetime import datetime

class CSVExporter:
    """Export predictions to CSV"""
    
    def export_decisions(self, decisions):
        """Export daily decisions"""
        os.makedirs('output_archive/decisions', exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
        filename = f'output_archive/decisions/{timestamp}_decisions.csv'
        
        df = pd.DataFrame(decisions)
        df.to_csv(filename, index=False)
        
        return filename
