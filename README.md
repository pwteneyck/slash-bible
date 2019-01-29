# slash-bible
A Slack slash command that provides Bible utilities.

# Dependencies
## Code Dependencies
Currently only uses `boto3` and `botocore` (included in `boto3`),
and standard Python stuff. `botocore` is the lambda-friendly way
to get `requests`.

## Infrastructure Dependencies

Stores an ESV developer API key (see https://api.esv.org/) in AWS
Secrets Manager. The key is stored as a single string, not as part
of a key-value pair.

# Usage
## Local
Good luck using it locally; you'll probably need to write some code
to mock the API key. Other than that, though, you should be fine!

Input into the lambda takes the form of `event` (a bunch of 
arguments) and `context` (no idea, it's ignored in this code). Event
will usually have a bunch of stuff in it when it's actually called
in AWS, but for testing purposes all it needs is a field called 
`body` that includes a `x-www-form-urlencoded` blob with a `text`
argument...basically, you need something that looks like:

```json
{
  "body": "text=john 3:16"
}
```

The `text` field is what's passed to the lambda from the user input
in Slack. So if a user typed `/bible john 3:16`, Slack would send 
the above text.

## Lambda
The `build.sh` script will package things up into a ZIP file that
you can upload to AWS Lambda. It needs to be aware of dependencies,
so if you add any in code you'll need to update `build.sh` as well.