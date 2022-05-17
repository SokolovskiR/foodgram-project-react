# from rest_framework.serializers import ValidationError


# class ValidTags:
#     def __init__(self, base):
#         self.base = base

#     def __call__(self, value):
#         if value % self.base != 0:
#             message = 'This field must be a multiple of %d.' % self.base
#             raise ValidationError(message)