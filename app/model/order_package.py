from enum import Enum


class OrderPackage(str, Enum):
	FRAGILE = "FRAGILE"
	SOLID = "SOLID"
	LIQUID = "LIQUID"
	FLAMMABLE = "FLAMMABLE"
