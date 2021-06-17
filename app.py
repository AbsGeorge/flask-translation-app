from flask import Flask, render_template
from os import getenv
import uuid, json, requests
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url=f"https://{getenv('KEY_VAULT_NAME')}.vault.azure.net/", credential=credential)




app = Flask(__name__)


app.config['SECRET_KEY']= secret_client.get_secret('SECRET-KEY').value
subscription_key = secret_client.get_secret('TRANSLATOR-TEXT-SUBSCRIPTION-KEY').value
endpoint = secret_client.get_secret("TRANSLATOR-TEXT-ENDPOINT").value

langs = requests.get('https://api.cognitive.microsofttranslator.com/languages?api-version=3.0')
langs = langs.json()
languages = []
for lang in langs['translation']:
    languages.append((lang,langs['translation'][lang]['nativeName']))

class TranslateForm(FlaskForm):

    sentence = StringField('Enter Some Text')
    language = SelectField('Language',
        choices=languages)
    submit = SubmitField('Translate')

@app.route('/', methods=['GET', 'POST'])
def translate():
    form = TranslateForm()
    response = ""
    if form.validate_on_submit():
        addition = "translate?api-version=3.0&to="
        headers = {
        'Ocp-Apim-Subscription-Key':subscription_key,
        'Ocp-Apim-Subscription-Region':'westeurope',
        'Content-Type':'application/json'
        }
        body = [{
        'Text': form.sentence.data
        }]
        constructed_url = endpoint + addition + form.language.data
        request = requests.post(constructed_url, headers=headers, json=body)
        response = request.json()
        response = response[0]['translations'][0]['text']
    return render_template('index.html', form=form, translation=response)


if __name__=='__main__':
    app.run(debug=True, host='0.0.0.0') 