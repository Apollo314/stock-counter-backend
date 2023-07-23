from decimal import Decimal
from uuid import uuid4

from django.contrib.auth.models import AnonymousUser, Group, Permission
from django.test import TestCase
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.test import APIClient

from inventory.models import Item, StockUnit, Warehouse
from invoice.models import Invoice
from invoice.tests.test_views import TestInvoice
from payments.models import Bank, PaymentAccount, PaymentType
from payments.serializers import PaymentSerializer
from stakeholder.models import Stakeholder, StakeholderRole
from users.models import User
from utilities.enums import Currency


def create_employee_group() -> Group:
    employee_group = Group.objects.create(name="employee_group")
    permissions = Permission.objects.filter(
        codename__in=[
            "add_payment",
            "change_payment",
            "delete_payment",
            "view_payment",
            #
            "add_paymentaccount",
            "change_paymentaccount",
            "delete_paymentaccount",
            "view_paymentaccount",
            #
            "add_invoicepayment",
            "change_invoicepayment",
            "delete_invoicepayment",
            "view_invoicepayment",
            #
            "add_invoice",
            "change_invoice",
            "delete_invoice",
            "view_invoice",
            #
            "view_item",
        ]
    )
    employee_group.permissions.set(permissions)
    employee_group.save()
    return employee_group


def create_stakeholder() -> Stakeholder:
    return Stakeholder.objects.create(
        name="Customer for payments",
        role=StakeholderRole.customer_and_supplier,
        shortname="Customer",
        phone="",
        email="",
        vkntckn="",
        address="",
    )


def create_warehouse() -> Warehouse:
    return Warehouse.objects.create(
        name="Warehouse for payments",
    )


def get_or_create_bank():
    return Bank.objects.get_or_create(
        name="Test Bank",
    )


def create_payment_account_for_stakeholder(
    stakeholder: Stakeholder, client: APIClient
) -> PaymentAccount:
    url = reverse("payment-accounts-list")
    bank, created = get_or_create_bank()
    res = client.post(
        url,
        {
            "name": f"{stakeholder.name}'s payment account",
            "stakeholder": stakeholder.id,
            "bank": bank.id,
            "account_number": "1234",
            "iban": "TR 1234 1234 1234 1234",
        },
        format="json",
    )
    return res


class TestInvoiceCreation(TestCase):
    def set_up_employee_client(self):
        self.employee_group = create_employee_group()
        self.user: User = User.objects.create_user(
            username="payments_user", password="password"
        )
        self.user.groups.add(self.employee_group)
        self.user.save()
        self.nonemployee_user: User = User.objects.create_user(
            username="payments_nonemployee_user", password="password"
        )
        self.employee_client = APIClient()
        self.employee_client.login(username="payments_user", password="password")
        self.nonemployee_client = APIClient()
        self.nonemployee_client.login(
            username="payments_nonemployee_user", password="password"
        )
        self.anon_client: APIClient = APIClient()
        self.anon_client.force_authenticate(user=AnonymousUser())

    def setUp(self) -> None:
        self.set_up_employee_client()
        self.stakeholder = create_stakeholder()
        self.warehouse = create_warehouse()
        paymentaccount_res = create_payment_account_for_stakeholder(
            stakeholder=self.stakeholder, client=self.employee_client
        )
        self.stakeholder_paymentaccount = PaymentAccount.objects.get(
            id=paymentaccount_res.data["id"]
        )
        self.paymentaccount = PaymentAccount.objects.create(
            name="Company payment account",
        )
        self.stock_unit, created = StockUnit.objects.get_or_create(name="kg")
        self.item = Item.objects.create(
            name="test item for payments",
            stock_unit=self.stock_unit,
            kdv=18,
            buyprice=Decimal("123.44"),
            sellprice=Decimal("150.0"),
        )

    def test_can_create_payment_account(self):
        url = reverse("payment-accounts-list")
        res: Response = self.employee_client.post(
            url,
            {
                "name": "Test payment account",
                "stakeholder": self.stakeholder.id,
                "bank": self.stakeholder_paymentaccount.bank.id,
                "account_number": "1234",
                "iban": "TR 1234 1234 1234 1234",
            },
            format="json",
        )
        self.assertEquals(res.status_code, 201)

    def test_can_create_invoice_payment(self):
        url = reverse("invoice-payments-list")
        invoice_res = TestInvoice.create_invoice(
            client=self.employee_client,
            items=[self.item],
            amounts=[Decimal("100")],
            stakeholder=self.stakeholder,
            warehouse=self.warehouse,
        )
        payments_count_before = self.stakeholder_paymentaccount.payments_made.count()
        invoice = Invoice.objects.get(id=invoice_res.data["id"])
        res: Response = self.employee_client.post(
            url,
            {
                "invoice": invoice.id,
                "payment": {
                    "payer": self.stakeholder_paymentaccount.id,
                    "receiver": self.paymentaccount.id,
                    "amount": Decimal("100"),
                    "currency": Currency.turkish_lira,
                    "payment_type": PaymentType.cash,
                },
            },
            format="json",
        )
        # payment is created by InvoicePayment
        payments_count_after = self.stakeholder_paymentaccount.payments_made.count()

        self.assertGreater(payments_count_after, payments_count_before)
        self.assertEquals(res.status_code, 201)
