from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Loan, Customer
from datetime import timedelta, datetime, date
from django.db.models import Sum
import uuid
from decimal import Decimal
from .utills import calculate_past_loans_paid_on_time,calculate_total_past_loans,calculate_loan_approved_volume,calculate_loan_in_activity_current_year,credit_calculator,calculate_monthly_installment


@api_view(["Post"])
def register_customer(request):
    try:
        if request.method == "POST":
            first_name = request.data.get("first_name")
            last_name = request.data.get("last_name")
            age = request.data.get("age")
            monthly_income = request.data.get("monthly_income")
            phone_number = request.data.get("phone_number")
            existing_customer = Customer.objects.filter(
                first_name=first_name,
                last_name=last_name,
                age=age,
                monthly_income=monthly_income,
                phone_number=phone_number,
            )
            if existing_customer:
                return Response({"message": "Customer already exists"}, status=400)
            approved_limit = round(36 * monthly_income, -5)
            if first_name and last_name and age and monthly_income and phone_number:
                new_customer = Customer.objects.create(
                    customer_id=uuid.uuid4(),
                    first_name=first_name,
                    last_name=last_name,
                    age=age,
                    monthly_income=monthly_income,
                    phone_number=phone_number,
                    approved_limit=approved_limit,
                )
                resposne_data = {
                    "customer_id": new_customer.customer_id,
                    "name": f"{first_name}{ last_name}",
                    "age": age,
                    "monthly_income": monthly_income,
                    "approved_limit": approved_limit,
                    "phone_number": phone_number,
                }
                return Response(resposne_data, status=201)
            else:
                return Response({"message": "Invalid input"}, status=400)
        else:
            return Response({"message": "Invalid request method"}, status=405)
    except Exception as e:
        return Response({"message": str(e)}, status=500)


@api_view(["Post"])
def check_loan_eligibility(request):
    try:
        if request.method == "POST":
            customer_id = request.data.get("customer_id")

            customer = Customer.objects.get(customer_id=customer_id)
            if customer is None:
                return Response({"message": "Customer not found"}, status=404)
            else:
                loan_amount = request.data.get("loan_amount")
                interest_rate = request.data.get("interest_rate")
                tenure = request.data.get("tenure")
                past_loan_paid_on_time = calculate_past_loans_paid_on_time(customer_id)
                total_past_loans = calculate_total_past_loans(customer_id)
                loan_approved_volume = calculate_loan_approved_volume(customer_id)
                loan_activity_in_current_year = calculate_loan_in_activity_current_year(
                    customer_id
                )
                credit_rating = credit_calculator(
                    past_loan_paid_on_time,
                    total_past_loans,
                    loan_activity_in_current_year,
                    Decimal(loan_approved_volume) + Decimal(loan_amount),
                    customer.approved_limit,
                )

                if credit_rating < 10:
                    return Response(
                        {
                            "customer_id": customer_id,
                            "approval": 0,
                            "interest_rate": interest_rate,
                            "tenure": tenure,
                            "monthly_installments": calculate_monthly_installment(
                                loan_amount, tenure, interest_rate
                            ),
                        },
                        status=200,
                    )
                current_date = datetime.now()
                sum_current_emi = (
                    Loan.objects.filter(
                        customer_id=customer_id, end_date__gt=current_date
                    ).aggregate(Sum("monthly_repayment"))["monthly_repayment__sum"]
                    or 0
                )

                if (sum_current_emi * 100) / customer.monthly_income > 50:
                    return Response(
                        {
                            "customer_id": customer_id,
                            "approval": 0,
                            "interest_rate": interest_rate,
                            "tenure": tenure,
                            "monthly_installments": calculate_monthly_installment(
                                loan_amount, tenure, interest_rate
                            ),
                        },
                        status=200,
                    )

                if credit_rating >= 50:
                    return Response(
                        {
                            "customer_id": customer_id,
                            "approval": 1,
                            "interest_rate": interest_rate,
                            "corrected_interest_rate": interest_rate,
                            "tenure": tenure,
                            "monthly_installments": calculate_monthly_installment(
                                loan_amount, tenure, interest_rate
                            ),
                        },
                        status=200,
                    )
                if credit_rating < 50 and credit_rating >= 30:
                    return Response(
                        {
                            "customer_id": customer_id,
                            "approval": 1,
                            "interest_rate": interest_rate,
                            "corrected_interest_rate": max(interest_rate, 12),
                            "tenure": tenure,
                            "monthly_installments": calculate_monthly_installment(
                                loan_amount, tenure, max(interest_rate, 12)
                            ),
                        },
                        status=200,
                    )

                return Response(
                    {
                        "customer_id": customer_id,
                        "approval": 1,
                        "interest_rate": interest_rate,
                        "corrected_interest_rate": max(interest_rate, 16),
                        "tenure": tenure,
                        "monthly_installments": calculate_monthly_installment(
                            loan_amount, tenure, max(interest_rate, 16)
                        ),
                    },
                    status=200,
                )
        else:
            return Response({"message": "Invalid request method"}, status=405)
    except Exception as e:
        return Response({"message": str(e)}, status=500)


@api_view(["POST"])
def create_loan(request):
    try:
        if request.method == "POST":
            customer_id = request.data.get("customer_id")

            customer = Customer.objects.get(customer_id=customer_id)
            if customer is None:
                return Response({"message": "Customer not found"}, status=404)
            else:
                loan_amount = request.data.get("loan_amount")
                interest_rate = request.data.get("interest_rate")
                tenure = request.data.get("tenure")
                past_loan_paid_on_time = calculate_past_loans_paid_on_time(customer_id)
                total_past_loans = calculate_total_past_loans(customer_id)
                loan_approved_volume = calculate_loan_approved_volume(customer_id)
                loan_activity_in_current_year = calculate_loan_in_activity_current_year(
                    customer_id
                )
                credit_rating = credit_calculator(
                    past_loan_paid_on_time,
                    total_past_loans,
                    loan_activity_in_current_year,
                    Decimal(loan_approved_volume) + Decimal(loan_amount),
                    customer.approved_limit,
                )

                if credit_rating < 10:
                    return Response(
                        {
                            "loan_id": "",
                            "customer_id": customer_id,
                            "loan_approved": 0,
                            "message": "We regret to inform you that your loan application did not meet our eligibility criteria. We encourage you to review our criteria and apply again in the future. Thank you for considering our services.",
                            "monthly_installments": "",
                        },
                        status=403,
                    )
                current_date = datetime.now()
                sum_current_emi = (
                    Loan.objects.filter(
                        customer_id=customer_id, end_date__gt=current_date
                    ).aggregate(Sum("monthly_repayment"))["monthly_repayment__sum"]
                    or 0
                )

                if (sum_current_emi * 100) / customer.monthly_income > 50:
                    return Response(
                        {
                            "loan_id": "",
                            "customer_id": customer_id,
                            "loan_approved": 0,
                            "message": "We regret to inform you that your loan application did not meet our eligibility criteria. We encourage you to review our criteria and apply again in the future. Thank you for considering our services.",
                            "monthly_installments": "",
                        },
                        status=403,
                    )

                if credit_rating >= 50:
                    new_loan = Loan.objects.create(
                        customer=customer,
                        loan_id=uuid.uuid4(),
                        loan_amount=loan_amount,
                        interest_rate=interest_rate,
                        tenure=tenure,
                        monthly_repayment=calculate_monthly_installment(
                            loan_amount, tenure, interest_rate
                        ),
                        emis_paid_on_time=0,
                        start_date=datetime.now(),
                        end_date=datetime(
                            datetime.now().year
                            + ((datetime.now().month + tenure - 1) // 12),
                            ((datetime.now().month + tenure - 1) % 12) + 1,
                            1,
                        )
                        - timedelta(days=1),
                    )
                    return Response(
                        {
                            "loan_id": new_loan.loan_id,
                            "customer_id": customer_id,
                            "loan_approved": 1,
                            "message": "Loan approved successfully",
                            "monthly_installments": new_loan.monthly_repayment,
                        },
                        status=201,
                    )
                if credit_rating < 50 and credit_rating >= 30:
                    if interest_rate > 12:
                        new_loan = Loan.objects.create(
                            customer=customer,
                            loan_id=uuid.uuid4(),
                            loan_amount=loan_amount,
                            interest_rate=interest_rate,
                            tenure=tenure,
                            monthly_repayment=calculate_monthly_installment(
                                loan_amount, tenure, interest_rate
                            ),
                            emis_paid_on_time=0,
                            start_date=datetime.now(),
                            end_date=datetime(
                                datetime.now().year
                                + ((datetime.now().month + tenure - 1) // 12),
                                ((datetime.now().month + tenure - 1) % 12) + 1,
                                1,
                            )
                            - timedelta(days=1),
                        )
                        return Response(
                            {
                                "loan_id": new_loan.loan_id,
                                "customer_id": customer_id,
                                "loan_approved": 1,
                                "message": "Loan approved successfully",
                                "monthly_installments": new_loan.monthly_repayment,
                            },
                            status=201,
                        )

                    else:
                        return Response(
                            {
                                "loan_id": "",
                                "customer_id": customer_id,
                                "loan_approved": 0,
                                "message": "We regret to inform you that your loan application did not meet our eligibility criteria. We encourage you to review our criteria and apply again in the future. Thank you for considering our services.",
                                "monthly_installments": "",
                            },
                            status=403,
                        )

                if interest_rate > 16:
                    new_loan = Loan.objects.create(
                        customer=customer,
                        loan_id=uuid.uuid4(),
                        loan_amount=loan_amount,
                        interest_rate=interest_rate,
                        tenure=tenure,
                        monthly_repayment=calculate_monthly_installment(
                            loan_amount, tenure, interest_rate
                        ),
                        emis_paid_on_time=0,
                        start_date=datetime.now(),
                        end_date=datetime(
                            datetime.now().year
                            + ((datetime.now().month + tenure - 1) // 12),
                            ((datetime.now().month + tenure - 1) % 12) + 1,
                            1,
                        )
                        - timedelta(days=1),
                    )
                    return Response(
                        {
                            "loan_id": new_loan.loan_id,
                            "customer_id": customer_id,
                            "loan_approved": 1,
                            "message": "Loan approved successfully",
                            "monthly_installments": new_loan.monthly_repayment,
                        },
                        status=201,
                    )

                else:
                    return Response(
                        {
                            "loan_id": "",
                            "customer_id": customer_id,
                            "loan_approved": 0,
                            "message": "We regret to inform you that your loan application did not meet our eligibility criteria. We encourage you to review our criteria and apply again in the future. Thank you for considering our services.",
                            "monthly_installments": "",
                        },
                        status=403,
                    )

        else:
            return Response({"message": "Invalid request method"}, status=405)

    except Exception as e:
        return Response({"message": str(e)}, status=500)


@api_view(["POST"])
def view_loan(request, loan_id):
    try:
        if request.method == "POST":
            loan = Loan.objects.get(loan_id=loan_id)
            if loan is None:
                return Response({"message": "Loan not found"}, status=404)
            else:
                return Response(
                    {
                        "loan_id": loan.loan_id,
                        "customer": {
                            "customer_id": loan.customer.customer_id,
                            "first_name": loan.customer.first_name,
                            "last_name": loan.customer.last_name,
                            "phone_number": loan.customer.phone_number,
                            "age": loan.customer.age,
                        },
                        "interest_rate": loan.interest_rate,
                        "monthly_installments": loan.monthly_repayment,
                        "tenure": loan.tenure,
                    },
                    status=200,
                )
        else:
            return Response({"message": "Invalid request method"}, status=405)
    except Exception as e:
        return Response({"message": str(e)}, status=500)


@api_view(["POST"])
def view_loans(request, customer_id):
    try:
        if request.method == "POST":
            customer = Customer.objects.get(customer_id=customer_id)
            if customer is None:
                return Response({"message": "Customer not found"}, status=404)
            else:
                loans = Loan.objects.filter(customer=customer)
                if loans is None:
                    return Response(
                        {"message": "There are no loans of this customer"}, status=404
                    )
                else:
                    return Response(
                        [
                            {
                                "loan_id": loan.loan_id,
                                "loan_amount": loan.loan_amount,
                                "interest_rate": loan.interest_rate,
                                "monthly_installments": loan.monthly_repayment,
                                "repayments_left": loan.tenure - loan.emis_paid_on_time,
                            }
                            for loan in loans
                        ],
                        status=200,
                    )
                    return Response(
                        {
                            "loan_id": loan.loan_id,
                            "customer": {
                                "customer_id": loan.customer.customer_id,
                                "first_name": loan.customer.first_name,
                                "last_name": loan.customer.last_name,
                                "phone_number": loan.customer.phone_number,
                                "age": loan.customer.age,
                            },
                            "interest_rate": loan.interest_rate,
                            "monthly_installments": loan.monthly_repayment,
                            "tenure": loan.tenure,
                        },
                        status=200,
                    )
        else:
            return Response({"message": "Invalid request method"}, status=405)
    except Exception as e:
        return Response({"message": str(e)}, status=500)
