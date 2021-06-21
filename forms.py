from django.contrib.auth.forms import UserCreationForm
from .models import User, Post
from django import forms
from django.contrib.auth import authenticate

class UserCreateForm(UserCreationForm):
    class Meta:
        model=User
        fields=('name', 'phone','email', 'password1', 'password2')
    def __init__(self, *args, **kwargs):
        super(UserCreateForm, self).__init__(*args, **kwargs)
        for field in (self.fields['email'],self.fields['password1'],self.fields['phone'],self.fields['password2'],self.fields['name']):
            field.widget.attrs.update({'class': 'form-control ' })

class AccountAuthenticationForm(forms.ModelForm):
    password  = forms.CharField(label= 'Password', widget=forms.PasswordInput)
    
    class Meta:
        model  =  User
        fields =  ('phone', 'password')
        widgets = {
                   'phone':forms.TextInput(attrs={'class':'form-control'}),
                   'password':forms.TextInput(attrs={'class':'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super(AccountAuthenticationForm, self).__init__(*args, **kwargs)
        for field in (self.fields['phone'],self.fields['password']):
            field.widget.attrs.update({'class': 'form-control '})

    def clean(self):
        if self.is_valid():

            phone = self.cleaned_data.get('phone')
            password = self.cleaned_data.get('password')
            if not authenticate(phone=phone, password=password):
                raise forms.ValidationError('Invalid Login')


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields= ("title", "image", "content")
    


    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        for field in (self.fields['title'],self.fields['content'],self.fields['image']):
            field.widget.attrs.update({'class': 'form-control '})
        self.fields['image'].widget.attrs.update({'class': 'form-control-file'})


class SearchForm(forms.Form):
    query = forms.CharField()


class UpdatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'image','content']
    def save(self, commit=False):
        blog_post = self.instance
        blog_post.title = self.cleaned_data['title']
        blog_post.content  = self.cleaned_data['content']
        # blog_post.status = self.cleaned_data['status']

        if self.cleaned_data['image']:
            blog_post.image = self.cleaned_data['image']
        if commit:
            blog_post.save()
        return blog_post

    def __init__(self, *args, **kwargs):
        super(UpdatePostForm, self).__init__(*args, **kwargs)
        for field in (self.fields['title'],self.fields['content']):
            field.widget.attrs.update({'class': 'form-control '})
        self.fields['image'].widget.attrs.update({'class': 'form-control-file'})