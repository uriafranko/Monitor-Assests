import boto3
import os


class Mailer:

    def __init__(self, base_url, source_email, target_email = None):
        aws_access_key_id = os.environ['AWS_KEY']
        aws_secret_access_key = os.environ['AWS_SECRET']
        self.client = boto3.client('ses', aws_access_key_id = aws_access_key_id,
                                   aws_secret_access_key = aws_secret_access_key,
                                   region_name = 'us-east-1')

        self.target_email = source_email
        if target_email is not None:
            self.target_email = target_email
        self.base_url = base_url
        self.source_email = source_email
        self.assets = []

    def send_mail(self):
        subject = "Assets Monitor Asset Failure"
        body = f"""
        <h2>There's a problem with one of your assets!</h2>
        <h4>Base URL: <a href={self.base_url}>{self.base_url}</a></h4>
        """
        for link in self.assets:
            body += f'<a href="{link}"><p>{link}</p></a><br>'
        self.send(subject, body)

    def send_errors(self, errors):
        subject = "Assets Monitor Website Failure"
        body = f"""
        <h3>There's a problem with your monitored website:</h3>
        <h4>{self.base_url}</h4>
        """
        for err in errors:
            body += f"<p>{err}</p><br>"
        self.send(subject, body)

    def send(self, subject, body):
        self.client.send_email(
            Source = self.source_email,
            Destination = {
                'ToAddresses': [
                    self.target_email,
                ],
            },
            Message = {
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Html': {
                        'Data': body,
                        'Charset': 'UTF-8'
                    }
                }
            },
            ReplyToAddresses = [
                self.source_email,
            ],
        )