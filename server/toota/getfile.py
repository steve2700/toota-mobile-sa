#!/usr/bin/python3
from authentication.models import User, Driver

driver = Driver.objects.all().first()
print(driver)