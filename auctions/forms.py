from django import forms
from .models import AuctionList, Comments


class CreateForm(forms.ModelForm):
	class Meta:
		model = AuctionList
		fields = ['title', 'image_url', 'description', 'price', 'category']
		widgets = {
		'title': forms.TextInput(),
		'image_url': forms.TextInput(),
		'description': forms.Textarea(attrs={'cols': 80, 'rows': 8})
		}

