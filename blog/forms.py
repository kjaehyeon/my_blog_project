from .models import Comment
from django import forms


class CommentForm(forms.ModelForm):
    # content = forms.Textarea()
    # def save(self, commit=True):
    #     comment = Comment()
    #     comment.content = self.cleaned_data['content']
    #     if commit:
    #         comment.save()
    #     return comment
    class Meta:
        model = Comment
        fields = ('content',)
        # 혹은 exclude = ('post','author','created_at','modified_at',) 으로 해도된다.
