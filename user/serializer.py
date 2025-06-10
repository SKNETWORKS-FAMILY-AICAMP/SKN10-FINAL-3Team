# user/serializer.py
from rest_framework.serializers import ModelSerializer
from .models import CustomUser

# 사용자 직렬화 클래스: 사용자 데이터를 JSON으로 변환하거나 역변환
class UserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser  # 사용할 모델 지정
        fields = ['name', 'email', 'phone', 'password', 'bio', 'exp_career', 'exp_activity', 'education_high', 'education_univ', 'education_grad']  # JSON으로 표현할 필드 목록
        extra_kwargs = {
            'bio': {'required': False, 'allow_null': True},
            'exp_career': {'required': False, 'allow_null': True},
            'exp_activity': {'required': False, 'allow_null': True},
            'education_high': {'required': False, 'allow_null': True},
            'education_univ': {'required': False, 'allow_null': True},
            'education_grad': {'required': False, 'allow_null': True},
            'password': {'write_only': True}  # 비밀번호는 쓰기 전용 필드로 설정하여 응답에 포함되지 않도록 함
        }

    # 사용자 생성 시 호출되는 메서드
    # 비밀번호를 평문 그대로 저장하지 않고, set_password로 해싱하여 저장
    def create(self, validated_data):
        print("[UserSerializer][create] Start")
        
        password = validated_data.pop('password', None)  # 입력 받은 데이터에서 비밀번호 추출
        instance = self.Meta.model(**validated_data)  # 나머지 데이터를 기반으로 사용자 인스턴스 생성
        
        if password is not None:
            instance.set_password(password)  # Django 제공 해싱 함수로 비밀번호 암호화
        instance.save()  # 데이터베이스에 저장
        return instance

# 회원가입 흐름에서 사용:
# - 클라이언트로부터 전달받은 사용자 데이터를 유효성 검증 및 직렬화
# - 서버 측에서는 이 직렬화 클래스의 create 메서드를 통해 안전하게 사용자 생성