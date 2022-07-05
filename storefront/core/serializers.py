from djoser.serializers import UserCreateSerializer as BaseUserSerializer, UserSerializer

class UserCreateSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['id','first_name','last_name','username','email','password']

class CurrentUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ['id','first_name','last_name','username','email']
