# machines_app/serializers.py
from rest_framework import serializers
from .models import Machine, DynamicData




from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['employee_id'] = user.employee_id
        token['role'] = user.role

        return token






from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['employee_id'] = user.employee_id
        token['role'] = user.role

        return token

class DynamicDataSerializer(serializers.ModelSerializer):
    actual_position = serializers.JSONField()
    distance_to_go = serializers.JSONField()
    homed = serializers.JSONField()
    tool_offset = serializers.JSONField()

    class Meta:
        model = DynamicData
        fields = [
            'id', 'machine_id', 'user_id', 'actual_position', 'distance_to_go',
            'homed', 'tool_offset', 'created_by', 'timestamp'
        ]

class MachineSerializer(serializers.ModelSerializer):
    dynamic_data = DynamicDataSerializer(many=True, read_only=True)

    class Meta:
        model = Machine
        fields = ['id', 'name', 'acceleration', 'velocity', 'dynamic_data']