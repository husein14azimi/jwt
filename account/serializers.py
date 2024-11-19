# account.serializers

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class CombinedUserPersonSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(source='person.bio', allow_blank=True)
    birth_date = serializers.DateField(source='person.birth_date', allow_null=True)
    gender = serializers.CharField(source='person.gender', allow_null=True)
    updated_at = serializers.DateTimeField(source='person.updated_at', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'date_joined', 'last_login', 'bio', 'birth_date', 'gender', 'updated_at',]
        read_only_fields = ['id', 'username', 'date_joined', 'last_login',]

    def update(self, instance, validated_data):
        person_data = {}
        for field in ['bio', 'birth_date', 'gender']:
            if field in validated_data:
                person_data[field] = validated_data.pop(field)

        super().update(instance, validated_data)

        if person_data:
            person = instance.person
            for attr, value in person_data.items():
                setattr(person, attr, value)
            person.save()

        return instance