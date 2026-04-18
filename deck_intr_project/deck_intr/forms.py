from django import forms
from .models import Category, Deck

class DeckForm(forms.ModelForm):
    class Meta:
        model = Deck
        fields = ['title', 'text', 'thumbnail', 'video', 'categories']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'video': forms.FileInput(attrs={'class': 'form-control', 'accept': 'video/*'}),
            'categories': forms.CheckboxSelectMultiple(),
        }

class DeckSearchForm(forms.Form):
    keyword = forms.CharField(
        required=False,
        label='キーワード',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'デッキ名や説明文で検索'
        })
    )
    
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label='カテゴリー',
        widget=forms.CheckboxSelectMultiple()
    )
    
    username = forms.CharField(
        required=False,
        label='投稿者',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ユーザー名で検索'
        })
    )
    
    ORDER_CHOICES = [
        ('-created_at', '新しい順'),
        ('created_at', '古い順'),
        ('title', 'タイトル順（昇順）'),
        ('-title', 'タイトル順（降順）'),
        ('-likes_count', 'いいねが多い順'),
    ]
    
    order = forms.ChoiceField(
        choices=ORDER_CHOICES,
        required=False,
        initial='-created_at',
        label='並び順',
        widget=forms.Select(attrs={'class': 'form-select'})
    )