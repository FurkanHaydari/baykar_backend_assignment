from rest_framework import serializers
from production.models import Part, UAV

class PartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Part
        fields = ['id', 'type', 'uav_type', 'serial_number', 'produced_by', 'production_date', 'is_used']
        read_only_fields = ['produced_by', 'production_date', 'is_used']

class UAVSerializer(serializers.ModelSerializer):
    class Meta:
        model = UAV
        fields = ['id', 'type', 'serial_number', 'wing', 'body', 'tail', 'avionics', 'assembled_by', 'assembly_date']
        read_only_fields = ['assembled_by', 'assembly_date']
