import sys

import click
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup

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
@click.option('--model', default="gpt-3.5-turbo",
              help='openai model to use; see https://platform.openai.com/docs/models for options')
@optgroup.group('Request type', cls=RequiredMutuallyExclusiveOptionGroup,
                help='The kind of request to make')
@optgroup.option('--refactor', is_flag=True, default=False, help='Refactor the code')
@optgroup.option('--document', is_flag=True, default=False, help='Documnet the code')
@optgroup.option('--test', is_flag=True, default=False, help='Test the code')
@click.pass_context
def ask(ctx, query, prompt, model, refactor, document, test):
    """
    Ask the AI something either on the command line, or if that's empty then read from stdin.
    """

    if not query:
        # read from stdin
        query = sys.stdin.read()

    api_key = ctx.obj.get('api_key') or get_api_key()

    prompt = PromptFactory.get_prompt(prompt)
    if refactor:
        prompt = prompt.refactoring
    elif document:
        prompt = prompt.documentation
    elif test:
        prompt = prompt.testing

    print(
        Service(
            api_key=api_key,
            prompt=prompt,
            model=model
        ).query(
            message=' '.join(query)
        )
    )

aimain = ai
