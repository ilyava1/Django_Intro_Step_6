from django.contrib.auth.models import User
from django_filters import DateFromToRangeFilter
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from advertisements.models import Advertisement

MAX_ADV = 10

class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""

    creator = UserSerializer(
        read_only=True,
    )
    created_at = DateFromToRangeFilter()

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'description', 'creator',
                  'status', 'created_at', )
        read_only_fields = ['creator',]

    def create(self, validated_data):
        """Метод для создания"""

        # Простановка значения поля создатель по-умолчанию.
        # Текущий пользователь является создателем объявления
        # изменить или переопределить его через API нельзя.
        # обратите внимание на `context` – он выставляется автоматически
        # через методы ViewSet.
        # само поле при этом объявляется как `read_only=True`

        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)


    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""

        open_adv_quantity = Advertisement.objects.filter(
            creator=self.context["request"].user,
            status='OPEN'
            ).count()

        print(f'!!!!!!!!!!!!! {self.context["view"].action} !!!!!!!!!!!!!!!!!!')

        if (open_adv_quantity >= MAX_ADV and
                self.context["view"].action == 'create'):
            raise ValidationError(f'Допускается не более {MAX_ADV} открытых'
                                  f' объявлений у пользователя. Сейчас '
                                  f'у {self.context["request"].user}'
                                  f' открыто {open_adv_quantity} объявлений.')
        if "status" in data.keys():
            if (self.context["view"].action == 'partial_update' and
                data["status"] == "OPEN"):
                raise ValidationError(f'Вы пытаетесь открыть {open_adv_quantity+1}-ое объявление.')
        return data
