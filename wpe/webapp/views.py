from django.shortcuts import render

# Create your views here.
from .forms import MainForm
from .models import EmailSignupModel


def index(request):
    if request.method == 'POST':
        form = MainForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            location = form.cleaned_data['location']
            print(email, location)
            model = EmailSignupModel(email=email, location=location)
            if not EmailSignupModel.objects.filter(email=email):
                model.save()

    else:
        form = MainForm()
    print(EmailSignupModel.objects.all())
    return render(request, 'base.html', {'form': form})
