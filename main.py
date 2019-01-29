import argparse
import boto3
import json
from botocore.vendored import requests
from urllib.parse import parse_qs

ESV_TOKEN = boto3.session.Session().client(
    service_name='secretsmanager',
    region_name='us-east-1').get_secret_value(
    SecretId='esv-api-key')['SecretString']
HEADERS = {'Authorization': f'Token {ESV_TOKEN}'}


def lambda_handler(event, context):
    args = parse_args(event)

    if args[0] == 'help':
        return help_response()

    parser = argparse.ArgumentParser()
    # These are currently included in the pretty-print functionality
    # parser.add_argument('--include-verse-numbers', '-v', action='store_true')
    # parser.add_argument('--include-headings', '-H', action='store_true')
    parser.add_argument('--include-footnotes', '-f', action='store_true')
    parser.add_argument('--pretty-print', '-p', action='store_true')

    try:
        options = parser.parse_args(args[1])
    except:
        return help_response()

    if args[0].startswith('search'):
        split = args[0].find(' ')
        return search(args[0][split:])
    else:
        return passage_lookup(args[0], options)


def parse_args(event):
    body = parse_qs(event["body"])
    if "text" not in body:
        return ('help')

    text = body["text"][0]

    ARG_SPLITTER = ';'

    if ARG_SPLITTER not in text:
        return text, []

    split_point = text.find(ARG_SPLITTER)
    search_text = text[0:split_point].strip()
    args = text[split_point + 1:].strip()
    return search_text, args.split(' ')


def wrap_in_public_response(text):
    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "response_type": "in_channel",
            "text": text
        })
    }


def search(query):
    MAX_RESULTS_PER_PAGE = 10

    resp = requests.get(
        f"https://api.esv.org/v3/passage/search/?q={query}"
        f"&page-size={MAX_RESULTS_PER_PAGE}",
        headers=HEADERS).json()

    total_pages = resp['total_pages']
    current_page = resp['page']

    fields = map(lambda result: {
        'title': result['reference'],
        'value': result['content']}, resp['results'])

    response_body_json = {
        "response_type": "ephemeral",
        "text": '',
        "attachments": [
            {
                "fields": list(fields)
            }
        ]
    }

    if total_pages > 1:
        response_body_json['attachments'][0]['footer'] = f'Page {current_page} out of {total_pages}'

    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(response_body_json)
    }


def passage_lookup(query, options):
    resp = requests.get(f"https://api.esv.org/v3/passage/text/?q={query}"
                        f"&include-passage-references={options.pretty_print}"
                        f"&include-footnotes={options.include_footnotes}"
                        f"&include-verse-numbers={options.pretty_print}"
                        f"&include-headings={options.pretty_print}"
                        f"&include-passage-horizontal-lines={options.pretty_print}"
                        f"&include-heading-horizontal-lines={options.pretty_print}", headers=HEADERS)

    passage = resp.json()['passages'][0]
    return wrap_in_public_response(passage)


def help_response():
    help_text = """
*NAME*
    bible -- turn verse references into text (ESV)

*SYNOPSIS*
```
    /bible [command] ; [options]
```

*COMMANDS*
    *reference*
        The passage to return text for. There's some leeway here as far as 
        formatting goes - the following will all work:

          * `/bible John 3:16`
          * `/bible john 3:16`
          * `/bible john 3 16`
          * `/bible john 3`
          * `/bible john 3 16-17`
          * `/bible john 3 16 - 17`

        OPTIONS
            *--pretty-print, -p*
                Applies extra formatting, including section headers and verse 
                numbers.

                `/bible john 3 16 ; --pretty-print`

            *--include-footnotes, -f*
                Adds any ESV footnotes about the passage to the bottom of the 
                text.

                `/bible john 3 16 ; --include-footnotes`

    *search [search term]*
        Provides verse results for a word or phrase search of the ESV text.
        Currently will only display the first 10 results. Search results are
        returned to the caller as _private replies_.

        Everything after 'search' will be treated as a search query:

        `/bible search rabble` 

        will return verses that include the word 'rabble.'
    """
    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "response_type": "ephemeral",
            "text": help_text,
            "attachments": [{
                "footer": "contact: pwteneyck@gmail.com"
            }]
        })
    }
