class Field:
    def __init__(self, name):
        self.name = name
        self.internal_name = '_' + self.name

    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return getattr(instance, self.internal_name, '')

    def __set__(self, instance, value):
        setattr(instance, self.internal_name, value)



class Exercise:
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, instance_type):
        return "getter"

    def __set__(self, instance, value):
        print("Do setter")
        self.value = value

class Celsius:
    def __get__(self, instance, owner):
        return 5 * (instance.fahrenheit - 32) / 9

    def __set__(self, instance, value):
        instance.fahrenheit = 32 + 9 * value / 5

class Temperature:
    celius = Celsius()

    def __init__(self, initial_f):
        self.fahrenheit = initial_f


class Meta(type):
    def __new__(meta, name, bases, class_dict):
        for key, value in class_dict.items():
            if isinstance(value, Field):
                value.name = key
                value.internal_name = '_' + key
        cls = type.__new__(meta, name, bases, class_dict)
        return cls