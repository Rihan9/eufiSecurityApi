import click, logging, asyncio
from .api import Api

_logger = logging.getLogger(__name__)
logging.basicConfig(format='%(name)-10s %(levelname)-8s %(message)s')

uefyApi = None


class MyContext(click.Context):
    def __init__(self):
        self.uefyApi = None

@click.group(chain=True)
@click.pass_context
@click.option('--debug/--no-debug', prompt='activate debug', default=False)
def cli(ctx, debug):
    _logger.debug('cli: %s, %s' %(type(ctx), ctx))
    if(ctx.obj is None):
        ctx.obj = MyContext()
    _logger.parent.setLevel(logging.DEBUG if debug else logging.INFO)
    _logger.setLevel(logging.DEBUG if debug else logging.INFO)

@cli.command()
@click.pass_context
@click.option('--username', prompt='eufy security username', default=None)
@click.option('--password', prompt='eufy security password', default=None)
@click.option('--tfa', prompt='preferred two factor authentication method (EMAIL, SMS, PUSH)', default='EMAIL')
def login(ctx, username, password, tfa):
    _logger.debug('Username: %s, Password: %s, tfa: %s' % (username, password, tfa))
    ctx.parent.obj.uefyApi = Api(username=username, password=password)
    try:
        asyncio.run(ctx.parent.obj.uefyApi.authenticate())
    except:
        pass
    pass

@cli.command()
@click.pass_context
@click.option('--token', prompt='eufy token', default=None, required=False)
@click.option('--token_expire_at', prompt='eufy token expiratio timestamp', default=None, required=False)
@click.option('--domain', prompt='eufy domain', default=None, required=False)
def session(ctx, token, domain, token_expire_at):
    ctx.parent.obj.uefyApi = Api(token=token, domain=domain, token_expire_at=int(token_expire_at))

@cli.command()
@click.pass_context
def devices(ctx):
    try:
        asyncio.run(ctx.parent.obj.uefyApi.get_devices())
        _logger.info(ctx.parent.obj.uefyApi.devices)
    except:
        pass
    pass
if __name__ == '__main__':
    #pylint: disable=no-value-for-parameter
    cli()