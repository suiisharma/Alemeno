import threading
import pandas as pd
from credit_app.models import Customer,Loan
import time
import os


class BackgroundWorker(threading.Thread):
    def __init__(self):
        super().__init__()
        self._is_running = False

    def run(self):
        self._is_running = True

        # Perform data ingestion tasks
        self.ingest_customer_data()
        self.ingest_loan_data()

    def stop(self):
        self._is_running = False

    def ingest_customer_data(self):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(current_dir, "data")
            customer_data_path = os.path.join(data_dir, "customer_data.xlsx")
            customer_data = pd.read_excel(customer_data_path)
            for index, row in customer_data.iterrows():
                Customer.objects.create(
                    customer_id=row["Customer ID"],
                    first_name=row["First Name"],
                    last_name=row["Last Name"],
                    phone_number=str(row["Phone Number"]),
                    monthly_income=row["Monthly Salary"],
                    approved_limit=row["Approved Limit"],
                    age=row["Age"],
                )
            print("Customer data ingestion completed.")
        except Exception as e:
            print(f"Error ingesting customer data: {str(e)}")

    def ingest_loan_data(self):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(current_dir, "data")
            loan_data_path = os.path.join(data_dir, "loan_data.xlsx")
            loan_data = pd.read_excel(loan_data_path)
            for index, row in loan_data.iterrows():
                customer = Customer.objects.get(customer_id=row["Customer ID"])
                Loan.objects.create(
                    customer=customer,
                    loan_id=row["Loan ID"],
                    loan_amount=row["Loan Amount"],
                    tenure=row["Tenure"],
                    interest_rate=row["Interest Rate"],
                    monthly_repayment=row["Monthly payment"],
                    emis_paid_on_time=row["EMIs paid on Time"],
                    start_date=row["Date of Approval"],
                    end_date=row["End Date"],
                )
            print("Loan data ingestion completed.")
        except Exception as e:
            print(f"Error ingesting loan data: {str(e)}")
