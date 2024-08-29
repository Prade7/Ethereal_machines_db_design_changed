# machines_app/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .models import Machine, DynamicData, User
from django.shortcuts import get_object_or_404

import jwt
from datetime import datetime, timedelta
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import MachineSerializer

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = []
    
    def post(self, request):
        employee_id = request.data.get('employee_id')
        password = request.data.get('password')
        role = request.data.get('role')

        if not employee_id or not password or not role:
            return Response({"error": "Employee ID, password, and role are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(employee_id=employee_id)
            
            if check_password(password, user.password_hash):
                payload = {
                    "employee_id" : f"{employee_id}",
                    "role" : f"{role}"
                }
                token = encode_jwt(payload=payload)
                return Response(token, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Incorrect password."}, status=status.HTTP_403_FORBIDDEN)

        except User.DoesNotExist:
            user = User.objects.create(
                employee_id=employee_id,
                password_hash=make_password(password), 
                role=role
            )

            payload = {
                    "employee_id" : f"{employee_id}",
                    "role" : f"{role}"
                }
            token = encode_jwt(payload=payload)
            return Response(token, status=status.HTTP_201_CREATED)


# @method_decorator(csrf_exempt, name='dispatch')
class Sview(APIView):
    permission_classes = []

    def get(self,request):
        print(request.headers.get('Authorization'))
        token = decode_jwt(request.headers.get('Authorization'))
        print(token)
        if not token:
            return Response({"error": "Authentication token is missing or invalid."}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({"message":f'{token}'}, status=status.HTTP_200_OK)


    

class MachineDetailView(APIView):
    permission_classes = []

    def get(self, request):
        machines = Machine.objects.all()
        serializer = MachineSerializer(machines, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)






from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from .models import Machine, DynamicData, User
from .serializers import MachineSerializer

class MachineListView(APIView):
    permission_classes = []

    def get(self, request):
        token = decode_jwt(request.headers.get('Authorization'))
        employee_id = token.get('employee_id')
        role = token.get("role")
        user = User.objects.get(employee_id=employee_id)
        if not user:
            return Response({"error": "Employee details not found"}, status=status.HTTP_400_BAD_REQUEST)
        
        machines = Machine.objects.all()
        serializer = MachineSerializer(machines, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        token = decode_jwt(request.headers.get('Authorization'))
        employee_id = token.get('employee_id')
        role = token.get("role")
        user = User.objects.get(employee_id=employee_id)
        if not user:
            return Response({"error": "Employee details not found"}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        if not data or 'name' not in data:
            return Response({"error": "Missing machine name in the data."}, status=status.HTTP_400_BAD_REQUEST)

        machine_name = data['name']
        
        if role.lower() == 'operator':
            return Response({"error": "Operators are not allowed to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        
        if role.lower() == 'supervisor':
            machine = Machine.objects.filter(name=machine_name).first()
            if not machine:
                return Response({"error": f"Permission denied for role {role}"}, status=status.HTTP_403_FORBIDDEN)

        # Find machine based on name, acceleration, and velocity
        machine = Machine.objects.filter(name=machine_name, acceleration=data['acceleration'], velocity=data['velocity']).first()
    
        if machine:
            print("machine id ", machine.id)
            # Check if a DynamicData instance already exists with the same attributes
            latest_dynamic_data = DynamicData.objects.filter(
                machine_id=machine.id,
                actual_position=data['actual_position'],
                distance_to_go=data['distance_to_go'],
                homed=data['homed'],
                tool_offset=data['tool_offset']
            ).first()

            if not latest_dynamic_data:
                DynamicData.objects.create(
                    machine_id=machine,
                    user_id=user,
                    actual_position=data['actual_position'],
                    distance_to_go=data['distance_to_go'],
                    homed=data['homed'],
                    tool_offset=data['tool_offset'],
                    created_by=employee_id,
                    timestamp=datetime.now()
                )
                return Response({"message": f"Machine {machine_name} data added."}, status=status.HTTP_201_CREATED)
        else:
            # Create a new machine if not found
            new_machine = Machine.objects.create(
                name=machine_name,
                acceleration=data['acceleration'],
                velocity=data['velocity']
            )

            DynamicData.objects.create(
                machine_id=new_machine,
                user_id=user,
                actual_position=data['actual_position'],
                distance_to_go=data['distance_to_go'],
                homed=data['homed'],
                tool_offset=data['tool_offset'],
                created_by=employee_id,
                timestamp=datetime.now()
            )
            return Response({"message": f"Machine {machine_name} created and data added."}, status=status.HTTP_200_OK)

        return Response({"message": f"Machine {machine_name} updated."}, status=status.HTTP_200_OK)















def encode_jwt(payload, expiration_minutes=30000):
    ALGORITHM = 'HS256'
    SECRET_KEY = "hrtshrthththte"
    expiration = datetime.utcnow() + timedelta(minutes=expiration_minutes)
    payload['exp'] = expiration
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token



def decode_jwt(token):
    SECRET_KEY = "hrtshrthththte"
    ALGORITHM = 'HS256'
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("The token has expired")
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError("The token is invalid")