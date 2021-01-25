import click, logging, asyncio
from .api import Api

_logger = logging.getLogger(__name__)
logging.basicConfig(format='%(name)-10s %(levelname)-8s %(message)s')

uefyApi = None


class MyContext(object):
    def __init__(self):
        self.uefyApi = None

@click.group(chain=True)
@click.pass_context
@click.option('--debug/--no-debug', prompt='activate debug', default=False)
def cli(ctx, debug):
    ctx.obj = MyContext()
    _logger.parent.setLevel(logging.DEBUG if debug else logging.INFO)
    _logger.setLevel(logging.DEBUG if debug else logging.INFO)

@cli.command()
@click.pass_context
@click.option('--username', prompt='eufy security username')
@click.option('--password', prompt='eufy security password')
@click.option('--tfa', prompt='preferred two factor authentication method (EMAIL, SMS, PUSH)', default='EMAIL')
def login(ctx, username, password, tfa):
    _logger.debug('Username: %s, Password: %s, tfa: %s' % (username, password, tfa))
    ctx.uefyApi = Api(username, password)
    try:
        asyncio.run(ctx.uefyApi.authenticate())
        #asyncio.run(ctx.uefyApi.get_devices())
        _logger.info(ctx.uefyApi.devices)
    except:
        pass
    pass

@cli.command()
@click.pass_context
def devices(ctx):
    pass

if __name__ == '__main__':
    #pylint: disable=no-value-for-parameter
    cli()