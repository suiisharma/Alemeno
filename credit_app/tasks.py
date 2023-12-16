import pandas as pd
from django_q.tasks import async_task
from .models import Customer,Loan
import os

def ingest_customer_data():
    try:
      
        for index, row in customer_data.iterrows():
          
            Customer.objects.create(
                
            )

        return True 
    except Exception as e:
        return str(e)


def ingest_loan_data():
    try:
        current_dir=os.path.dirname(os.path.abspath(__file__))
        loan_data_path=os.path.join(current_dir,'loan_data.xlsx')
        loan_data = pd.read_excel(loan_data_path)
        # Iterate through rows and create Loan instances
        for index, row in loan_data.iterrows():
            # Retrieve customer using customer_id (assuming it's in the Excel)

            # Create Loan instances and associate with respective customers
            Loan.objects.create(
                
                # Add other fields as per your Excel columns
            )

        return True  # Return True if successful
    except Exception as e:
        return str(e)  # Return error message if any exception occurs


def start_data_ingestion():
    # Start customer data ingestion asynchronously
    async_task(ingest_customer_data)
    
    # Start loan data ingestion after customer data is ingested
    async_task(ingest_loan_data)


start_data_ingestion()