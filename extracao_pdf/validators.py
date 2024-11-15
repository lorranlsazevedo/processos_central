from django.core.exceptions import ValidationError

def validate_file_extension(value):
    if not value.name.endswith('.docx'):
        raise ValidationError('Apenas arquivos .docx são permitidos.')