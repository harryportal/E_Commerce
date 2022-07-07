from django.core.exceptions import ValidationError

def validate_file_size(file):
    max_size = 50
    if file.size > max_size * 1024:
        raise ValidationError(f'File cannot be greater than {max_size}kb')