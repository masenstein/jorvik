def valida_dimensione_file_2mb(fieldfile_obj):
    from django.core.exceptions import ValidationError
    filesize = fieldfile_obj.size
    megabyte_limit = 2
    if filesize > megabyte_limit*1024*1024:
        raise ValidationError("Seleziona un file più piccolo di %sMB" % str(megabyte_limit))