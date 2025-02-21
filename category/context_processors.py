from .models import Category

def menu_links(request):
    links= Category.objects.all()
    return dict(links=links)

#context processor is python  function which accepts request argument and returns dict. need to mentioned this processor in settings.py
