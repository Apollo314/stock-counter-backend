from decimal import Decimal
from uuid import uuid4
from django.contrib.auth.models import Group, Permission, AnonymousUser
from django.test import TestCase
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.test import APIClient, APIRequestFactory

from inventory.models import Item, StockUnit, Warehouse, WarehouseItemStock
from inventory.serializers import (
    ItemInSerializer,
    ItemOutSerializer,
    WarehouseSerializer,
)
from stakeholder.models import Stakeholder, StakeholderRole
from stakeholder.serializers import StakeholderSerializer
from users.models import User
from utilities.enums import Currency, InvoiceType


def create_employee_group() -> Group:
    employee_group = Group.objects.create(name="employee_group")
    permissions = Permission.objects.filter(
        codename__in=[
            "add_item",
            "change_item",
            "delete_item",
            "view_item",
            #
            "add_invoice",
            "change_invoice",
            "delete_invoice",
            "view_invoice",
        ]
    )
    employee_group.permissions.set(permissions)
    employee_group.save()
    return employee_group


class TestItemCreation(TestCase):
    def set_up_employee_client(self):
        self.employee_group = create_employee_group()
        self.user: User = User.objects.create_user(
            username="invoicec_creating_employee", password="password"
        )
        self.user.groups.add(self.employee_group)
        self.user.save()
        self.nonemployee_user: User = User.objects.create_user(
            username="notemployee1", password="password"
        )
        self.employee_client = APIClient()
        self.employee_client.login(
            username="invoicec_creating_employee", password="password"
        )
        self.nonemployee_client = APIClient()
        self.nonemployee_client.login(username="notemployee1", password="password")
        self.anon_client: APIClient = APIClient()
        self.anon_client.force_authenticate(user=AnonymousUser())

    def setUp(self) -> None:
        self.set_up_employee_client()
        self.stock_unit = StockUnit.objects.create(name="kg")
        self.item1: Item = Item.objects.create(
            name="test item 1",
            description="Test Description 1",
            stock_unit=self.stock_unit,
            kdv=18,
            buyprice=Decimal("123.44"),
            sellprice=Decimal("150.0"),
        )
        self.item2: Item = Item.objects.create(
            name="test item 2",
            description="Test Description 2",
            stock_unit=self.stock_unit,
            kdv=18,
            buyprice=Decimal("50.50"),
            sellprice=Decimal("99.99"),
        )
        self.warehouse = Warehouse.objects.create(name="Ana Depo")
        self.stakeholder = Stakeholder.objects.create(
            name="sh1", shortname="sh1", role=StakeholderRole.customer_and_supplier
        )

    def create_invoice(
        self,
        client: APIClient,
        items: list[Item],
        amounts: list[Decimal],
        invoice_type: InvoiceType = InvoiceType.purchase,
    ):
        url = reverse("invoice-list")
        inventory_items = [
            {
                "stock_movement": {
                    "warehouse_item_stock": {
                        "item": ItemOutSerializer(item).data,
                    },
                    "amount": amount,
                },
                "price": (
                    item.buyprice
                    if invoice_type
                    in [InvoiceType.purchase, InvoiceType.refund_purchase]
                    else item.sellprice
                ),
            }
            for (item, amount) in zip(items, amounts)
        ]
        res = client.post(
            url,
            {
                "invoice_type": invoice_type,
                "name": uuid4(),
                "stakeholder": self.stakeholder.id,
                "warehouse": self.warehouse.id,
                "items": inventory_items,
            },
            format="json",
        )
        return res

    def test_employee_can_create_invoice_and_it_increases_stocks(self):
        self.amounts = [Decimal(10), Decimal(20)]
        res: Response = self.create_invoice(
            self.employee_client,
            items=[self.item1, self.item2],
            amounts=self.amounts,
        )

        # is invoice created?
        self.assertEqual(res.status_code, 201)

        # is warehouse item stock amount calculated correctly?
        self.assertEqual(self.item1.stocks.first().amount, self.amounts[0])
        self.assertEqual(self.item2.stocks.first().amount, self.amounts[1])

        # create another invoice to see if it increases furthermore,
        # if cache isn't reset by creation of invoice, it would fail.
        self.create_invoice(
            self.employee_client,
            items=[self.item1, self.item2],
            amounts=self.amounts,
        )

        # is warehouse item stock amount updated correctly?
        self.assertEqual(self.item1.stocks.first().amount, self.amounts[0] * 2)
        self.assertEqual(self.item2.stocks.first().amount, self.amounts[1] * 2)
