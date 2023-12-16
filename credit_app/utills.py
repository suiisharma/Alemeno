from datetime import date
from .models import Loan
from decimal import Decimal
from django.db.models import Sum


# Credit rating calculator (I have done few assumptions in this)
def credit_calculator(
    past_loans_paid_on_time,
    total_past_loans,
    loan_activity_in_current_year,
    loan_approved_volume,
    approved_limit,
):
    if approved_limit < loan_approved_volume:
        return 0
    credit_rating = 0

    if (past_loans_paid_on_time * 100) // total_past_loans > 70:
        credit_rating += 15

    if loan_activity_in_current_year > 0:
        credit_rating += 10

    if (loan_approved_volume * 100) // approved_limit > 60:
        credit_rating += 25
    return credit_rating


def calculate_past_loans_paid_on_time(customer_id):
    current_date = date.today()
    loans = Loan.objects.filter(customer_id=customer_id)

    past_loans_paid_on_time = sum(
        1
        for loan in loans
        if loan.end_date <= current_date and loan.emis_paid_on_time == loan.tenure
    )
    return past_loans_paid_on_time


def calculate_total_past_loans(customer_id):
    current_date = date.today()
    total_past_loans = Loan.objects.filter(
        customer_id=customer_id, end_date__lt=current_date
    ).count()
    return total_past_loans


def calculate_loan_in_activity_current_year(customer_id):
    current_year = date.today().year
    start_of_year = date(current_year, 1, 1)
    end_of_year = date(current_year, 12, 31)

    loan_activity_in_current_year = Loan.objects.filter(
        customer_id=customer_id,
        start_date__gte=start_of_year,
        end_date__lte=end_of_year,
    ).count()

    return loan_activity_in_current_year


def calculate_loan_approved_volume(customer_id):
    current_date = date.today()
    loan_approved_volume = (
        Loan.objects.filter(
            customer_id=customer_id,
            end_date__gt=current_date,
        ).aggregate(Sum("loan_amount"))["loan_amount__sum"]
        or 0
    )

    return loan_approved_volume


def calculate_monthly_installment(loan_amount, tenure, interest_rate):
    monthly_interest_rate = Decimal(interest_rate) / Decimal(1200)
    numerator = (
        Decimal(loan_amount)
        * Decimal(monthly_interest_rate)
        * ((1 + Decimal(monthly_interest_rate)) ** Decimal(tenure))
    )
    denominator = ((1 + monthly_interest_rate) ** tenure) - 1
    monthly_payment = numerator / denominator
    return monthly_payment

