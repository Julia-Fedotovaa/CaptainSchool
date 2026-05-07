class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            if field.widget.__class__.__name__ != "CheckboxInput":
                field.widget.attrs["class"] = "form-control"
