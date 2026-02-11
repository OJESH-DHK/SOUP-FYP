from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django_rest_passwordreset.signals import reset_password_token_created

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    # Context for the template
    context = {
        'username': reset_password_token.user.username,
        'reset_password_token': reset_password_token.key,
    }

    # Render HTML and Plain Text versions
    email_html_message = render_to_string('user/password_reset_email.html', context)
    email_plaintext_message = f"Token: {reset_password_token.key}"

    msg = EmailMultiAlternatives(
        # title:
        "Reset your SOUP-FYP Password",
        # message (plain text backup):
        email_plaintext_message,
        # from:
        "SOUP-FYP <ssspppaaammmaaaccc@gmail.com>",
        # to:
        [reset_password_token.user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()