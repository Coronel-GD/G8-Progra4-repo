from django import forms

# === Refund form (para request_refund.html si lo usás) ===
class RefundForm(forms.Form):
    ref_code = forms.CharField(label="Código de referencia")
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label="Mensaje"
    )
    email = forms.EmailField(label="Correo electrónico")
