import sys

import click

from .key import get_api_key
from .prompt import get_calling_shell, prompt_choices
from ..service import Service
from ..factories import PromptFactory


@click.group()
@click.option("--api-key", nargs=1, required=False, help="openai API key")
@click.pass_context
def ai(ctx, api_key):
    ctx.ensure_object(dict)
    ctx.obj['api_key'] = api_key


PROMPT_CHOICE = click.Choice(prompt_choices(), case_sensitive=False)
PROMPT_DEFAULT = get_calling_shell()


@ai.command()
@click.argument("query", nargs=-1)
@click.option('--prompt', default=PROMPT_DEFAULT, type=PROMPT_CHOICE, help='The prompt to use')
@click.option('--model', default="gpt-3.5-turbo", help='openai model to use')
@click.pass_context
def ask(ctx, query, prompt, model):
    """
    Ask the AI something either on the command line, or if that's empty then read from stdin.
    """

    if not query:
        # read from stdin
        query = sys.stdin.read()

    api_key = ctx.obj.get('api_key') or get_api_key()

    print(
        Service(
            api_key=api_key,
            prompt=PromptFactory.get_prompt(prompt),
            model=model
        ).query(
            message=' '.join(query)
        )
    )

aimain = ai
