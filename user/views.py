# from django.shortcuts import render

# from rest_framework.views import APIView
# from rest_framework.response import Response

# from authentication.exceptions import EmailValidator, PasswordValidator, PhoneNumberValidator

# # 회원가입 뷰
# class RegisterView(APIView):
#     def post(self, request):
#         data = request.data

#         email = data.get("email")
#         password = data.get("password")
#         phone = data.get("phone")

#         # 유효성 검사 수행
#         EmailValidator()(email)
#         PasswordValidator()(password)
#         PhoneNumberValidator()(phone)

#         # 여기서 사용자 생성 로직 (예: User.objects.create_user 등)을 수행하면 됨
#         return Response({"message": "회원가입 성공"})

