from uuid import uuid4

from django.contrib.auth.models import AnonymousUser, Group, Permission
from django.test import TestCase
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.test import APIClient

from inventory.models import StockUnit
from users.models import User


def create_employee_group() -> Group:
    employee_group = Group.objects.create(name="employee_group")
    permissions = Permission.objects.filter(
        codename__in=[
            "add_item",
            "change_item",
            "delete_item",
            "view_item",
            #
            "add_stockunit",
            "change_stockunit",
            "delete_stockunit",
            "view_stockunit",
        ]
    )
    employee_group.permissions.set(permissions)
    employee_group.save()
    return employee_group


class TestInventory(TestCase):
    def set_up_employee_client(self):
        self.employee_group = create_employee_group()
        self.user: User = User.objects.create_user(
            username="employee1", password="password"
        )
        self.user.groups.add(self.employee_group)
        self.user.save()
        self.nonemployee_user: User = User.objects.create_user(
            username="notemployee1", password="password"
        )
        self.employee_client = APIClient()
        self.employee_client.login(username="employee1", password="password")
        self.nonemployee_client = APIClient()
        self.nonemployee_client.login(username="notemployee1", password="password")
        self.anon_client: APIClient = APIClient()
        self.anon_client.force_authenticate(user=AnonymousUser())

    def setUp(self) -> None:
        self.set_up_employee_client()
        self.stock_unit = StockUnit.objects.create()

    def test_stock_unit_create_by_employee(self):
        url = reverse("stockunit-list")
        res: Response = self.employee_client.post(url, {"name": "kg"}, format="json")
        self.assertEquals(res.status_code, 201)

    def create_item(self, client: APIClient):
        url = reverse("item-list")
        res: Response = client.post(
            url,
            {
                "name": uuid4(),
                "stock_unit": self.stock_unit.id,
                "buyprice": 10,
                "sellprice": 12,
                "kdv": 18,
            },
            format="json",
        )
        return res

    def test_item_create_by_employee(self):
        res = self.create_item(self.employee_client)
        self.assertEquals(res.status_code, 201)

    def test_item_not_created_by_anon(self):
        res = self.create_item(self.anon_client)
        self.assertEquals(res.status_code, 403)

    def test_item_not_created_by_non_employee_user(self):
        res = self.create_item(self.nonemployee_client)
        self.assertEqual(res.status_code, 403)
