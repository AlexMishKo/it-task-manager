from django import forms
from manager.models import Task, Worker


class TaskForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = "__all__"
        widgets = {
            "name": forms.TextInput(attrs={
                "class":
                    "input input-bordered w-full "
                    "font-bold italic uppercase text-secondary",
                "placeholder": "Operation name..."
            }),
            "description": forms.Textarea(attrs={
                "class": "textarea textarea-bordered w-full italic",
                "rows": 3
            }),
            "deadline": forms.DateInput(attrs={
                "class": "input input-bordered w-full",
                "type": "date"
            }),
            "priority": forms.Select(attrs={
                "class": "select select-bordered w-full font-black uppercase"
            }),
            "task_type": forms.Select(attrs={
                "class": "select select-bordered w-full"
            }),
            "project": forms.Select(attrs={
                "class": "select select-bordered w-full"}),
            "team": forms.Select(attrs={
                "class": "select select-bordered w-full"
            }),
            "assignees": forms.CheckboxSelectMultiple(attrs={
                "class": "flex flex-wrap gap-4"
            }),
            "tags": forms.CheckboxSelectMultiple(attrs={
                "class": "flex flex-wrap gap-2"
            }),
            "is_completed": forms.CheckboxInput(attrs={
                "class": "checkbox checkbox-primary"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assignees"].queryset = Worker.objects.select_related("position")
