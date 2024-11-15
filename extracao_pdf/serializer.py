from rest_framework import serializers
from extracao_pdf.models import Processo, Board, List, Card, Bem


class BemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bem
        fields = ['id', 'descricao']

class ProcessoSerializer(serializers.ModelSerializer):
    bens = BemSerializer(many=True, read_only=True)

    class Meta:
        model = Processo
        fields = ['id', 'numero', 'bens']


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'

class ListSerializer(serializers.ModelSerializer):
    cards = CardSerializer(many=True, read_only=True)
    class Meta:
        model = List
        fields = '__all__'

class BoardSerializer(serializers.ModelSerializer):
    lists = ListSerializer(many=True, read_only=True)
    class Meta:
        model = Board
        fields = '__all__'